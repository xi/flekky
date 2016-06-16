import sys
import os
from random import randint
from shutil import rmtree
from time import sleep
import locale

from datetime import datetime
from flask import Markup
from werkzeug.exceptions import NotFound

import unittest

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

locale.setlocale(locale.LC_ALL, 'C')

from flekky import flekky  # noqa

if sys.version_info[0] < 3:
    from StringIO import StringIO
    _str = unicode  # noqa
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
            self.assertTrue(isinstance(flekky.page_route('test'), _str))
            self.assertRaises(NotFound, flekky.page_route, 'nonexistent')


class TestFreeze(unittest.TestCase):
    def test_freeze(self):
        source = os.path.join(root, '_example')
        self.freezer = flekky.create_freezer(source)
        expected = set(['/static/css/style.css', '/test/', '/lorem ipsum/',
                        '/tag/test/', '/tag/example/', '/category/greeting/',
                        '/'])
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


class TestRLink(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.abspath('.tmp_%i' % randint(1000, 10000))
        os.mkdir(self.dirname)

    def tearDown(self):
        rmtree(self.dirname)

    def touch(self, path):
        with open(path, 'a'):
            pass

    def test_file(self):
        src = os.path.join(self.dirname, 'file')
        dest = os.path.join(self.dirname, 'link')
        self.touch(src)
        flekky.rlink(src, dest)
        self.assertTrue(os.path.samefile(src, dest))

    def test_file_exists_newer(self):
        src1 = os.path.join(self.dirname, 'file1')
        src2 = os.path.join(self.dirname, 'file2')
        dest = os.path.join(self.dirname, 'link')
        self.touch(src1)
        self.touch(src2)
        flekky.rlink(src1, dest)
        flekky.rlink(src2, dest)
        self.assertFalse(os.path.samefile(src1, src2))
        self.assertTrue(os.path.samefile(src1, dest))
        self.assertFalse(os.path.samefile(src2, dest))

    def test_file_exists_older(self):
        src1 = os.path.join(self.dirname, 'file1')
        src2 = os.path.join(self.dirname, 'file2')
        dest = os.path.join(self.dirname, 'link')
        self.touch(src1)
        flekky.rlink(src1, dest)
        sleep(0.1)
        self.touch(src2)
        flekky.rlink(src2, dest)
        self.assertFalse(os.path.samefile(src1, src2))
        self.assertFalse(os.path.samefile(src1, dest))
        self.assertTrue(os.path.samefile(src2, dest))

    def test_dir(self):
        src = os.path.join(self.dirname, 'src')
        dest = os.path.join(self.dirname, 'dest')
        os.mkdir(src)
        self.touch(os.path.join(src, 'file'))

        flekky.rlink(src, dest)
        self.assertTrue(os.path.samefile(
            os.path.join(src, 'file'),
            os.path.join(dest, 'file')))

    def test_dir_dir(self):
        src = os.path.join(self.dirname, 'src')
        dest = os.path.join(self.dirname, 'dest')
        os.mkdir(src)
        os.mkdir(os.path.join(src, 'dir'))
        self.touch(os.path.join(src, 'dir', 'file'))

        flekky.rlink(src, dest)
        self.assertTrue(os.path.samefile(
            os.path.join(src, 'dir', 'file'),
            os.path.join(dest, 'dir', 'file')))

    def test_empty_dir(self):
        src = os.path.join(self.dirname, 'src')
        dest = os.path.join(self.dirname, 'dest')
        os.mkdir(src)
        os.mkdir(os.path.join(src, 'dir'))

        flekky.rlink(src, dest)
        self.assertTrue(os.path.isdir(os.path.join(src, 'dir')))

    def test_dir_exists_file(self):
        src = os.path.join(self.dirname, 'src')
        dest = os.path.join(self.dirname, 'dest')
        os.mkdir(src)
        os.mkdir(dest)
        os.mkdir(os.path.join(src, 'dir'))
        self.touch(os.path.join(dest, 'dir'))

        flekky.rlink(src, dest)
        self.assertTrue(os.path.isdir(os.path.join(src, 'dir')))


if __name__ == '__main__':
    unittest.main()

# vim: set ts=4 sw=4 sts=4 et:
