#!/use/bin/env python
# -*- coding: utf-8 -*-
"""Static website generator inspired by jekyll based on flask."""

# Based on the tutorial on https://nicolas.perriault.net/code/2012/dead-easy-\
# yet-powerful-static-website-generator-with-flask/.

import os
import argparse
import shutil
import locale
from datetime import date, datetime
from pkg_resources import resource_filename

from bs4 import BeautifulSoup

from flask import Flask, Blueprint, render_template
from flask import current_app, url_for
from flask import Markup, escape
from flask_flatpages import FlatPages, Page
from flask_frozen import Freezer

__version__ = '0.4.1'

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ['.html', '.md']

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

# https://docs.python.org/3/library/locale.html#locale.setlocale
locale.setlocale(locale.LC_ALL, '')

flekky = Blueprint('flekky', __name__)


def _(s):
    return s


def shift_headings(html, offset):
    if offset == 0:
        return html

    soup = BeautifulSoup(html, 'html.parser')

    order = range(1, 6)
    if offset > 0:
        order = reversed(order)

    for i in order:
        j = min(max(i + offset, 1), 6)
        for tag in soup.find_all('h%i' % i):
            tag.name = 'h%i' % j

    return str(soup)


def page_fix_outline(self, base_heading_level):
    return shift_headings(self.html, base_heading_level - 1)


Page.fix_outline = page_fix_outline


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

    def by_key(self, key, value, default=None, is_list=False):
        if is_list:
            return (p for p in self if value in p.meta.get(key, []))
        else:
            return (p for p in self if value == p.meta.get(key, default))

    def values(self, key, is_list=False):
        if is_list:
            values = set()
            for page in self:
                values.update(set(page.meta.get(key, [])))
            return values
        else:
            return set([p.meta[key] for p in self if key in p.meta])


pages = FlekkyPages()


# filters
@flekky.app_template_filter('datetime')
def filter_datetime(dt, format="%c"):
    """Convert datetime object to HTML5 markup representing full datetime."""
    return Markup('<time datetime="%s">%s</time>' % (dt, dt.strftime(format)))


@flekky.app_template_filter('date')
def filter_date(dt, format="%x"):
    """Convert datetime object to HTML5 markup representing date only."""
    if isinstance(dt, datetime):
        dt = dt.date()
    return Markup('<time datetime="%s">%s</time>' % (dt, dt.strftime(format)))


@flekky.app_template_filter('time')
def filter_time(dt, format="%X"):
    """Convert datetime object to HTML5 markup representing time only."""
    return Markup('<time datetime="%s">%s</time>' % (dt.time(),
                                                     dt.strftime(format)))


@flekky.app_template_filter('link_page')
def filter_link_page(page):
    """Convert page object to an HTML link to that page."""
    if page is not None:
        href = url_for('flekky.page_route', path=page.path)
        text = page.meta['title']
        return Markup('<a href="%s">%s</a>' % (href, escape(text)))


def _site(_pages):
    """Construct site wide variables.

    ... as opposed to page specific variables.
    """
    site = {
        'title': 'Flekky',
        'time': datetime.now(),
        'pages': _pages,
        'config': current_app.config,
    }

    index = _pages.get('index')
    if hasattr(index, 'meta'):
        site.update(index.meta)

    return site


@flekky.route('/', defaults={'path': 'index'})
@flekky.route('/<path:path>/')
def page_route(path):
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
    def urls():
        yield '.page_route', {'path': '/'}
        for page in pages:
            yield '.page_route', {'path': page.path}

    freezer = Freezer(create_app(*args, **kwargs))
    freezer.register_generator(urls)
    return freezer


def parse_args(argv=None):
    """Parse command line arguments.

    Args:
        argv (list): List of command line parameters.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--version', '-V', action='version', version=__version__)
    parser.add_argument(
        '--source', '-s', default='_source',
        help=_('directory where Flekky will read files (default: _source)'))
    parser.add_argument(
        '--future', action='store_true', dest='FLEKKY_FUTURE',
        help=_('include pages with dates in the future (default: false)'))
    parser.add_argument(
        '--unpublished', action='store_true', dest='FLEKKY_UNPUBLISHED',
        help=_('include unpublished pages (default: false)'))
    subparsers = parser.add_subparsers(title=_('commands'))

    parser_build = subparsers.add_parser(
        'build', help=_('generate static sites'))
    parser_build.add_argument(
        '--destination', '-d', default=None,
        help=_('directory where Flekky will write files '
               '(default: <source>_build)'))
    parser_build.set_defaults(cmd='build')

    parser_serve = subparsers.add_parser(
        'serve', help=_('run a test server for development'))
    parser_serve.add_argument('--port', '-p', type=int, default=8000)
    parser_serve.set_defaults(cmd='serve')

    parser_build = subparsers.add_parser(
        'init', help=_('bootstrap a new project'))
    parser_build.set_defaults(cmd='init')

    return parser.parse_args(argv)


def rlink(src, dest):
    if os.path.isdir(src):
        if not os.path.exists(dest):
            os.mkdir(dest)
        for filename in os.listdir(src):
            rlink(os.path.join(src, filename), os.path.join(dest, filename))
    elif os.path.lexists(dest):
        if (not os.path.exists(dest) or
                os.path.getmtime(dest) < os.path.getmtime(src)):
            os.unlink(dest)
            os.link(src, dest)
    else:
        os.link(src, dest)


def main():  # pragma: no cover
    args = parse_args()
    source = os.path.abspath(args.source)

    if args.cmd == 'build':
        if args.destination is None:
            args.destination = '%s_build' % args.source
        destination = os.path.abspath(args.destination)
        args.FREEZER_DESTINATION = destination
        freezer = create_freezer(source, args)
        freezer.freeze()

        # copy all additional files
        for filename in os.listdir(source):
            if (filename not in ['pages', 'static', 'templates'] and
                    not filename.startswith('_') and
                    not filename.startswith('.')):
                srcpath = os.path.join(source, filename)
                dstpath = os.path.join(destination, filename)
                rlink(srcpath, dstpath)
    elif args.cmd == 'serve':
        app = create_app(source, args)
        app.run(port=args.port)
    elif args.cmd == 'init':
        init = resource_filename(__name__, 'init')
        shutil.copytree(init, source)
        print(_('Created new project in %s.') % source)
    else:
        raise ValueError('invalid command: %s' % args.cmd)


if __name__ == '__main__':  # pragma: no cover
    main()

# vim: set ts=4 sw=4 sts=4 et:
