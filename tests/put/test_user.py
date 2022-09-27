import unittest
from mock import Mock

from trashcli.put.user import User, user_replied_no, user_replied_yes, \
    parse_user_reply


class TestUser(unittest.TestCase):
    def setUp(self):
        self.my_input = Mock()
        self.my_input.return_value = "y"
        self.user = User(self.my_input)

    def test_yes(self):
        result = self.user.ask_user_about_deleting_file('prg', "file")

        assert result == 'user_replied_yes'


class Test_parse_user_reply(unittest.TestCase):
    def test_y(self): assert parse_user_reply('y') == user_replied_yes
    def test_Y(self): assert parse_user_reply('Y') == user_replied_yes
    def test_n(self): assert parse_user_reply('n') == user_replied_no
    def test_N(self): assert parse_user_reply('N') == user_replied_no
    def test_other(self): assert parse_user_reply('other') == user_replied_no
