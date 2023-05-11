import unittest
import sys
from test import support
from test.support import import_helper

try:
    import _testcapi
except ImportError:
    _testcapi = None


NULL = None

class Str(str):
    pass


class CAPITest(unittest.TestCase):

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_new(self):
        """Test PyUnicode_New()"""
        from _testcapi import unicode_new as new

        for maxchar in 0, 0x61, 0xa1, 0x4f60, 0x1f600, 0x10ffff:
            self.assertEqual(new(0, maxchar), '')
            self.assertEqual(new(5, maxchar), chr(maxchar)*5)
        self.assertEqual(new(0, 0x110000), '')
        self.assertRaises(SystemError, new, 5, 0x110000)
        self.assertRaises(SystemError, new, -1, 0)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_fill(self):
        """Test PyUnicode_Fill()"""
        from _testcapi import unicode_fill as fill

        strings = [
            # all strings have exactly 5 characters
            'abcde', '\xa1\xa2\xa3\xa4\xa5',
            '\u4f60\u597d\u4e16\u754c\uff01',
            '\U0001f600\U0001f601\U0001f602\U0001f603\U0001f604'
        ]
        chars = [0x78, 0xa9, 0x20ac, 0x1f638]

        for idx, fill_char in enumerate(chars):
            # wide -> narrow: exceed maxchar limitation
            for to in strings[:idx]:
                self.assertRaises(ValueError, fill, to, 0, 0, fill_char)
            for to in strings[idx:]:
                for start in range(7):
                    for length in range(-1, 7 - start):
                        filled = max(min(length, 5 - start), 0)
                        if filled == 5 and to != strings[idx]:
                            # narrow -> wide
                            # Tests omitted since this creates invalid strings.
                            continue
                        expected = to[:start] + chr(fill_char) * filled + to[start + filled:]
                        self.assertEqual(fill(to, start, length, fill_char),
                                        (expected, filled))

        s = strings[0]
        self.assertRaises(IndexError, fill, s, -1, 0, 0x78)
        self.assertRaises(ValueError, fill, s, 0, 0, 0x110000)
        self.assertRaises(SystemError, fill, b'abc', 0, 0, 0x78)
        self.assertRaises(SystemError, fill, [], 0, 0, 0x78)
        # CRASHES fill(s, 0, NULL, 0, 0)
        # CRASHES fill(NULL, 0, 0, 0x78)
        # TODO: Test PyUnicode_Fill() with non-modifiable unicode.

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_writechar(self):
        """Test PyUnicode_ReadChar()"""
        from _testcapi import unicode_writechar as writechar

        strings = [
            # one string for every kind
            'abc', '\xa1\xa2\xa3', '\u4f60\u597d\u4e16',
            '\U0001f600\U0001f601\U0001f602'
        ]
        # one character for every kind + out of range code
        chars = [0x78, 0xa9, 0x20ac, 0x1f638, 0x110000]
        for i, s in enumerate(strings):
            for j, c in enumerate(chars):
                if j <= i:
                    self.assertEqual(writechar(s, 1, c),
                                     (s[:1] + chr(c) + s[2:], 0))
                else:
                    self.assertRaises(ValueError, writechar, s, 1, c)

        self.assertRaises(IndexError, writechar, 'abc', 3, 0x78)
        self.assertRaises(IndexError, writechar, 'abc', -1, 0x78)
        self.assertRaises(TypeError, writechar, b'abc', 0, 0x78)
        self.assertRaises(TypeError, writechar, [], 0, 0x78)
        # CRASHES writechar(NULL, 0, 0x78)
        # TODO: Test PyUnicode_CopyCharacters() with non-modifiable and legacy
        # unicode.

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_resize(self):
        """Test PyUnicode_Resize()"""
        from _testcapi import unicode_resize as resize

        strings = [
            # all strings have exactly 3 characters
            'abc', '\xa1\xa2\xa3', '\u4f60\u597d\u4e16',
            '\U0001f600\U0001f601\U0001f602'
        ]
        for s in strings:
            self.assertEqual(resize(s, 3), (s, 0))
            self.assertEqual(resize(s, 2), (s[:2], 0))
            self.assertEqual(resize(s, 4), (s + '\0', 0))
            self.assertEqual(resize(s, 0), ('', 0))
        self.assertRaises(SystemError, resize, b'abc', 0)
        self.assertRaises(SystemError, resize, [], 0)
        self.assertRaises(SystemError, resize, NULL, 0)
        # TODO: Test PyUnicode_Resize() with non-modifiable and legacy unicode
        # and with NULL as the address.

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_append(self):
        """Test PyUnicode_Append()"""
        from _testcapi import unicode_append as append

        strings = [
            'abc', '\xa1\xa2\xa3', '\u4f60\u597d\u4e16',
            '\U0001f600\U0001f601\U0001f602'
        ]
        for left in strings:
            left = left[::-1]
            for right in strings:
                expected = left + right
                self.assertEqual(append(left, right), expected)

        self.assertRaises(SystemError, append, 'abc', b'abc')
        self.assertRaises(SystemError, append, b'abc', 'abc')
        self.assertRaises(SystemError, append, b'abc', b'abc')
        self.assertRaises(SystemError, append, 'abc', [])
        self.assertRaises(SystemError, append, [], 'abc')
        self.assertRaises(SystemError, append, [], [])
        self.assertRaises(SystemError, append, NULL, 'abc')
        self.assertRaises(SystemError, append, 'abc', NULL)
        # TODO: Test PyUnicode_Append() with modifiable unicode
        # and with NULL as the address.
        # TODO: Check reference counts.

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_appendanddel(self):
        """Test PyUnicode_AppendAndDel()"""
        from _testcapi import unicode_appendanddel as appendanddel

        strings = [
            'abc', '\xa1\xa2\xa3', '\u4f60\u597d\u4e16',
            '\U0001f600\U0001f601\U0001f602'
        ]
        for left in strings:
            left = left[::-1]
            for right in strings:
                self.assertEqual(appendanddel(left, right), left + right)

        self.assertRaises(SystemError, appendanddel, 'abc', b'abc')
        self.assertRaises(SystemError, appendanddel, b'abc', 'abc')
        self.assertRaises(SystemError, appendanddel, b'abc', b'abc')
        self.assertRaises(SystemError, appendanddel, 'abc', [])
        self.assertRaises(SystemError, appendanddel, [], 'abc')
        self.assertRaises(SystemError, appendanddel, [], [])
        self.assertRaises(SystemError, appendanddel, NULL, 'abc')
        self.assertRaises(SystemError, appendanddel, 'abc', NULL)
        # TODO: Test PyUnicode_AppendAndDel() with modifiable unicode
        # and with NULL as the address.
        # TODO: Check reference counts.

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_fromstringandsize(self):
        """Test PyUnicode_FromStringAndSize()"""
        from _testcapi import unicode_fromstringandsize as fromstringandsize

        self.assertEqual(fromstringandsize(b'abc'), 'abc')
        self.assertEqual(fromstringandsize(b'abc', 2), 'ab')
        self.assertEqual(fromstringandsize(b'abc\0def'), 'abc\0def')
        self.assertEqual(fromstringandsize(b'\xc2\xa1\xc2\xa2'), '\xa1\xa2')
        self.assertEqual(fromstringandsize(b'\xe4\xbd\xa0'), '\u4f60')
        self.assertEqual(fromstringandsize(b'\xf0\x9f\x98\x80'), '\U0001f600')
        self.assertRaises(UnicodeDecodeError, fromstringandsize, b'\xc2\xa1', 1)
        self.assertRaises(UnicodeDecodeError, fromstringandsize, b'\xa1', 1)
        self.assertEqual(fromstringandsize(b'', 0), '')
        self.assertEqual(fromstringandsize(NULL, 0), '')

        self.assertRaises(SystemError, fromstringandsize, b'abc', -1)
        # TODO: Test PyUnicode_FromStringAndSize(NULL, size) for size != 0

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_fromstring(self):
        """Test PyUnicode_FromString()"""
        from _testcapi import unicode_fromstring as fromstring

        self.assertEqual(fromstring(b'abc'), 'abc')
        self.assertEqual(fromstring(b'\xc2\xa1\xc2\xa2'), '\xa1\xa2')
        self.assertEqual(fromstring(b'\xe4\xbd\xa0'), '\u4f60')
        self.assertEqual(fromstring(b'\xf0\x9f\x98\x80'), '\U0001f600')
        self.assertRaises(UnicodeDecodeError, fromstring, b'\xc2')
        self.assertRaises(UnicodeDecodeError, fromstring, b'\xa1')
        self.assertEqual(fromstring(b''), '')

        # CRASHES fromstring(NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_fromkindanddata(self):
        """Test PyUnicode_FromKindAndData()"""
        from _testcapi import unicode_fromkindanddata as fromkindanddata

        strings = [
            'abcde', '\xa1\xa2\xa3\xa4\xa5',
            '\u4f60\u597d\u4e16\u754c\uff01',
            '\U0001f600\U0001f601\U0001f602\U0001f603\U0001f604'
        ]
        enc1 = 'latin1'
        for s in strings[:2]:
            self.assertEqual(fromkindanddata(1, s.encode(enc1)), s)
        enc2 = 'utf-16le' if sys.byteorder == 'little' else 'utf-16be'
        for s in strings[:3]:
            self.assertEqual(fromkindanddata(2, s.encode(enc2)), s)
        enc4 = 'utf-32le' if sys.byteorder == 'little' else 'utf-32be'
        for s in strings:
            self.assertEqual(fromkindanddata(4, s.encode(enc4)), s)
        self.assertEqual(fromkindanddata(2, '\U0001f600'.encode(enc2)),
                         '\ud83d\ude00')
        for kind in 1, 2, 4:
            self.assertEqual(fromkindanddata(kind, b''), '')
            self.assertEqual(fromkindanddata(kind, b'\0'*kind), '\0')
            self.assertEqual(fromkindanddata(kind, NULL, 0), '')

        for kind in -1, 0, 3, 5, 8:
            self.assertRaises(SystemError, fromkindanddata, kind, b'')
        self.assertRaises(ValueError, fromkindanddata, 1, b'abc', -1)
        self.assertRaises(ValueError, fromkindanddata, 1, NULL, -1)
        # CRASHES fromkindanddata(1, NULL, 1)
        # CRASHES fromkindanddata(4, b'\xff\xff\xff\xff')

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_substring(self):
        """Test PyUnicode_Substring()"""
        from _testcapi import unicode_substring as substring

        strings = [
            'ab', 'ab\xa1\xa2',
            'ab\xa1\xa2\u4f60\u597d',
            'ab\xa1\xa2\u4f60\u597d\U0001f600\U0001f601'
        ]
        for s in strings:
            for start in range(0, len(s) + 2):
                for end in range(max(start-1, 0), len(s) + 2):
                    self.assertEqual(substring(s, start, end), s[start:end])

        self.assertRaises(IndexError, substring, 'abc', -1, 0)
        self.assertRaises(IndexError, substring, 'abc', 0, -1)
        # CRASHES substring(b'abc', 0, 0)
        # CRASHES substring([], 0, 0)
        # CRASHES substring(NULL, 0, 0)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_getlength(self):
        """Test PyUnicode_GetLength()"""
        from _testcapi import unicode_getlength as getlength

        for s in ['abc', '\xa1\xa2', '\u4f60\u597d', 'a\U0001f600',
                  'a\ud800b\udfffc', '\ud834\udd1e']:
            self.assertEqual(getlength(s), len(s))

        self.assertRaises(TypeError, getlength, b'abc')
        self.assertRaises(TypeError, getlength, [])
        # CRASHES getlength(NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_readchar(self):
        """Test PyUnicode_ReadChar()"""
        from _testcapi import unicode_readchar as readchar

        for s in ['abc', '\xa1\xa2', '\u4f60\u597d', 'a\U0001f600',
                  'a\ud800b\udfffc', '\ud834\udd1e']:
            for i, c in enumerate(s):
                self.assertEqual(readchar(s, i), ord(c))
            self.assertRaises(IndexError, readchar, s, len(s))
            self.assertRaises(IndexError, readchar, s, -1)

        self.assertRaises(TypeError, readchar, b'abc', 0)
        self.assertRaises(TypeError, readchar, [], 0)
        # CRASHES readchar(NULL, 0)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_fromobject(self):
        """Test PyUnicode_FromObject()"""
        from _testcapi import unicode_fromobject as fromobject

        for s in ['abc', '\xa1\xa2', '\u4f60\u597d', 'a\U0001f600',
                  'a\ud800b\udfffc', '\ud834\udd1e']:
            self.assertEqual(fromobject(s), s)
            o = Str(s)
            s2 = fromobject(o)
            self.assertEqual(s2, s)
            self.assertIs(type(s2), str)
            self.assertIsNot(s2, s)

        self.assertRaises(TypeError, fromobject, b'abc')
        self.assertRaises(TypeError, fromobject, [])
        # CRASHES fromobject(NULL)

    def test_from_format(self):
        """Test PyUnicode_FromFormat()"""
        import_helper.import_module('ctypes')
        from ctypes import (
            c_char_p,
            pythonapi, py_object, sizeof,
            c_int, c_long, c_longlong, c_ssize_t,
            c_uint, c_ulong, c_ulonglong, c_size_t, c_void_p)
        name = "PyUnicode_FromFormat"
        _PyUnicode_FromFormat = getattr(pythonapi, name)
        _PyUnicode_FromFormat.argtypes = (c_char_p,)
        _PyUnicode_FromFormat.restype = py_object

        def PyUnicode_FromFormat(format, *args):
            cargs = tuple(
                py_object(arg) if isinstance(arg, str) else arg
                for arg in args)
            return _PyUnicode_FromFormat(format, *cargs)

        def check_format(expected, format, *args):
            text = PyUnicode_FromFormat(format, *args)
            self.assertEqual(expected, text)

        # ascii format, non-ascii argument
        check_format('ascii\x7f=unicode\xe9',
                     b'ascii\x7f=%U', 'unicode\xe9')

        # non-ascii format, ascii argument: ensure that PyUnicode_FromFormatV()
        # raises an error
        self.assertRaisesRegex(ValueError,
            r'^PyUnicode_FromFormatV\(\) expects an ASCII-encoded format '
            'string, got a non-ASCII byte: 0xe9$',
            PyUnicode_FromFormat, b'unicode\xe9=%s', 'ascii')

        # test "%c"
        check_format('\uabcd',
                     b'%c', c_int(0xabcd))
        check_format('\U0010ffff',
                     b'%c', c_int(0x10ffff))
        with self.assertRaises(OverflowError):
            PyUnicode_FromFormat(b'%c', c_int(0x110000))
        # Issue #18183
        check_format('\U00010000\U00100000',
                     b'%c%c', c_int(0x10000), c_int(0x100000))

        # test "%"
        check_format('%',
                     b'%%')
        check_format('%s',
                     b'%%s')
        check_format('[%]',
                     b'[%%]')
        check_format('%abc',
                     b'%%%s', b'abc')

        # truncated string
        check_format('abc',
                     b'%.3s', b'abcdef')
        check_format('abc[\ufffd',
                     b'%.5s', 'abc[\u20ac]'.encode('utf8'))
        check_format("'\\u20acABC'",
                     b'%A', '\u20acABC')
        check_format("'\\u20",
                     b'%.5A', '\u20acABCDEF')
        check_format("'\u20acABC'",
                     b'%R', '\u20acABC')
        check_format("'\u20acA",
                     b'%.3R', '\u20acABCDEF')
        check_format('\u20acAB',
                     b'%.3S', '\u20acABCDEF')
        check_format('\u20acAB',
                     b'%.3U', '\u20acABCDEF')
        check_format('\u20acAB',
                     b'%.3V', '\u20acABCDEF', None)
        check_format('abc[\ufffd',
                     b'%.5V', None, 'abc[\u20ac]'.encode('utf8'))

        # following tests comes from #7330
        # test width modifier and precision modifier with %S
        check_format("repr=  abc",
                     b'repr=%5S', 'abc')
        check_format("repr=ab",
                     b'repr=%.2S', 'abc')
        check_format("repr=   ab",
                     b'repr=%5.2S', 'abc')

        # test width modifier and precision modifier with %R
        check_format("repr=   'abc'",
                     b'repr=%8R', 'abc')
        check_format("repr='ab",
                     b'repr=%.3R', 'abc')
        check_format("repr=  'ab",
                     b'repr=%5.3R', 'abc')

        # test width modifier and precision modifier with %A
        check_format("repr=   'abc'",
                     b'repr=%8A', 'abc')
        check_format("repr='ab",
                     b'repr=%.3A', 'abc')
        check_format("repr=  'ab",
                     b'repr=%5.3A', 'abc')

        # test width modifier and precision modifier with %s
        check_format("repr=  abc",
                     b'repr=%5s', b'abc')
        check_format("repr=ab",
                     b'repr=%.2s', b'abc')
        check_format("repr=   ab",
                     b'repr=%5.2s', b'abc')

        # test width modifier and precision modifier with %U
        check_format("repr=  abc",
                     b'repr=%5U', 'abc')
        check_format("repr=ab",
                     b'repr=%.2U', 'abc')
        check_format("repr=   ab",
                     b'repr=%5.2U', 'abc')

        # test width modifier and precision modifier with %V
        check_format("repr=  abc",
                     b'repr=%5V', 'abc', b'123')
        check_format("repr=ab",
                     b'repr=%.2V', 'abc', b'123')
        check_format("repr=   ab",
                     b'repr=%5.2V', 'abc', b'123')
        check_format("repr=  123",
                     b'repr=%5V', None, b'123')
        check_format("repr=12",
                     b'repr=%.2V', None, b'123')
        check_format("repr=   12",
                     b'repr=%5.2V', None, b'123')

        # test integer formats (%i, %d, %u)
        check_format('010',
                     b'%03i', c_int(10))
        check_format('0010',
                     b'%0.4i', c_int(10))
        check_format('-123',
                     b'%i', c_int(-123))
        check_format('-123',
                     b'%li', c_long(-123))
        check_format('-123',
                     b'%lli', c_longlong(-123))
        check_format('-123',
                     b'%zi', c_ssize_t(-123))

        check_format('-123',
                     b'%d', c_int(-123))
        check_format('-123',
                     b'%ld', c_long(-123))
        check_format('-123',
                     b'%lld', c_longlong(-123))
        check_format('-123',
                     b'%zd', c_ssize_t(-123))

        check_format('123',
                     b'%u', c_uint(123))
        check_format('123',
                     b'%lu', c_ulong(123))
        check_format('123',
                     b'%llu', c_ulonglong(123))
        check_format('123',
                     b'%zu', c_size_t(123))

        # test long output
        min_longlong = -(2 ** (8 * sizeof(c_longlong) - 1))
        max_longlong = -min_longlong - 1
        check_format(str(min_longlong),
                     b'%lld', c_longlong(min_longlong))
        check_format(str(max_longlong),
                     b'%lld', c_longlong(max_longlong))
        max_ulonglong = 2 ** (8 * sizeof(c_ulonglong)) - 1
        check_format(str(max_ulonglong),
                     b'%llu', c_ulonglong(max_ulonglong))
        PyUnicode_FromFormat(b'%p', c_void_p(-1))

        # test padding (width and/or precision)
        check_format('123'.rjust(10, '0'),
                     b'%010i', c_int(123))
        check_format('123'.rjust(100),
                     b'%100i', c_int(123))
        check_format('123'.rjust(100, '0'),
                     b'%.100i', c_int(123))
        check_format('123'.rjust(80, '0').rjust(100),
                     b'%100.80i', c_int(123))

        check_format('123'.rjust(10, '0'),
                     b'%010u', c_uint(123))
        check_format('123'.rjust(100),
                     b'%100u', c_uint(123))
        check_format('123'.rjust(100, '0'),
                     b'%.100u', c_uint(123))
        check_format('123'.rjust(80, '0').rjust(100),
                     b'%100.80u', c_uint(123))

        check_format('123'.rjust(10, '0'),
                     b'%010x', c_int(0x123))
        check_format('123'.rjust(100),
                     b'%100x', c_int(0x123))
        check_format('123'.rjust(100, '0'),
                     b'%.100x', c_int(0x123))
        check_format('123'.rjust(80, '0').rjust(100),
                     b'%100.80x', c_int(0x123))

        # test %A
        check_format(r"%A:'abc\xe9\uabcd\U0010ffff'",
                     b'%%A:%A', 'abc\xe9\uabcd\U0010ffff')

        # test %V
        check_format('repr=abc',
                     b'repr=%V', 'abc', b'xyz')

        # test %p
        # We cannot test the exact result,
        # because it returns a hex representation of a C pointer,
        # which is going to be different each time. But, we can test the format.
        p_format_regex = r'^0x[a-zA-Z0-9]{3,}$'
        p_format1 = PyUnicode_FromFormat(b'%p', 'abc')
        self.assertIsInstance(p_format1, str)
        self.assertRegex(p_format1, p_format_regex)

        p_format2 = PyUnicode_FromFormat(b'%p %p', '123456', b'xyz')
        self.assertIsInstance(p_format2, str)
        self.assertRegex(p_format2,
                         r'0x[a-zA-Z0-9]{3,} 0x[a-zA-Z0-9]{3,}')

        # Extra args are ignored:
        p_format3 = PyUnicode_FromFormat(b'%p', '123456', None, b'xyz')
        self.assertIsInstance(p_format3, str)
        self.assertRegex(p_format3, p_format_regex)

        # Test string decode from parameter of %s using utf-8.
        # b'\xe4\xba\xba\xe6\xb0\x91' is utf-8 encoded byte sequence of
        # '\u4eba\u6c11'
        check_format('repr=\u4eba\u6c11',
                     b'repr=%V', None, b'\xe4\xba\xba\xe6\xb0\x91')

        #Test replace error handler.
        check_format('repr=abc\ufffd',
                     b'repr=%V', None, b'abc\xff')

        # Issue #33817: empty strings
        check_format('',
                     b'')
        check_format('',
                     b'%s', b'')

        # check for crashes
        for fmt in (b'%', b'%0', b'%01', b'%.', b'%.1',
                    b'%0%s', b'%1%s', b'%.%s', b'%.1%s', b'%1abc',
                    b'%l', b'%ll', b'%z', b'%ls', b'%lls', b'%zs'):
            with self.subTest(fmt=fmt):
                self.assertRaisesRegex(SystemError, 'invalid format string',
                    PyUnicode_FromFormat, fmt, b'abc')
        self.assertRaisesRegex(SystemError, 'invalid format string',
            PyUnicode_FromFormat, b'%+i', c_int(10))

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_interninplace(self):
        """Test PyUnicode_InternInPlace()"""
        from _testcapi import unicode_interninplace as interninplace

        s = b'abc'.decode()
        r = interninplace(s)
        self.assertEqual(r, 'abc')

        # CRASHES interninplace(b'abc')
        # CRASHES interninplace(NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_internfromstring(self):
        """Test PyUnicode_InternFromString()"""
        from _testcapi import unicode_internfromstring as internfromstring

        self.assertEqual(internfromstring(b'abc'), 'abc')
        self.assertEqual(internfromstring(b'\xf0\x9f\x98\x80'), '\U0001f600')
        self.assertRaises(UnicodeDecodeError, internfromstring, b'\xc2')
        self.assertRaises(UnicodeDecodeError, internfromstring, b'\xa1')
        self.assertEqual(internfromstring(b''), '')

        # CRASHES internfromstring(NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_fromwidechar(self):
        """Test PyUnicode_FromWideChar()"""
        from _testcapi import unicode_fromwidechar as fromwidechar
        from _testcapi import SIZEOF_WCHAR_T

        if SIZEOF_WCHAR_T == 2:
            encoding = 'utf-16le' if sys.byteorder == 'little' else 'utf-16be'
        elif SIZEOF_WCHAR_T == 4:
            encoding = 'utf-32le' if sys.byteorder == 'little' else 'utf-32be'

        for s in '', 'abc', '\xa1\xa2', '\u4f60', '\U0001f600':
            b = s.encode(encoding)
            self.assertEqual(fromwidechar(b), s)
            self.assertEqual(fromwidechar(b + b'\0'*SIZEOF_WCHAR_T, -1), s)
        for s in '\ud83d', '\ude00':
            b = s.encode(encoding, 'surrogatepass')
            self.assertEqual(fromwidechar(b), s)
            self.assertEqual(fromwidechar(b + b'\0'*SIZEOF_WCHAR_T, -1), s)

        self.assertEqual(fromwidechar('abc'.encode(encoding), 2), 'ab')
        if SIZEOF_WCHAR_T == 2:
            self.assertEqual(fromwidechar('a\U0001f600'.encode(encoding), 2), 'a\ud83d')

        self.assertRaises(SystemError, fromwidechar, b'\0'*SIZEOF_WCHAR_T, -2)
        self.assertEqual(fromwidechar(NULL, 0), '')
        self.assertRaises(SystemError, fromwidechar, NULL, 1)
        self.assertRaises(SystemError, fromwidechar, NULL, -1)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_aswidechar(self):
        """Test PyUnicode_AsWideChar()"""
        from _testcapi import unicode_aswidechar
        from _testcapi import unicode_aswidechar_null
        from _testcapi import SIZEOF_WCHAR_T

        wchar, size = unicode_aswidechar('abcdef', 2)
        self.assertEqual(size, 2)
        self.assertEqual(wchar, 'ab')

        wchar, size = unicode_aswidechar('abc', 3)
        self.assertEqual(size, 3)
        self.assertEqual(wchar, 'abc')
        self.assertEqual(unicode_aswidechar_null('abc', 10), 4)
        self.assertEqual(unicode_aswidechar_null('abc', 0), 4)

        wchar, size = unicode_aswidechar('abc', 4)
        self.assertEqual(size, 3)
        self.assertEqual(wchar, 'abc\0')

        wchar, size = unicode_aswidechar('abc', 10)
        self.assertEqual(size, 3)
        self.assertEqual(wchar, 'abc\0')

        wchar, size = unicode_aswidechar('abc\0def', 20)
        self.assertEqual(size, 7)
        self.assertEqual(wchar, 'abc\0def\0')
        self.assertEqual(unicode_aswidechar_null('abc\0def', 20), 8)

        nonbmp = chr(0x10ffff)
        if SIZEOF_WCHAR_T == 2:
            nchar = 2
        else: # SIZEOF_WCHAR_T == 4
            nchar = 1
        wchar, size = unicode_aswidechar(nonbmp, 10)
        self.assertEqual(size, nchar)
        self.assertEqual(wchar, nonbmp + '\0')
        self.assertEqual(unicode_aswidechar_null(nonbmp, 10), nchar + 1)

        self.assertRaises(TypeError, unicode_aswidechar, b'abc', 10)
        self.assertRaises(TypeError, unicode_aswidechar, [], 10)
        self.assertRaises(SystemError, unicode_aswidechar, NULL, 10)
        self.assertRaises(TypeError, unicode_aswidechar_null, b'abc', 10)
        self.assertRaises(TypeError, unicode_aswidechar_null, [], 10)
        self.assertRaises(SystemError, unicode_aswidechar_null, NULL, 10)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_aswidecharstring(self):
        """Test PyUnicode_AsWideCharString()"""
        from _testcapi import unicode_aswidecharstring
        from _testcapi import unicode_aswidecharstring_null
        from _testcapi import SIZEOF_WCHAR_T

        wchar, size = unicode_aswidecharstring('abc')
        self.assertEqual(size, 3)
        self.assertEqual(wchar, 'abc\0')
        self.assertEqual(unicode_aswidecharstring_null('abc'), 'abc')

        wchar, size = unicode_aswidecharstring('abc\0def')
        self.assertEqual(size, 7)
        self.assertEqual(wchar, 'abc\0def\0')
        self.assertRaises(ValueError, unicode_aswidecharstring_null, 'abc\0def')

        nonbmp = chr(0x10ffff)
        if SIZEOF_WCHAR_T == 2:
            nchar = 2
        else: # SIZEOF_WCHAR_T == 4
            nchar = 1
        wchar, size = unicode_aswidecharstring(nonbmp)
        self.assertEqual(size, nchar)
        self.assertEqual(wchar, nonbmp + '\0')
        self.assertEqual(unicode_aswidecharstring_null(nonbmp), nonbmp)

        self.assertRaises(TypeError, unicode_aswidecharstring, b'abc')
        self.assertRaises(TypeError, unicode_aswidecharstring, [])
        self.assertRaises(SystemError, unicode_aswidecharstring, NULL)
        self.assertRaises(TypeError, unicode_aswidecharstring_null, b'abc')
        self.assertRaises(TypeError, unicode_aswidecharstring_null, [])
        self.assertRaises(SystemError, unicode_aswidecharstring_null, NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_asucs4(self):
        """Test PyUnicode_AsUCS4()"""
        from _testcapi import unicode_asucs4

        for s in ['abc', '\xa1\xa2', '\u4f60\u597d', 'a\U0001f600',
                  'a\ud800b\udfffc', '\ud834\udd1e']:
            l = len(s)
            self.assertEqual(unicode_asucs4(s, l, 1), s+'\0')
            self.assertEqual(unicode_asucs4(s, l, 0), s+'\uffff')
            self.assertEqual(unicode_asucs4(s, l+1, 1), s+'\0\uffff')
            self.assertEqual(unicode_asucs4(s, l+1, 0), s+'\0\uffff')
            self.assertRaises(SystemError, unicode_asucs4, s, l-1, 1)
            self.assertRaises(SystemError, unicode_asucs4, s, l-2, 0)
            s = '\0'.join([s, s])
            self.assertEqual(unicode_asucs4(s, len(s), 1), s+'\0')
            self.assertEqual(unicode_asucs4(s, len(s), 0), s+'\uffff')

        # CRASHES unicode_asucs4(b'abc', 1, 0)
        # CRASHES unicode_asucs4(b'abc', 1, 1)
        # CRASHES unicode_asucs4([], 1, 1)
        # CRASHES unicode_asucs4(NULL, 1, 0)
        # CRASHES unicode_asucs4(NULL, 1, 1)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_asucs4copy(self):
        """Test PyUnicode_AsUCS4Copy()"""
        from _testcapi import unicode_asucs4copy as asucs4copy

        for s in ['abc', '\xa1\xa2', '\u4f60\u597d', 'a\U0001f600',
                  'a\ud800b\udfffc', '\ud834\udd1e']:
            self.assertEqual(asucs4copy(s), s+'\0')
            s = '\0'.join([s, s])
            self.assertEqual(asucs4copy(s), s+'\0')

        # CRASHES asucs4copy(b'abc')
        # CRASHES asucs4copy([])
        # CRASHES asucs4copy(NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_fromordinal(self):
        """Test PyUnicode_FromOrdinal()"""
        from _testcapi import unicode_fromordinal as fromordinal

        self.assertEqual(fromordinal(0x61), 'a')
        self.assertEqual(fromordinal(0x20ac), '\u20ac')
        self.assertEqual(fromordinal(0x1f600), '\U0001f600')

        self.assertRaises(ValueError, fromordinal, 0x110000)
        self.assertRaises(ValueError, fromordinal, -1)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_asutf8(self):
        """Test PyUnicode_AsUTF8()"""
        from _testcapi import unicode_asutf8

        self.assertEqual(unicode_asutf8('abc', 4), b'abc\0')
        self.assertEqual(unicode_asutf8('абв', 7), b'\xd0\xb0\xd0\xb1\xd0\xb2\0')
        self.assertEqual(unicode_asutf8('\U0001f600', 5), b'\xf0\x9f\x98\x80\0')
        self.assertEqual(unicode_asutf8('abc\0def', 8), b'abc\0def\0')

        self.assertRaises(UnicodeEncodeError, unicode_asutf8, '\ud8ff', 0)
        self.assertRaises(TypeError, unicode_asutf8, b'abc', 0)
        self.assertRaises(TypeError, unicode_asutf8, [], 0)
        # CRASHES unicode_asutf8(NULL, 0)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_asutf8andsize(self):
        """Test PyUnicode_AsUTF8AndSize()"""
        from _testcapi import unicode_asutf8andsize
        from _testcapi import unicode_asutf8andsize_null

        self.assertEqual(unicode_asutf8andsize('abc', 4), (b'abc\0', 3))
        self.assertEqual(unicode_asutf8andsize('абв', 7), (b'\xd0\xb0\xd0\xb1\xd0\xb2\0', 6))
        self.assertEqual(unicode_asutf8andsize('\U0001f600', 5), (b'\xf0\x9f\x98\x80\0', 4))
        self.assertEqual(unicode_asutf8andsize('abc\0def', 8), (b'abc\0def\0', 7))
        self.assertEqual(unicode_asutf8andsize_null('abc', 4), b'abc\0')
        self.assertEqual(unicode_asutf8andsize_null('abc\0def', 8), b'abc\0def\0')

        self.assertRaises(UnicodeEncodeError, unicode_asutf8andsize, '\ud8ff', 0)
        self.assertRaises(TypeError, unicode_asutf8andsize, b'abc', 0)
        self.assertRaises(TypeError, unicode_asutf8andsize, [], 0)
        # CRASHES unicode_asutf8andsize(NULL, 0)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_getdefaultencoding(self):
        """Test PyUnicode_GetDefaultEncoding()"""
        from _testcapi import unicode_getdefaultencoding as getdefaultencoding

        self.assertEqual(getdefaultencoding(), b'utf-8')

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_transform_decimal_and_space(self):
        """Test _PyUnicode_TransformDecimalAndSpaceToASCII()"""
        from _testcapi import unicode_transformdecimalandspacetoascii as transform_decimal

        self.assertEqual(transform_decimal('123'),
                         '123')
        self.assertEqual(transform_decimal('\u0663.\u0661\u0664'),
                         '3.14')
        self.assertEqual(transform_decimal("\N{EM SPACE}3.14\N{EN SPACE}"),
                         " 3.14 ")
        self.assertEqual(transform_decimal('12\u20ac3'),
                         '12?')
        self.assertEqual(transform_decimal(''), '')

        self.assertRaises(SystemError, transform_decimal, b'123')
        self.assertRaises(SystemError, transform_decimal, [])
        # CRASHES transform_decimal(NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_concat(self):
        """Test PyUnicode_Concat()"""
        from _testcapi import unicode_concat as concat

        self.assertEqual(concat('abc', 'def'), 'abcdef')
        self.assertEqual(concat('abc', 'где'), 'abcгде')
        self.assertEqual(concat('абв', 'def'), 'абвdef')
        self.assertEqual(concat('абв', 'где'), 'абвгде')
        self.assertEqual(concat('a\0b', 'c\0d'), 'a\0bc\0d')

        self.assertRaises(TypeError, concat, b'abc', 'def')
        self.assertRaises(TypeError, concat, 'abc', b'def')
        self.assertRaises(TypeError, concat, b'abc', b'def')
        self.assertRaises(TypeError, concat, [], 'def')
        self.assertRaises(TypeError, concat, 'abc', [])
        self.assertRaises(TypeError, concat, [], [])
        # CRASHES concat(NULL, 'def')
        # CRASHES concat('abc', NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_split(self):
        """Test PyUnicode_Split()"""
        from _testcapi import unicode_split as split

        self.assertEqual(split('a|b|c|d', '|'), ['a', 'b', 'c', 'd'])
        self.assertEqual(split('a|b|c|d', '|', 2), ['a', 'b', 'c|d'])
        self.assertEqual(split('a|b|c|d', '\u20ac'), ['a|b|c|d'])
        self.assertEqual(split('a||b|c||d', '||'), ['a', 'b|c', 'd'])
        self.assertEqual(split('а|б|в|г', '|'), ['а', 'б', 'в', 'г'])
        self.assertEqual(split('абабагаламага', 'а'),
                         ['', 'б', 'б', 'г', 'л', 'м', 'г', ''])
        self.assertEqual(split(' a\tb\nc\rd\ve\f', NULL),
                         ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual(split('a\x85b\xa0c\u1680d\u2000e', NULL),
                         ['a', 'b', 'c', 'd', 'e'])

        self.assertRaises(ValueError, split, 'a|b|c|d', '')
        self.assertRaises(TypeError, split, 'a|b|c|d', ord('|'))
        self.assertRaises(TypeError, split, [], '|')
        # CRASHES split(NULL, '|')

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_rsplit(self):
        """Test PyUnicode_RSplit()"""
        from _testcapi import unicode_rsplit as rsplit

        self.assertEqual(rsplit('a|b|c|d', '|'), ['a', 'b', 'c', 'd'])
        self.assertEqual(rsplit('a|b|c|d', '|', 2), ['a|b', 'c', 'd'])
        self.assertEqual(rsplit('a|b|c|d', '\u20ac'), ['a|b|c|d'])
        self.assertEqual(rsplit('a||b|c||d', '||'), ['a', 'b|c', 'd'])
        self.assertEqual(rsplit('а|б|в|г', '|'), ['а', 'б', 'в', 'г'])
        self.assertEqual(rsplit('абабагаламага', 'а'),
                         ['', 'б', 'б', 'г', 'л', 'м', 'г', ''])
        self.assertEqual(rsplit('aжbжcжd', 'ж'), ['a', 'b', 'c', 'd'])
        self.assertEqual(rsplit(' a\tb\nc\rd\ve\f', NULL),
                         ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual(rsplit('a\x85b\xa0c\u1680d\u2000e', NULL),
                         ['a', 'b', 'c', 'd', 'e'])

        self.assertRaises(ValueError, rsplit, 'a|b|c|d', '')
        self.assertRaises(TypeError, rsplit, 'a|b|c|d', ord('|'))
        self.assertRaises(TypeError, rsplit, [], '|')
        # CRASHES rsplit(NULL, '|')

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_partition(self):
        """Test PyUnicode_Partition()"""
        from _testcapi import unicode_partition as partition

        self.assertEqual(partition('a|b|c', '|'), ('a', '|', 'b|c'))
        self.assertEqual(partition('a||b||c', '||'), ('a', '||', 'b||c'))
        self.assertEqual(partition('а|б|в', '|'), ('а', '|', 'б|в'))
        self.assertEqual(partition('кабан', 'а'), ('к', 'а', 'бан'))
        self.assertEqual(partition('aжbжc', 'ж'), ('a', 'ж', 'bжc'))

        self.assertRaises(ValueError, partition, 'a|b|c', '')
        self.assertRaises(TypeError, partition, b'a|b|c', '|')
        self.assertRaises(TypeError, partition, 'a|b|c', b'|')
        self.assertRaises(TypeError, partition, 'a|b|c', ord('|'))
        self.assertRaises(TypeError, partition, [], '|')
        # CRASHES partition(NULL, '|')
        # CRASHES partition('a|b|c', NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_rpartition(self):
        """Test PyUnicode_RPartition()"""
        from _testcapi import unicode_rpartition as rpartition

        self.assertEqual(rpartition('a|b|c', '|'), ('a|b', '|', 'c'))
        self.assertEqual(rpartition('a||b||c', '||'), ('a||b', '||', 'c'))
        self.assertEqual(rpartition('а|б|в', '|'), ('а|б', '|', 'в'))
        self.assertEqual(rpartition('кабан', 'а'), ('каб', 'а', 'н'))
        self.assertEqual(rpartition('aжbжc', 'ж'), ('aжb', 'ж', 'c'))

        self.assertRaises(ValueError, rpartition, 'a|b|c', '')
        self.assertRaises(TypeError, rpartition, b'a|b|c', '|')
        self.assertRaises(TypeError, rpartition, 'a|b|c', b'|')
        self.assertRaises(TypeError, rpartition, 'a|b|c', ord('|'))
        self.assertRaises(TypeError, rpartition, [], '|')
        # CRASHES rpartition(NULL, '|')
        # CRASHES rpartition('a|b|c', NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_splitlines(self):
        """Test PyUnicode_SplitLines()"""
        from _testcapi import unicode_splitlines as splitlines

        self.assertEqual(splitlines('a\nb\rc\r\nd'), ['a', 'b', 'c', 'd'])
        self.assertEqual(splitlines('a\nb\rc\r\nd', True),
                         ['a\n', 'b\r', 'c\r\n', 'd'])
        self.assertEqual(splitlines('a\x85b\u2028c\u2029d'),
                         ['a', 'b', 'c', 'd'])
        self.assertEqual(splitlines('a\x85b\u2028c\u2029d', True),
                         ['a\x85', 'b\u2028', 'c\u2029', 'd'])
        self.assertEqual(splitlines('а\nб\rв\r\nг'), ['а', 'б', 'в', 'г'])

        self.assertRaises(TypeError, splitlines, b'a\nb\rc\r\nd')
        # CRASHES splitlines(NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_translate(self):
        """Test PyUnicode_Translate()"""
        from _testcapi import unicode_translate as translate

        self.assertEqual(translate('abcd', {ord('a'): 'A', ord('b'): ord('B'), ord('c'): '<>'}), 'AB<>d')
        self.assertEqual(translate('абвг', {ord('а'): 'А', ord('б'): ord('Б'), ord('в'): '<>'}), 'АБ<>г')
        self.assertEqual(translate('abc', {}), 'abc')
        self.assertEqual(translate('abc', []), 'abc')
        self.assertRaises(UnicodeTranslateError, translate, 'abc', {ord('b'): None})
        self.assertRaises(UnicodeTranslateError, translate, 'abc', {ord('b'): None}, 'strict')
        self.assertRaises(LookupError, translate, 'abc', {ord('b'): None}, 'foo')
        self.assertEqual(translate('abc', {ord('b'): None}, 'ignore'), 'ac')
        self.assertEqual(translate('abc', {ord('b'): None}, 'replace'), 'a\ufffdc')
        self.assertEqual(translate('abc', {ord('b'): None}, 'backslashreplace'), r'a\x62c')
        # XXX Other error handlers do not support UnicodeTranslateError
        self.assertRaises(TypeError, translate, b'abc', [])
        self.assertRaises(TypeError, translate, 123, [])
        self.assertRaises(TypeError, translate, 'abc', {ord('a'): b'A'})
        self.assertRaises(TypeError, translate, 'abc', 123)
        self.assertRaises(TypeError, translate, 'abc', NULL)
        self.assertRaises(LookupError, translate, 'abc', {ord('b'): None}, 'foo')
        # CRASHES translate(NULL, [])

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_join(self):
        """Test PyUnicode_Join()"""
        from _testcapi import unicode_join as join
        self.assertEqual(join('|', ['a', 'b', 'c']), 'a|b|c')
        self.assertEqual(join('|', ['a', '', 'c']), 'a||c')
        self.assertEqual(join('', ['a', 'b', 'c']), 'abc')
        self.assertEqual(join(NULL, ['a', 'b', 'c']), 'a b c')
        self.assertEqual(join('|', ['а', 'б', 'в']), 'а|б|в')
        self.assertEqual(join('ж', ['а', 'б', 'в']), 'ажбжв')
        self.assertRaises(TypeError, join, b'|', ['a', 'b', 'c'])
        self.assertRaises(TypeError, join, '|', [b'a', b'b', b'c'])
        self.assertRaises(TypeError, join, NULL, [b'a', b'b', b'c'])
        self.assertRaises(TypeError, join, '|', b'123')
        self.assertRaises(TypeError, join, '|', 123)
        self.assertRaises(SystemError, join, '|', NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_count(self):
        """Test PyUnicode_Count()"""
        from _testcapi import unicode_count

        for str in "\xa1", "\u8000\u8080", "\ud800\udc02", "\U0001f100\U0001f1f1":
            for i, ch in enumerate(str):
                self.assertEqual(unicode_count(str, ch, 0, len(str)), 1)

        str = "!>_<!"
        self.assertEqual(unicode_count(str, 'z', 0, len(str)), 0)
        self.assertEqual(unicode_count(str, '', 0, len(str)), len(str)+1)
        # start < end
        self.assertEqual(unicode_count(str, '!', 1, len(str)+1), 1)
        # start >= end
        self.assertEqual(unicode_count(str, '!', 0, 0), 0)
        self.assertEqual(unicode_count(str, '!', len(str), 0), 0)
        # negative
        self.assertEqual(unicode_count(str, '!', -len(str), -1), 1)
        # bad arguments
        self.assertRaises(TypeError, unicode_count, str, b'!', 0, len(str))
        self.assertRaises(TypeError, unicode_count, b"!>_<!", '!', 0, len(str))
        self.assertRaises(TypeError, unicode_count, str, ord('!'), 0, len(str))
        self.assertRaises(TypeError, unicode_count, [], '!', 0, len(str), 1)
        # CRASHES unicode_count(NULL, '!', 0, len(str))
        # CRASHES unicode_count(str, NULL, 0, len(str))

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_tailmatch(self):
        """Test PyUnicode_Tailmatch()"""
        from _testcapi import unicode_tailmatch as tailmatch

        str = 'ababahalamaha'
        self.assertEqual(tailmatch(str, 'aba', 0, len(str), -1), 1)
        self.assertEqual(tailmatch(str, 'aha', 0, len(str), 1), 1)

        self.assertEqual(tailmatch(str, 'aba', 0, sys.maxsize, -1), 1)
        self.assertEqual(tailmatch(str, 'aba', -len(str), sys.maxsize, -1), 1)
        self.assertEqual(tailmatch(str, 'aba', -sys.maxsize-1, len(str), -1), 1)
        self.assertEqual(tailmatch(str, 'aha', 0, sys.maxsize, 1), 1)
        self.assertEqual(tailmatch(str, 'aha', -sys.maxsize-1, len(str), 1), 1)

        self.assertEqual(tailmatch(str, 'z', 0, len(str), 1), 0)
        self.assertEqual(tailmatch(str, 'z', 0, len(str), -1), 0)
        self.assertEqual(tailmatch(str, '', 0, len(str), 1), 1)
        self.assertEqual(tailmatch(str, '', 0, len(str), -1), 1)

        self.assertEqual(tailmatch(str, 'ba', 0, len(str)-1, -1), 0)
        self.assertEqual(tailmatch(str, 'ba', 1, len(str)-1, -1), 1)
        self.assertEqual(tailmatch(str, 'aba', 1, len(str)-1, -1), 0)
        self.assertEqual(tailmatch(str, 'ba', -len(str)+1, -1, -1), 1)
        self.assertEqual(tailmatch(str, 'ah', 0, len(str), 1), 0)
        self.assertEqual(tailmatch(str, 'ah', 0, len(str)-1, 1), 1)
        self.assertEqual(tailmatch(str, 'ah', -len(str), -1, 1), 1)

        # bad arguments
        self.assertRaises(TypeError, tailmatch, str, ('aba', 'aha'), 0, len(str), -1)
        self.assertRaises(TypeError, tailmatch, str, ('aba', 'aha'), 0, len(str), 1)
        # CRASHES tailmatch(NULL, 'aba', 0, len(str), -1)
        # CRASHES tailmatch(str, NULL, 0, len(str), -1)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_find(self):
        """Test PyUnicode_Find()"""
        from _testcapi import unicode_find as find

        for str in "\xa1", "\u8000\u8080", "\ud800\udc02", "\U0001f100\U0001f1f1":
            for i, ch in enumerate(str):
                self.assertEqual(find(str, ch, 0, len(str), 1), i)
                self.assertEqual(find(str, ch, 0, len(str), -1), i)

        str = "!>_<!"
        self.assertEqual(find(str, 'z', 0, len(str), 1), -1)
        self.assertEqual(find(str, 'z', 0, len(str), -1), -1)
        self.assertEqual(find(str, '', 0, len(str), 1), 0)
        self.assertEqual(find(str, '', 0, len(str), -1), len(str))
        # start < end
        self.assertEqual(find(str, '!', 1, len(str)+1, 1), 4)
        self.assertEqual(find(str, '!', 1, len(str)+1, -1), 4)
        # start >= end
        self.assertEqual(find(str, '!', 0, 0, 1), -1)
        self.assertEqual(find(str, '!', len(str), 0, 1), -1)
        # negative
        self.assertEqual(find(str, '!', -len(str), -1, 1), 0)
        self.assertEqual(find(str, '!', -len(str), -1, -1), 0)
        # bad arguments
        self.assertRaises(TypeError, find, str, b'!', 0, len(str), 1)
        self.assertRaises(TypeError, find, b"!>_<!", '!', 0, len(str), 1)
        self.assertRaises(TypeError, find, str, ord('!'), 0, len(str), 1)
        self.assertRaises(TypeError, find, [], '!', 0, len(str), 1)
        # CRASHES find(NULL, '!', 0, len(str), 1)
        # CRASHES find(str, NULL, 0, len(str), 1)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_findchar(self):
        """Test PyUnicode_FindChar()"""
        from _testcapi import unicode_findchar

        for str in "\xa1", "\u8000\u8080", "\ud800\udc02", "\U0001f100\U0001f1f1":
            for i, ch in enumerate(str):
                self.assertEqual(unicode_findchar(str, ord(ch), 0, len(str), 1), i)
                self.assertEqual(unicode_findchar(str, ord(ch), 0, len(str), -1), i)

        str = "!>_<!"
        self.assertEqual(unicode_findchar(str, 0x110000, 0, len(str), 1), -1)
        self.assertEqual(unicode_findchar(str, 0x110000, 0, len(str), -1), -1)
        # start < end
        self.assertEqual(unicode_findchar(str, ord('!'), 1, len(str)+1, 1), 4)
        self.assertEqual(unicode_findchar(str, ord('!'), 1, len(str)+1, -1), 4)
        # start >= end
        self.assertEqual(unicode_findchar(str, ord('!'), 0, 0, 1), -1)
        self.assertEqual(unicode_findchar(str, ord('!'), len(str), 0, 1), -1)
        # negative
        self.assertEqual(unicode_findchar(str, ord('!'), -len(str), -1, 1), 0)
        self.assertEqual(unicode_findchar(str, ord('!'), -len(str), -1, -1), 0)
        # bad arguments
        # CRASHES unicode_findchar(b"!>_<!", ord('!'), 0, len(str), 1)
        # CRASHES unicode_findchar([], ord('!'), 0, len(str), 1)
        # CRASHES unicode_findchar(NULL, ord('!'), 0, len(str), 1), 1)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_replace(self):
        """Test PyUnicode_Replace()"""
        from _testcapi import unicode_replace as replace

        str = 'abracadabra'
        self.assertEqual(replace(str, 'a', '='), '=br=c=d=br=')
        self.assertEqual(replace(str, 'a', '<>'), '<>br<>c<>d<>br<>')
        self.assertEqual(replace(str, 'abra', '='), '=cad=')
        self.assertEqual(replace(str, 'a', '=', 2), '=br=cadabra')
        self.assertEqual(replace(str, 'a', '=', 0), str)
        self.assertEqual(replace(str, 'a', '=', sys.maxsize), '=br=c=d=br=')
        self.assertEqual(replace(str, 'z', '='), str)
        self.assertEqual(replace(str, '', '='), '=a=b=r=a=c=a=d=a=b=r=a=')
        self.assertEqual(replace(str, 'a', 'ж'), 'жbrжcжdжbrж')
        self.assertEqual(replace('абабагаламага', 'а', '='), '=б=б=г=л=м=г=')
        self.assertEqual(replace('Баден-Баден', 'Баден', 'Baden'), 'Baden-Baden')
        # bad arguments
        self.assertRaises(TypeError, replace, 'a', 'a', b'=')
        self.assertRaises(TypeError, replace, 'a', b'a', '=')
        self.assertRaises(TypeError, replace, b'a', 'a', '=')
        self.assertRaises(TypeError, replace, 'a', 'a', ord('='))
        self.assertRaises(TypeError, replace, 'a', ord('a'), '=')
        self.assertRaises(TypeError, replace, [], 'a', '=')
        # CRASHES replace('a', 'a', NULL)
        # CRASHES replace('a', NULL, '=')
        # CRASHES replace(NULL, 'a', '=')

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_compare(self):
        """Test PyUnicode_Compare()"""
        from _testcapi import unicode_compare as compare

        self.assertEqual(compare('abc', 'abc'), 0)
        self.assertEqual(compare('abc', 'def'), -1)
        self.assertEqual(compare('def', 'abc'), 1)
        self.assertEqual(compare('abc', 'abc\0def'), -1)
        self.assertEqual(compare('abc\0def', 'abc\0def'), 0)
        self.assertEqual(compare('абв', 'abc'), 1)

        self.assertRaises(TypeError, compare, b'abc', 'abc')
        self.assertRaises(TypeError, compare, 'abc', b'abc')
        self.assertRaises(TypeError, compare, b'abc', b'abc')
        self.assertRaises(TypeError, compare, [], 'abc')
        self.assertRaises(TypeError, compare, 'abc', [])
        self.assertRaises(TypeError, compare, [], [])
        # CRASHES compare(NULL, 'abc')
        # CRASHES compare('abc', NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_comparewithasciistring(self):
        """Test PyUnicode_CompareWithASCIIString()"""
        from _testcapi import unicode_comparewithasciistring as comparewithasciistring

        self.assertEqual(comparewithasciistring('abc', b'abc'), 0)
        self.assertEqual(comparewithasciistring('abc', b'def'), -1)
        self.assertEqual(comparewithasciistring('def', b'abc'), 1)
        self.assertEqual(comparewithasciistring('abc', b'abc\0def'), 0)
        self.assertEqual(comparewithasciistring('abc\0def', b'abc\0def'), 1)
        self.assertEqual(comparewithasciistring('абв', b'abc'), 1)

        # CRASHES comparewithasciistring(b'abc', b'abc')
        # CRASHES comparewithasciistring([], b'abc')
        # CRASHES comparewithasciistring(NULL, b'abc')

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_richcompare(self):
        """Test PyUnicode_RichCompare()"""
        from _testcapi import unicode_richcompare as richcompare

        LT, LE, EQ, NE, GT, GE = range(6)
        strings = ('abc', 'абв', '\U0001f600', 'abc\0')
        for s1 in strings:
            for s2 in strings:
                self.assertIs(richcompare(s1, s2, LT), s1 < s2)
                self.assertIs(richcompare(s1, s2, LE), s1 <= s2)
                self.assertIs(richcompare(s1, s2, EQ), s1 == s2)
                self.assertIs(richcompare(s1, s2, NE), s1 != s2)
                self.assertIs(richcompare(s1, s2, GT), s1 > s2)
                self.assertIs(richcompare(s1, s2, GE), s1 >= s2)

        for op in LT, LE, EQ, NE, GT, GE:
            self.assertIs(richcompare(b'abc', 'abc', op), NotImplemented)
            self.assertIs(richcompare('abc', b'abc', op), NotImplemented)
            self.assertIs(richcompare(b'abc', b'abc', op), NotImplemented)
            self.assertIs(richcompare([], 'abc', op), NotImplemented)
            self.assertIs(richcompare('abc', [], op), NotImplemented)
            self.assertIs(richcompare([], [], op), NotImplemented)

            # CRASHES richcompare(NULL, 'abc', op)
            # CRASHES richcompare('abc', NULL, op)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_format(self):
        """Test PyUnicode_Format()"""
        from _testcapi import unicode_format as format

        self.assertEqual(format('x=%d!', 42), 'x=42!')
        self.assertEqual(format('x=%d!', (42,)), 'x=42!')
        self.assertEqual(format('x=%d y=%s!', (42, [])), 'x=42 y=[]!')

        self.assertRaises(SystemError, format, 'x=%d!', NULL)
        self.assertRaises(SystemError, format, NULL, 42)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_contains(self):
        """Test PyUnicode_Contains()"""
        from _testcapi import unicode_contains as contains

        self.assertEqual(contains('abcd', ''), 1)
        self.assertEqual(contains('abcd', 'b'), 1)
        self.assertEqual(contains('abcd', 'x'), 0)
        self.assertEqual(contains('abcd', 'ж'), 0)
        self.assertEqual(contains('abcd', '\0'), 0)
        self.assertEqual(contains('abc\0def', '\0'), 1)
        self.assertEqual(contains('abcd', 'bc'), 1)

        self.assertRaises(TypeError, contains, b'abcd', 'b')
        self.assertRaises(TypeError, contains, 'abcd', b'b')
        self.assertRaises(TypeError, contains, b'abcd', b'b')
        self.assertRaises(TypeError, contains, [], 'b')
        self.assertRaises(TypeError, contains, 'abcd', ord('b'))
        # CRASHES contains(NULL, 'b')
        # CRASHES contains('abcd', NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_isidentifier(self):
        """Test PyUnicode_IsIdentifier()"""
        from _testcapi import unicode_isidentifier as isidentifier

        self.assertEqual(isidentifier("a"), 1)
        self.assertEqual(isidentifier("b0"), 1)
        self.assertEqual(isidentifier("µ"), 1)
        self.assertEqual(isidentifier("𝔘𝔫𝔦𝔠𝔬𝔡𝔢"), 1)

        self.assertEqual(isidentifier(""), 0)
        self.assertEqual(isidentifier(" "), 0)
        self.assertEqual(isidentifier("["), 0)
        self.assertEqual(isidentifier("©"), 0)
        self.assertEqual(isidentifier("0"), 0)
        self.assertEqual(isidentifier("32M"), 0)

        # CRASHES isidentifier(b"a")
        # CRASHES isidentifier([])
        # CRASHES isidentifier(NULL)

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_copycharacters(self):
        """Test PyUnicode_CopyCharacters()"""
        from _testcapi import unicode_copycharacters

        strings = [
            # all strings have exactly 5 characters
            'abcde', '\xa1\xa2\xa3\xa4\xa5',
            '\u4f60\u597d\u4e16\u754c\uff01',
            '\U0001f600\U0001f601\U0001f602\U0001f603\U0001f604'
        ]

        for idx, from_ in enumerate(strings):
            # wide -> narrow: exceed maxchar limitation
            for to in strings[:idx]:
                self.assertRaises(
                    SystemError,
                    unicode_copycharacters, to, 0, from_, 0, 5
                )
            # same kind
            for from_start in range(5):
                self.assertEqual(
                    unicode_copycharacters(from_, 0, from_, from_start, 5),
                    (from_[from_start:from_start+5].ljust(5, '\0'),
                     5-from_start)
                )
            for to_start in range(5):
                self.assertEqual(
                    unicode_copycharacters(from_, to_start, from_, to_start, 5),
                    (from_[to_start:to_start+5].rjust(5, '\0'),
                     5-to_start)
                )
            # narrow -> wide
            # Tests omitted since this creates invalid strings.

        s = strings[0]
        self.assertRaises(IndexError, unicode_copycharacters, s, 6, s, 0, 5)
        self.assertRaises(IndexError, unicode_copycharacters, s, -1, s, 0, 5)
        self.assertRaises(IndexError, unicode_copycharacters, s, 0, s, 6, 5)
        self.assertRaises(IndexError, unicode_copycharacters, s, 0, s, -1, 5)
        self.assertRaises(SystemError, unicode_copycharacters, s, 1, s, 0, 5)
        self.assertRaises(SystemError, unicode_copycharacters, s, 0, s, 0, -1)
        self.assertRaises(SystemError, unicode_copycharacters, s, 0, b'', 0, 0)
        self.assertRaises(SystemError, unicode_copycharacters, s, 0, [], 0, 0)
        # CRASHES unicode_copycharacters(s, 0, NULL, 0, 0)
        # TODO: Test PyUnicode_CopyCharacters() with non-unicode and
        # non-modifiable unicode as "to".

    @support.cpython_only
    @unittest.skipIf(_testcapi is None, 'need _testcapi module')
    def test_pep393_utf8_caching_bug(self):
        # Issue #25709: Problem with string concatenation and utf-8 cache
        from _testcapi import getargs_s_hash
        for k in 0x24, 0xa4, 0x20ac, 0x1f40d:
            s = ''
            for i in range(5):
                # Due to CPython specific optimization the 's' string can be
                # resized in-place.
                s += chr(k)
                # Parsing with the "s#" format code calls indirectly
                # PyUnicode_AsUTF8AndSize() which creates the UTF-8
                # encoded string cached in the Unicode object.
                self.assertEqual(getargs_s_hash(s), chr(k).encode() * (i + 1))
                # Check that the second call returns the same result
                self.assertEqual(getargs_s_hash(s), chr(k).encode() * (i + 1))


if __name__ == "__main__":
    unittest.main()