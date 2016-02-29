Changelog
=========

0.3.0 (2016-02-29)
------------------

- add ``init`` option to bootstrap a new project


0.2.0 (2016-01-04)
------------------

- allow HTML pages
- drop support for python2.6
- add support for python3.4
- rename ``flekky.page`` to ``flekky.page_route``, so calls to ``url_for`` need
  to be adjusted
- add ``--version`` command line option


0.1.1 (2015-02-06)
------------------

- Bugfix on ``rlink()``


0.1.0 (2015-02-06)
------------------

- tags and category support has been removed.  Instead, the generic functions
  ``by_key`` and ``values`` have been introduced.
- Additional files in root folder may now also be directories.


0.0.2 (2014-06-14)
------------------

- Default destination depends on source.
- Any additional files from the root folder that do not begin with
  an underscore (``_``) or dot (``.``) will be copied verbatim.


0.0.1 (2014-06-14)
------------------

- initial release
