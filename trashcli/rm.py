import fnmatch
import os, sys

from trashcli.trash import TrashDir, parse_path, ParseError
from trashcli.trash import TrashDirsScanner
from trashcli.trash import TopTrashDirRules
from trashcli.empty import CleanableTrashcan
from trashcli.fs import FileSystemReader
from trashcli.fs import FileRemover

class RmCmd:
    def __init__(self,
                 environ,
                 getuid,
                 list_volumes,
                 stderr,
                 file_reader):
        self.environ      = environ
        self.getuid       = getuid
        self.list_volumes = list_volumes
        self.stderr       = stderr
        self.file_reader  = file_reader
    def run(self, argv):
        args = argv[1:]
        self.exit_code = 0

        if not args:
            self.print_err('Usage:\n'
                           '    trash-rm PATTERN\n'
                           '\n'
                           'Please specify PATTERN')
            self.exit_code = 8
            return

        trashcan = CleanableTrashcan(FileRemover())
        pattern = args[0]
        cmd = Filter(trashcan.delete_trashinfo_and_backup_copy, pattern)

        listing = ListTrashinfos(self.file_reader)

        scanner = TrashDirsScanner(self.environ,
                                   self.getuid,
                                   self.list_volumes,
                                   TopTrashDirRules(self.file_reader))

        for event, args in scanner.scan_trash_dirs():
            if event == TrashDirsScanner.Found:
                path, volume = args
                for type, arg in listing.list_from_volume_trashdir(path, volume):
                    if type == 'unable_to_parse_path':
                        self.unable_to_parse_path(arg)
                    elif type == 'trashed_file':
                        cmd.delete_if_matches(arg)

    def unable_to_parse_path(self, trashinfo):
        self.report_error('{}: unable to parse \'Path\''.format(trashinfo))

    def report_error(self, error_msg):
        self.print_err('trash-rm: {}'.format(error_msg))

    def print_err(self, msg):
        self.stderr.write(msg + '\n')


def main():
    from trashcli.list_mount_points import os_mount_points
    cmd = RmCmd(environ        = os.environ
                , getuid       = os.getuid
                , list_volumes = os_mount_points
                , stderr       = sys.stderr
                , file_reader  = FileSystemReader())

    cmd.run(sys.argv)

    return cmd.exit_code

class Filter:
    def __init__(self, delete, pattern):
        self.delete = delete
        self.pattern = pattern

    def delete_if_matches(self, trashed_file):
        original_location, info_file = trashed_file
        if self.pattern[0] == '/':
            if self.pattern == original_location:
                self.delete(info_file)
        else:
            basename = os.path.basename(original_location)
            if fnmatch.fnmatchcase(basename, self.pattern):
                self.delete(info_file)


class ListTrashinfos:
    def __init__(self, file_reader):
        self.file_reader = file_reader

    def list_from_volume_trashdir(self, trashdir_path, volume):
        trashdir = TrashDir(self.file_reader)
        trashdir.open(trashdir_path, volume)
        for trashinfo_path in trashdir.list_trashinfo():
            trashinfo = self.file_reader.contents_of(trashinfo_path)
            try:
                path = parse_path(trashinfo)
            except ParseError:
                yield 'unable_to_parse_path', trashinfo_path
            else:
                complete_path = os.path.join(volume, path)
                yield 'trashed_file', (complete_path, trashinfo_path)
