# -*- coding: utf-8 -*-
"""Static website generator inspired by jekyll based on flask.

Based on the tutorial on https://nicolas.perriault.net/code/2012/dead-easy-\
yet-powerful-static-website-generator-with-flask/.

"""

import argparse

from flask import Flask, render_template
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

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
freezer = Freezer(app)


@app.route('/')
def index():
    return render_template('index.html', pages=pages)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag)


@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    return render_template('page.html', page=page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cmd', choices={'serve', 'build'}, nargs='?',
                        default='serve')
    args = parser.parse_args()

    if args.cmd == 'build':
        freezer.freeze()
    else:
        app.run(port=8000)

# vim: set ts=4 sw=4 sts=4 et:
