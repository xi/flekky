About
=====

Flekky is a static website generator inspired by `Jekyll`_ but written
in python and based on `Flask`_. It is basically a wrapper around the
excellent `Frozen Flask`_ and `Flask FlatPages`_ as described in `this
article`_ by Nicolas Perriault.

So what does it do? It allows you to write templates, assets and
contents for your website and bake all that into static HTML. You can
than deploy that HTML on any webserver and do not have to worry about
anything. `Jinja2`_ is used for templating. `Markdown`_ is used for
creating content.

There are many static website generators out there of which Jekyll is
arguably the most popular. You are probably better of with that. But if
you like Flask and have fun experimenting with things you might give
Flekky a try.

Quickstart
==========

::

    $ pip install flekky
    $ flekky init
    $ flekky build

Basic Usage
===========

To start a new project, run the ``init`` command::

    $ flekky init

You can generate static HTML by using the ``build`` command::

    $ flekky build

Flekky also comes with a built-in development server that will allow you
to preview what the generated site will look like in your browser
locally::

    $ flekky serve

File structure
==============

A basic Flekky site usually looks like this::

    _source
    ├── pages
    │   ├── index.md
    │   └── test.md
    ├── static
    │   ├── css
    │   │   └── style.css
    │   └── js
    └── templates
        ├── base.html
        ├── layout
        │   ├── category.html
        │   ├── default.html
        │   ├── post.html
        │   └── tag.html
        └── partial.html

An overview of what each of them does:

-  ``pages``: Your dynamic content, so to speak. These are Markdown
   files, but they also contain some `YAML`_ data at the top.
   ``index.md`` is special because all its metadata is added to ``site``
   , so you can use it to set the title of the complete website.

-  ``static``: Static files like CSS, JavaScript and images.

-  ``templates``: Each page can select a layout that is used to render that
   page. But you will probably also want to include a ``base.html`` that
   these layouts can extend and maybe some partials that can be included.

-  Any additional files from the root folder that do not begin with
   an underscore (``_``) or dot (``.``) will be copied verbatim.

Command-line options
====================

Flekky has several command-line options:

-  general

   -  ``--source``: directory where Flekky will read files (default:
      ``_source``)
   -  ``--future``: include pages with dates in the future (default:
      ``false``)
   -  ``--unpublished``: include unpublished pages (default: ``false``)

-  build

   -  ``--destination``: directory where Flekky will write files
      (default: ``<source>_build``)

-  serve

   -  ``--port``: port to run at (default: ``8000``)

Variables
=========

Flekky makes a variety of data available to the templating system. The
following is a reference of the available data.

page
----

A page is a Markdown file in the ``pages`` folder. However, at the top
of the file you can (and should) set some meta data using `YAML`_
syntax. All key-value pairs defined here will be available in the
templates. But some fields also have a special meaning:

-  ``title``: Title for this page.

-  ``layout``: Select a template from the ``layout`` folder for
   rendering (default: ``default``).

-  ``published``: Unpublished pages will not be included in the website.
   This can be disabled using the ``--unpublished`` command-line option.

-  ``date``: Pages with dates in the future are not included in the
   website. This can be disabled using the ``--future`` command-line
   option.

site
----

The site object stores all data that applies to the whole project. This
also includes any metadata from ``index.md``.

-  ``title``: Title of the website.

-  ``time``: Current time. This can be used to display the time of the
   last build.

-  ``pages``: A list of all pages.

-  ``config``: The complete configuration.

Tags and Categories
===================

Tags and categories are commonly used on websites.  The ``site.pages`` object
available in templates containes the functions ``by_key`` and ``values`` that
can be used to implement them.

``by_key`` will return only those pages that match the given key/value pair.
So ``by_key('category', 'greeting')`` will return a list of all pages in
category 'greeting'.  ``by_key('tags', 'example', is_list=True)`` will return
all pages that have the 'example' tag.  Note that ``tags`` should be a list,
so the ``is_list`` argument is needed here.

``values`` will return a list of all values that have been used with a given
key.  So ``values('category')`` will return a list with all categories and
``values('tags', is_list=True)`` will return a list with all tags.

These functions can be used to create a template for tag or category pages
respectively.  Note that tag and category pages will not be created
automatically.

But these functions can not only be used for tags and categories.  You can
basically define any structure you want.  Or you can filter by existing field,
e.g. by layout.

Differences from Jekyll
=======================

Flekky aims at being very similar to Jekyll. However it is far from
being a drop-in replacement. Some of the missing features might be added
in the future. For now, these are some of the most important
differences:

-  written in python and based on Flask

-  Markdown only (though it should be easy to extend)

-  slightly different directory structure

   -  no configuration file like ``_config.yml``
   -  ``templates`` instead of ``_includes`` and ``_layouts``
   -  ``pages`` instead of top level files and ``_posts``
   -  no drafts
   -  no data files
   -  date is not encoded in file name

-  only pages that are linked to are included in the build

-  no build-in SCSS or CoffeeScript support

-  different (but similar) templating syntax

-  no separators before and after YAML data in page files

-  no build-in pagination

-  no build-in plugin system but the rich Flask ecosystem

License
=======

Copyright (C) 2014 Tobias Bengfort tobias.bengfort@gmx.net

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see http://www.gnu.org/licenses/.

.. _Jekyll: http://jekyllrb.com/
.. _Flask: http://flask.pocoo.org/
.. _Frozen Flask: http://packages.python.org/Frozen-Flask/
.. _Flask FlatPages: http://packages.python.org/Flask-FlatPages/
.. _this article: https://nicolas.perriault.net/code/2012/dead-easy-yet-powerful-static-website-generator-with-flask/
.. _Jinja2: http://jinja.pocoo.org/
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _YAML: http://yaml.org/
