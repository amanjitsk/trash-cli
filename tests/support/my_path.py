import os
import shutil
import tempfile

from mock import Mock

from trashcli.fstab import Volumes


def volumes_mock(func = lambda x: "volume_of %s" % x):
    volumes = Mock(spec=Volumes)
    volumes.volume_of = func
    return volumes


def remove_dir_if_exists(dir):
    if os.path.exists(dir):
        os.rmdir(dir)


class MyPath(str):

    def __truediv__(self, other_path):
        return self.path_join(other_path)

    def __div__(self, other_path):
        return self.path_join(other_path)

    def path_join(self, other_path):
        return MyPath(os.path.join(self, other_path))

    def clean_up(self):
        shutil.rmtree(self)

    @classmethod
    def make_temp_dir(cls):
        return cls(os.path.realpath(tempfile.mkdtemp(suffix="_trash_cli_test")))
