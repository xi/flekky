#!/use/bin/env python
# -*- coding: utf-8 -*-
"""Static website generator inspired by jekyll based on flask.

Based on the tutorial on https://nicolas.perriault.net/code/2012/dead-easy-\
yet-powerful-static-website-generator-with-flask/.

"""

import os
import argparse
from datetime import date, datetime

from flask import Flask, Blueprint, render_template
from flask import current_app, url_for
from flask import Markup, escape
from flask_flatpages import FlatPages
from flask_frozen import Freezer

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

# http://pythonhosted.org//Markdown/extensions/#officially-supported-extensions
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

flaky = Blueprint('flaky', __name__)

_ = lambda s: s


class FlakyPages(FlatPages):
    """Flat Pages with some extra features for Jekyll compatibility."""

    def _is_included(self, page):
        if not page:
            return False

        include_unpublished = current_app.config.get('FLAKY_UNPUBLISHED',
                                                     False)
        if not include_unpublished and not page.meta.get('published', True):
            return False

        include_future = current_app.config.get('FLAKY_FUTURE', False)
        is_future = 'date' in page.meta and page.meta['date'] > date.today()
        if not include_future and is_future:
            return False

        return True

    def get(self, path, default=None):
        page = super(FlakyPages, self).get(path)

        if self._is_included(page):
            return page
        else:
            return default

    def __iter__(self):
        for page in super(FlakyPages, self).__iter__():
            if self._is_included(page):
                yield page


pages = FlakyPages()


# filters
@flaky.app_template_filter('datetime')
def filter_datetime(dt, format="%c"):
    return Markup('<time datetime="%s">%s</time>' % (dt, dt.strftime(format)))


@flaky.app_template_filter('date')
def filter_date(dt, format="%x"):
    return Markup('<time datetime="%s">%s</time>' % (dt.date(),
                                                     dt.strftime(format)))


@flaky.app_template_filter('time')
def filter_time(dt, format="%X"):
    return Markup('<time datetime="%s">%s</time>' % (dt.time(),
                                                     dt.strftime(format)))


@flaky.app_template_filter('link_page')
def filter_link_page(page):
    href = url_for('.page', path=page.path)
    text = page.meta['title']
    return Markup('<a href="%s">%s</a>' % (href, escape(text)))


@flaky.app_template_filter('link_tag')
def filter_link_tag(tag):
    href = url_for('.tag', tag=tag)
    return Markup('<a href="%s">%s</a>' % (href, escape(tag)))


@flaky.app_template_filter('link_category')
def filter_link_category(category):
    href = url_for('.category', category=category)
    return Markup('<a href="%s">%s</a>' % (href, escape(category)))


def _site(pages):
    return {
        'time': datetime.now(),
        'pages': pages,
        'categories': set().union(*[set([p.meta['category']]) for p in pages
                                    if 'category' in p.meta]),
        'tags': set().union(*[set(p.meta.get('tags', [])) for p in pages]),
        'config': current_app.config,
    }


@flaky.route('/')
def index():
    return render_template('index.html', site=_site(pages))


@flaky.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag,
                           site=_site(pages))


@flaky.route('/category/<string:category>/')
def category(category):
    categorized = [p for p in pages if category == p.meta.get('category')]
    return render_template('category.html', pages=categorized,
                           category=category, site=_site(pages))


@flaky.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    template = 'layout/%s.html' % page.meta.get('layout', 'page')
    return render_template(template, page=page, site=_site(pages))


def create_app(source, settings=None):
    app = Flask(__name__,
                template_folder=os.path.join(source, 'templates'),
                static_folder=os.path.join(source, 'static'))

    app.config.from_object(__name__)
    app.config['FLATPAGES_ROOT'] = os.path.join(source, 'pages')
    app.config.from_object(settings)

    app.register_blueprint(flaky)
    pages.init_app(app)

    return app


def create_freezer(*args, **kwargs):
    return Freezer(create_app(*args, **kwargs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', '-s', default='_source',
                        help=_('directory where flaky will read files '
                        '(default: _source)'))
    parser.add_argument('--future', action='store_true', dest='FLAKY_FUTURE',
                        help=_('include pages with dates in the future '
                        '(default: false)'))
    parser.add_argument('--unpublished', action='store_true',
                        dest='FLAKY_UNPUBCLISHED', help=_('include '
                        'unpublished pages (default: false)'))
    subparsers = parser.add_subparsers(title=_('commands'))

    parser_build = subparsers.add_parser('build', help=_('generate static '
                                         'sites'))
    parser_build.add_argument('--destination', '-d', default='_deploy',
                              metavar='DEST', dest='FREEZER_DESTINATION',
                              help=_('directory where flaky will write files '
                              '(default: _deploy)'))
    parser_build.set_defaults(cmd='build')

    parser_serve = subparsers.add_parser('serve', help=_('run a test server '
                                         'for development'))
    parser_serve.add_argument('--port', '-p', type=int, default=8000)
    parser_serve.set_defaults(cmd='serve')

    args = parser.parse_args()

    if args.cmd == 'build':
        freezer = create_freezer(args.source, args)
        freezer.freeze()
    elif args.cmd == 'serve':
        app = create_app(args.source, args)
        app.run(port=args.port)
    else:
        raise ValueError('invalid command: %s' % args.cmd)

# vim: set ts=4 sw=4 sts=4 et:
