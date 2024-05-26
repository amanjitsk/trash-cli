import unittest


def assert_equals_with_unidiff(expected, actual):
    def unidiff(expected, actual):
        import difflib
        expected = expected.splitlines(1)
        actual = actual.splitlines(1)

        diff = difflib.unified_diff(expected, actual,
                                    fromfile='Expected', tofile='Actual',
                                    lineterm='\n', n=10)

        return ''.join(diff)

    assert expected == actual, ("\n"
                                "Expected:%s\n" % repr(expected) +
                                "  Actual:%s\n" % repr(actual) +
                                unidiff(expected, actual))


def assert_starts_with(actual, expected):
    class Dummy(unittest.TestCase):
        def nop(self):
            pass

    _t = Dummy('nop')
    _t.assertEqual(actual[:len(expected)], expected)
