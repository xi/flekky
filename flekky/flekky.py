#!/use/bin/env python
# -*- coding: utf-8 -*-
"""Static website generator inspired by jekyll based on flask."""

# Based on the tutorial on https://nicolas.perriault.net/code/2012/dead-easy-\
# yet-powerful-static-website-generator-with-flask/.

import os
import argparse
from datetime import date, datetime

from flask import Flask, Blueprint, render_template, abort
from flask import current_app, url_for
from flask import Markup, escape
from flask_flatpages import FlatPages
from flask_frozen import Freezer

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

# http://pythonhosted.org/Markdown/extensions/#officially-supported-extensions
FLATPAGES_MARKDOWN_EXTENSIONS = [
    'codehilite',
    'headerid',
    'fenced_code',
    'footnotes',
    'tables',
    'abbr',
    'wikilinks',
    'toc',
]

flekky = Blueprint('flekky', __name__)

_ = lambda s: s


class FlekkyPages(FlatPages):
    """Flat Pages with some extra features for Jekyll compatibility."""

    def _is_included(self, page):
        if not page:
            return False

        include_unpublished = self.app.config.get('FLEKKY_UNPUBLISHED', False)
        if not include_unpublished and not page.meta.get('published', True):
            return False

        include_future = self.app.config.get('FLEKKY_FUTURE', False)
        is_future = 'date' in page.meta and page.meta['date'] > date.today()
        if not include_future and is_future:
            return False

        return True

    def get(self, path, default=None):
        page = super(FlekkyPages, self).get(path)

        if self._is_included(page):
            return page
        else:
            return default

    def __iter__(self):
        for page in super(FlekkyPages, self).__iter__():
            if self._is_included(page) and page.path != 'index':
                yield page

    def by_tag(self, tag):
        """Get all pages tagged with `tag`."""
        return (p for p in self if tag in p.meta.get('tags', []))

    def by_category(self, category):
        """Get all pages filed under `category`."""
        return (p for p in self if category == p.meta.get('category'))

    def tags(self):
        """Get a set of all tags."""
        tags = set()
        for page in self:
            tags.update(set(page.meta.get('tags', [])))
        return tags

    def categories(self):
        """Get a set of all categories."""
        return set([p.meta['category'] for p in self if 'category' in p.meta])


pages = FlekkyPages()


# filters
@flekky.app_template_filter('datetime')
def filter_datetime(dt, format="%c"):
    """Convert datetime object to HTML5 markup representing full datetime."""
    return Markup('<time datetime="%s">%s</time>' % (dt, dt.strftime(format)))


@flekky.app_template_filter('date')
def filter_date(dt, format="%x"):
    """Convert datetime object to HTML5 markup representing date only."""
    return Markup('<time datetime="%s">%s</time>' % (dt.date(),
                                                     dt.strftime(format)))


@flekky.app_template_filter('time')
def filter_time(dt, format="%X"):
    """Convert datetime object to HTML5 markup representing time only."""
    return Markup('<time datetime="%s">%s</time>' % (dt.time(),
                                                     dt.strftime(format)))


@flekky.app_template_filter('link_page')
def filter_link_page(page):
    """Convert page object to an HTML link to that page."""
    href = url_for('flekky.page', path=page.path)
    text = page.meta['title']
    return Markup('<a href="%s">%s</a>' % (href, escape(text)))


@flekky.app_template_filter('link_tag')
def filter_link_tag(tag):
    """Convert tag name to an HTML link to that tag."""
    href = url_for('flekky.tag', tag=tag)
    return Markup('<a href="%s">%s</a>' % (href, escape(tag)))


@flekky.app_template_filter('link_category')
def filter_link_category(category):
    """Convert category name to an HTML link to that category."""
    href = url_for('flekky.category', category=category)
    return Markup('<a href="%s">%s</a>' % (href, escape(category)))


def _site(pages):
    """Construct site wide variables.

    ... as opposed to page specific variables.
    """
    site = {
        'title': 'Flekky',
        'time': datetime.now(),
        'pages': pages,
        'categories': pages.categories(),
        'tags': pages.tags(),
        'config': current_app.config,
    }

    index = pages.get('index')
    if hasattr(index, 'meta'):
        site.update(index.meta)

    return site


@flekky.route('/tag/<string:tag>/')
def tag(tag):
    if not tag in pages.tags():
        abort(404)
    return render_template('tag.html', pages=pages.by_tag(tag), tag=tag,
                           site=_site(pages))


@flekky.route('/category/<string:category>/')
def category(category):
    if not category in pages.categories():
        abort(404)
    return render_template('category.html', pages=pages.by_category(category),
                           category=category, site=_site(pages))


@flekky.route('/', defaults={'path': 'index'})
@flekky.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    template = 'layout/%s.html' % page.meta.get('layout', 'default')
    return render_template(template, page=page, site=_site(pages))


def create_app(source, settings=None):
    """App factory.

    Args:
        source (str): source directory
        settings (dict): will be loaded after all other configuration is done
    """
    app = Flask(__name__,
                template_folder=os.path.join(source, 'templates'),
                static_folder=os.path.join(source, 'static'))

    app.config.from_object(__name__)
    app.config['FLATPAGES_ROOT'] = os.path.join(source, 'pages')
    app.config.from_object(settings)

    app.register_blueprint(flekky)
    pages.init_app(app)

    return app


def create_freezer(*args, **kwargs):
    """Freezer factory.

    Any arguments will be forwarded to the underlying app factory.
    """
    freezer = Freezer(create_app(*args, **kwargs))
    urls = lambda: (('.page', {'path': page.path}) for page in pages)
    freezer.register_generator(urls)
    return freezer


def parse_args(argv=None):
    """Parse command line arguments.

    Args:
        argv (list): List of command line parameters.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', '-s', default='_source',
                        help=_('directory where Flekky will read files '
                        '(default: _source)'))
    parser.add_argument('--future', action='store_true', dest='FLEKKY_FUTURE',
                        help=_('include pages with dates in the future '
                        '(default: false)'))
    parser.add_argument('--unpublished', action='store_true',
                        dest='FLEKKY_UNPUBLISHED', help=_('include '
                        'unpublished pages (default: false)'))
    subparsers = parser.add_subparsers(title=_('commands'))

    parser_build = subparsers.add_parser('build', help=_('generate static '
                                         'sites'))
    parser_build.add_argument('--destination', '-d', default='_deploy',
                              metavar='DEST', dest='FREEZER_DESTINATION',
                              help=_('directory where Flekky will write files '
                              '(default: _deploy)'))
    parser_build.set_defaults(cmd='build')

    parser_serve = subparsers.add_parser('serve', help=_('run a test server '
                                         'for development'))
    parser_serve.add_argument('--port', '-p', type=int, default=8000)
    parser_serve.set_defaults(cmd='serve')

    return parser.parse_args(argv)


if __name__ == '__main__':  # pragma: no cover
    args = parse_args()

    if args.cmd == 'build':
        freezer = create_freezer(args.source, args)
        freezer.freeze()
    elif args.cmd == 'serve':
        app = create_app(args.source, args)
        app.run(port=args.port)
    else:
        raise ValueError('invalid command: %s' % args.cmd)

# vim: set ts=4 sw=4 sts=4 et:
