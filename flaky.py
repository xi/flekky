# -*- coding: utf-8 -*-
"""Static website generator inspired by jekyll based on flask.

Based on the tutorial on https://nicolas.perriault.net/code/2012/dead-easy-\
yet-powerful-static-website-generator-with-flask/.

"""

import argparse
from datetime import date

from flask import Flask, Blueprint, render_template, abort
from flask import current_app
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

pages = FlatPages()
flaky = Blueprint('flaky', __name__)

_ = lambda s: s


@flaky.route('/')
def index():
    return render_template('index.html', pages=pages)


@flaky.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag)


@flaky.route('/category/<string:category>/')
def category(category):
    categories = lambda p: p.meta.get('category', p.meta.get('categories', []))
    categorized = [p for p in pages if category in categories(p)]
    return render_template('category.html', pages=categorized,
                           category=category)


@flaky.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)

    include_unpublished = current_app.config.get('FLAKY_UNPUBLISHED', False)
    if not include_unpublished and not page.meta.get('published', True):
        abort(404)

    include_future = current_app.config.get('FLAKY_FUTURE', False)
    is_future = 'date' in page.meta and page.meta['date'] > date.today()
    if not include_future and is_future:
        abort(404)

    template = 'layout/%s.html' % page.meta.get('layout', 'page')
    return render_template(template, page=page)


def create_app(settings=None):
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.config.from_object(settings)
    app.register_blueprint(flaky)
    pages.init_app(app)
    return app


def create_freezer(settings=None):
    return Freezer(create_app(settings))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', '-s', default='_source', metavar='SOURCE',
                        dest='FLATPAGES_ROOT', help=_('directory where flaky '
                        'will read files (default: _source)'))
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
        freezer = create_freezer(args)
        freezer.freeze()
    elif args.cmd == 'serve':
        app = create_app(args)
        app.run(port=args.port)
    else:
        raise ValueError('invalid command: %s' % args.cmd)

# vim: set ts=4 sw=4 sts=4 et:
