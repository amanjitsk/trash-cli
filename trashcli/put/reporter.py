# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import re
from pwd import getpwuid

from grp import getgrgid
from typing import List, NamedTuple
from trashcli.lib.environ import Environ

from trashcli.put.candidate import Candidate
from trashcli.put.core.failure_reason import FailureReason, Level, LogContext
from trashcli.put.core.trash_all_result import TrashAllResult
from trashcli.put.describer import Describer
from trashcli.put.my_logger import MyLogger, LogData
from trashcli.lib.exit_codes import EX_OK, EX_IOERR
from trashcli.put.trashee import Trashee


class TrashPutReporter:
    def __init__(self,
                 logger,  # type: MyLogger
                 describer,  # type: Describer
                 ):
        self.logger = logger
        self.describer = describer

    def _describe(self, path):
        return self.describer.describe(path)

    def unable_to_trash_dot_entries(self, file, program_name):
        self.logger.warning2(
            "cannot trash %s '%s'" % (self._describe(file), file),
            program_name)

    def unable_to_trash_file(self, f, log_data):
        self.logger.warning2("cannot trash %s '%s'" % (self._describe(f), f),
                             log_data.program_name)

    def file_has_been_trashed_in_as(self,
                                    trashed_file,
                                    trash_dir,  # type: Candidate
                                    log_data,  # type: LogData
                                    environ):
        trash_dir_path = trash_dir.shrink_user(environ)
        self.logger.info("'%s' trashed in %s" % (trashed_file, trash_dir_path),
                         log_data)

    def log_info_messages(self,
                          messages,  # type: List[str]
                          log_data,  # type: LogData
                          ):
        for message in messages:
            self.logger.info(message, log_data)

    @classmethod
    def log_data_for_debugging(cls, error):
        try:
            filename = error.filename
        except AttributeError:
            pass
        else:
            if filename is not None:
                for path in [filename, os.path.dirname(filename)]:
                    info = gentle_stat_read(path)
                    yield "stats for %s: %s" % (path, info)

    def trash_dir_with_volume(self,
                              candidate,  # type: Candidate
                              log_data,  # type: LogData
                              ):
        # type: (...) -> None
        self.logger.info(
            "trying trash dir: %s from volume: %s" % (candidate.norm_path(),
                                                      candidate.volume),
            log_data)

    def exit_code(self,
                  result,  # type: TrashAllResult
                  ):  # type: (...) -> int
        if not result.any_failure():
            return EX_OK
        else:
            return EX_IOERR

    def volume_of_file(self, volume, log_data):
        self.logger.info("volume of file: %s" % volume, log_data)

    def report_reason(self,
                      reason,  # type: FailureReason
                      log_data,  # type: LogData
                      environ,  # type: Environ
                      trashee,  # type: Trashee
                      candidate,  # type: Candidate
                      ):  # type: (...) -> None
        for entry in reason.log_entries(
            LogContext(trashee.path,
                       candidate.shrink_user(environ),
                       )
        ):
            if entry.level == Level.INFO:
                self.logger.info(entry.message, log_data)
            else:
                raise ValueError("unknown level: %s" % entry.level)


def gentle_stat_read(path):
    try:
        stats = os.lstat(path)
        user = getpwuid(stats.st_uid).pw_name
        group = getgrgid(stats.st_gid).gr_name
        perms = remove_octal_prefix(oct(stats.st_mode & 0o777))
        return "%s %s %s" % (perms, user, group)
    except OSError as e:
        return str(e)


def remove_octal_prefix(s):
    remove_new_octal_format = s.replace('0o', '')
    remove_old_octal_format = re.sub(r"^0", '', remove_new_octal_format)
    return remove_old_octal_format
