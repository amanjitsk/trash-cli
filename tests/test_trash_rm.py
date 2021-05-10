import unittest

import six

from mock import Mock, call

from trashcli.rm import Filter
from six import StringIO


class TestTrashRmCmdRun(unittest.TestCase):
    def test_without_arguments(self):
        from trashcli.rm import RmCmd
        cmd = RmCmd(None, None, None, None, None)
        cmd.stderr = StringIO()
        cmd.run([None])

        assert ('Usage:\n    trash-rm PATTERN\n\nPlease specify PATTERN\n' ==
                     cmd.stderr.getvalue())

    def test_without_pattern_argument(self):
        from trashcli.rm import RmCmd
        cmd = RmCmd(None, None, None, None, None)
        cmd.stderr = StringIO()
        cmd.file_reader = Mock([])
        cmd.file_reader.exists = Mock([], return_value = None)
        cmd.file_reader.entries_if_dir_exists = Mock([], return_value = [])
        cmd.environ = {}
        cmd.getuid = lambda : '111'
        cmd.list_volumes = lambda: ['/vol1']

        cmd.run([None, None])

        assert '' == cmd.stderr.getvalue()


class TestTrashRmCmd(unittest.TestCase):

    def setUp(self):
        self.deleted = []

    def test_a_star_matches_all(self):
        self.cmd = Filter(self.deleted.append, '*')

        self.cmd.delete_if_matches(('/foo', 'info/foo'))
        self.cmd.delete_if_matches(('/bar', 'info/bar'))

        six.assertCountEqual(self, [
            'info/foo',
            'info/bar',
        ], self.deleted)

    def test_basename_matches(self):
        self.cmd = Filter(self.deleted.append, 'foo')

        self.cmd.delete_if_matches(('/foo', 'info/foo')),
        self.cmd.delete_if_matches(('/bar', 'info/bar'))

        six.assertCountEqual(self, [
            'info/foo',
        ], self.deleted)

    def test_example_with_star_dot_o(self):
        self.cmd = Filter(self.deleted.append, '*.o')

        self.cmd.delete_if_matches(('/foo.h', 'info/foo.h')),
        self.cmd.delete_if_matches(('/foo.c', 'info/foo.c')),
        self.cmd.delete_if_matches(('/foo.o', 'info/foo.o')),
        self.cmd.delete_if_matches(('/bar.o', 'info/bar.o'))

        six.assertCountEqual(self, [
            'info/foo.o',
            'info/bar.o',
        ], self.deleted)

    def test_absolute_pattern(self):
        self.cmd = Filter(self.deleted.append, '/foo/bar.baz')

        self.cmd.delete_if_matches(('/foo/bar.baz', '1')),
        self.cmd.delete_if_matches(('/foo/bar', '2')),

        six.assertCountEqual(self, [
            '1',
        ], self.deleted)
