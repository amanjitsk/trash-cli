from trashcli.empty.older_than import older_than
from trashcli.trash import parse_deletion_date, Clock


class ContentReader:
    def contents_of(self, path):
        raise NotImplementedError


class DeleteAccordingDate:
    def __init__(self, reader, clock):  # type: (ContentReader, Clock) -> None
        self.reader = reader
        self.clock = clock

    def ok_to_delete(self, trashinfo_path, environ, parsed_days):
        if parsed_days is None:
            return True
        else:
            contents = self.reader.contents_of(trashinfo_path)
            now_value = self.clock.get_now_value(environ)
            deletion_date = parse_deletion_date(contents)
            if deletion_date is not None:
                if older_than(parsed_days, now_value, deletion_date):
                    return True
            return False
