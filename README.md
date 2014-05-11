About
=====

Flaky is a static website generator inspired by [Jekyll] but written in
python and based on [Flask].  It is basically a wrapper around the excellent
[Frozen-Flask] and [Flask-FlatPages] as described in [this
article][article] by Nicolas Perriault.

So what does it do? It allows you to write templates, assets and contents for
your website and bake all that into static HTML. You can than deply that HTML
on any webserver and do not have to worry about anything. [Jinja2] is used
for templating. [Markdown] is used for creating content.

There are many static website generators out there of which Jekyll is arguably
the most popular. You are probably better of with that. But if you like Flask
and have fun experimenting with things you might give Flaky a try.

Quickstart
==========

    $ virtualenv init env
    $ . env/bin/activate
    $ pip -Ur requirements.txt
    $ python flaky.py --source _example build --destination _deploy

Basic Usage
===========

You can generate static HTML by using the `build` command:

    $ python flaky.py build

Please note that Flaky uses crawling to find your pages. It starts with
`index.html` and follows links from there. If a page is never linked it will
not be included in the build.

Flaky also comes with a built-in development server that will allow you to
preview what the generated site will look like in your browser locally.

    $ python flaky.py serve

File structure
==============

A basic Flaky site usually looks like this:

    _source
    ├── pages
    │   └── test.md
    ├── static
    │   ├── css
    │   │   └── style.css
    │   └── js
    └── templates
        ├── base.html
        ├── category.html
        ├── index.html
        ├── layout
        │   ├── default.html
        │   └── post.html
        └── tag.html

An overview of what each of them does:

-   `pages`: Your dynamic content, so to speak. These are Markdown files, but
    they also contain some [YAML] data at the top.

-   `static`: Static files like CSS, JavaScript and images.

-   `templates`: You will probably want to include a `base.html` that all other
    templates can extend. `index.html` is used to render the front page;
    `category.html` and `tag.html` are used to render category and tag pages
    respectively.  Layouts are used to render pages.

Command-line options
====================

Flaky has several command-line options:

-   general
    -   `--source`: directory where Flaky will read files (default: `_source`)
    -   `--future`: include pages with dates in the future (default: `false`)
    -   `--unpublished`: include unpublished pages (default: `false`)

-   build
    -   `--destination`: directory where Flaky will write files (default: `_deploy`)

-   serve
    -   `--port`: port to run at (default: `8000`)

Variables
=========

Flaky makes a variety of data available to the templating system. The following
is a reference of the available data.

page
----

A page is a Markdown file in the `pages` folder. However, at the top of the
file you can (and should) set some meta data using [YAML] syntax. All key-value
pairs defined here will be available in the templates. But some fields also
have a special meaning:

-   `title`: Title for this page.

-   `layout`: Select a template from the `layout` folder for rendering (default:
    `default`).

-   `published`: Unpublished pages will not be included in the website. This can
    be disabled using the `--unpublished` command-line option.

-   `date`: Pages with dates in the future are not included in the website.
    This can be disabled using the `--future` command-line option.

-   `category`: Each page can be filed under a single category. It will be
    included on the category page.

-   `tags`: Tags can be used to categorize pages. They are very similar to
    categories with the difference that a page can have multiple tags.

site
----

The site object stores all data that applies to the whole project:

-   `time`: Current time. This can be used to display the time of the last build.

-   `pages`: A list of all pages.

-   `categories`: A list of all used categories.

-   `tags`: A list of all used tags.

-   `config`: The  complete configuration.

Differences from Jekyll
=======================

Flaky aims at being very similar to Jekyll. However it is far from being a
drop-in replacement. Some of the missing features might be added in the future.
For now, these are some of the most important differences:

-   written in python and based on Flask

-   Markdown only (though it should be easy to extend)

-   slightly different directory structure
    -   no configuration file like `_config.yml`
    -   `templates` instead of `_includes` and `_layouts`
    -   `pages` instead of top level files and `_posts`
    -   no drafts
    -   no data files
    -   date is not encoded in file name
    -   additional files are not copied automatically

-   only pages that are linked to are included in the build

-   no build-in SCSS or CoffeeScript support

-   different (but similar) templating syntax

-   no separators before and after YAML data in page files

-   no build-in pagination

-   no build-in plugin system but the rich Flask ecosystem

License
=======

Copyright (C) 2014 Tobias Bengfort <tobias.bengfort@gmx.net>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.


[Jekyll]: http://jekyllrb.com/
[Flask]: http://flask.pocoo.org/
[Frozen-Flask]: http://packages.python.org/Frozen-Flask/
[Flask-FlatPages]: http://packages.python.org/Flask-FlatPages/
[article]: https://nicolas.perriault.net/code/2012/dead-easy-yet-powerful-static-website-generator-with-flask/
[Jinja2]: http://jinja.pocoo.org/
[Markdown]: http://daringfireball.net/projects/markdown/
[YAML]: http://yaml.org/
