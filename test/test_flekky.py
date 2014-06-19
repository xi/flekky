import sys
import os

from datetime import datetime
from flask import Markup
from werkzeug.exceptions import NotFound

try:
    import unittest2 as unittest
except ImportError:
    import unittest

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

from flekky import flekky

if sys.version_info[0] < 3:
    from StringIO import StringIO
    _str = unicode
else:
    from io import StringIO
    _str = str


ENVIRON = {
    'SERVER_NAME': 'localhost',
    'wsgi.url_scheme': 'http',
    'SERVER_PORT': '80',
    'REQUEST_METHOD': 'GET',
    'PATH_INFO': '/',
}


class TestCase(unittest.TestCase):
    def setUp(self):
        source = os.path.join(root, '_example')
        self.app = flekky.create_app(source)
        self.pages = flekky.FlekkyPages(self.app)


class TestFlekkyPages(TestCase):
    def test_get(self):
        self.assertTrue(self.pages.get('test') is not None)
        self.assertTrue(self.pages.get('draft') is None)
        self.assertTrue(self.pages.get('future') is None)
        self.assertTrue(self.pages.get('nonexistent') is None)

    def test_iter(self):
        actual = set([p.path for p in self.pages])
        expected = set(['lorem ipsum', 'test', 'tag/test', 'tag/example',
                        'category/greeting'])
        self.assertSetEqual(actual, expected)

    def test_by_tag(self):
        by_tag = self.pages.by_key('tags', 'test', is_list=True)
        paths = set([p.path for p in by_tag])
        self.assertSetEqual(paths, set(['test']))

    def test_by_category(self):
        by_category = self.pages.by_key('category', 'greeting')
        paths = set([p.path for p in by_category])
        self.assertSetEqual(paths, set(['test']))

    def test_tags(self):
        actual = self.pages.values('tags', is_list=True)
        expected = set(['test', 'example'])
        self.assertSetEqual(actual, expected)

    def test_categories(self):
        self.assertSetEqual(self.pages.values('category'), set(['greeting']))


class TestFilters(TestCase):
    dt = datetime(2012, 3, 20, 20)

    def test_datetime(self):
        expected = Markup('<time datetime="2012-03-20 20:00:00">'
            'Tue Mar 20 20:00:00 2012</time>')
        actual = flekky.filter_datetime(self.dt)
        self.assertEqual(expected, actual)

    def test_date(self):
        expected = Markup('<time datetime="2012-03-20">03/20/12</time>')
        actual = flekky.filter_date(self.dt)
        self.assertEqual(expected, actual)

    def test_time(self):
        expected = Markup('<time datetime="20:00:00">20:00:00</time>')
        actual = flekky.filter_time(self.dt)
        self.assertEqual(expected, actual)

    def test_link_page(self):
        expected = Markup('<a href="/test/">Hello World</a>')
        page = self.pages.get('test')
        with self.app.request_context(ENVIRON):
            actual = flekky.filter_link_page(page)
        self.assertEqual(expected, actual)

        with self.app.request_context(ENVIRON):
            self.assertIsNone(flekky.filter_link_page(None))


class TestRoutes(TestCase):
    def test_page(self):
        with self.app.request_context(ENVIRON):
            self.assertTrue(isinstance(flekky.page('test'), _str))
            self.assertRaises(NotFound, flekky.page, 'nonexistent')


class TestFreeze(unittest.TestCase):
    def test_freeze(self):
        source = os.path.join(root, '_example')
        self.freezer = flekky.create_freezer(source)
        expected = set(['/static/css/style.css', '/test/', '/lorem ipsum/',
                        '/tag/test/', '/tag/example/', '/category/greeting/'])
        actual = set(self.freezer.all_urls())
        self.assertSetEqual(actual, expected)


class TestArgs(unittest.TestCase):
    def setUp(self):
        self._stdout = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out

        self._stderr = sys.stderr
        self.err = StringIO()
        sys.stderr = self.err

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._stdout

        sys.stderr.close()
        sys.stderr = self._stderr

    def get_out(self):
        return self.out.getvalue().strip()

    def get_err(self):
        return self.err.getvalue().strip()

    def test_serve_default(self):
        args = flekky.parse_args(['serve'])
        self.assertEqual(args.cmd, 'serve')
        self.assertEqual(args.source, '_source')
        self.assertFalse(args.FLEKKY_FUTURE)
        self.assertFalse(args.FLEKKY_UNPUBLISHED)
        self.assertEqual(args.port, 8000)

    def test_build_default(self):
        args = flekky.parse_args(['build'])
        self.assertEqual(args.cmd, 'build')
        self.assertEqual(args.source, '_source')
        self.assertFalse(args.FLEKKY_FUTURE)
        self.assertFalse(args.FLEKKY_UNPUBLISHED)
        self.assertIsNone(args.destination)

    def test_invalid_cmd(self):
        self.assertRaises(SystemExit, flekky.parse_args, ['invalid'])
        self.assertTrue(self.get_err().startswith('usage'))

    def test_help(self):
        self.assertRaises(SystemExit, flekky.parse_args, ['-h'])
        self.assertTrue(self.get_out().startswith('usage'))

if __name__ == '__main__':
    unittest.main()

# vim: set ts=4 sw=4 sts=4 et:
