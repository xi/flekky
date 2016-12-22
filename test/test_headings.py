import unittest

from flekky.flekky import shift_headings


class TestShiftHeadings(unittest.TestCase):
    def test_no_headings(self):
        actual = shift_headings('<a>test</a>', 1)
        self.assertEqual(actual, '<a>test</a>')

    def test_h1_shift_1(self):
        actual = shift_headings('<h1>test</h1>', 1)
        self.assertEqual(actual, '<h2>test</h2>')

    def test_h1_shift_3(self):
        actual = shift_headings('<h1>test</h1>', 3)
        self.assertEqual(actual, '<h4>test</h4>')

    def test_h1_shift_7(self):
        actual = shift_headings('<h1>test</h1>', 7)
        self.assertEqual(actual, '<h6>test</h6>')

    def test_h1_shift_0(self):
        actual = shift_headings('<h1>test</h1>', 0)
        self.assertEqual(actual, '<h1>test</h1>')

    def test_h1_unshift_1(self):
        actual = shift_headings('<h1>test</h1>', -1)
        self.assertEqual(actual, '<h1>test</h1>')

    def test_mixed_shift_1(self):
        actual = shift_headings('<h1>test</h1><h3>foo</h3>'
            '<div><h4>baz</h4></div>', 1)
        self.assertEqual(actual, '<h2>test</h2><h4>foo</h4>'
            '<div><h5>baz</h5></div>')

    def test_mixed_unshift_2(self):
        actual = shift_headings('<h1>test</h1><h3>foo</h3>'
            '<div><h4>baz</h4></div>', -2)
        self.assertEqual(actual, '<h1>test</h1><h1>foo</h1>'
            '<div><h2>baz</h2></div>')
