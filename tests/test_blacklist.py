from unittest import TestCase
from mock import patch, Mock
from mockredis import mock_strict_redis_client
from models.blacklist import Blacklist


class TestBlacklist(TestCase):

    def setUp(self):
        self.client = mock_strict_redis_client()
        self.encoder = Mock()
        self.encoder.encode = self.reverse_string
        self.blacklist = Blacklist(self.client, self.encoder)
        self.poll_texts_key_name = "blacklist:poll_texts:231"
        self.poll_contacts_key_name = "blacklist:poll_contacts:231"

    def reverse_string(self, text):
        return text[::-1]

    def test_that_poll_text_can_be_black_listed(self):
        self.blacklist.poll_text(231, "sample text")
        self.assertTrue(self.client.sismember(self.poll_texts_key_name, self.reverse_string("sample text")))

    def test_that_an_array_of_poll_texts_can_be_black_listed(self):
        self.blacklist.poll_text(231, ["sample 1", "sample 2", "sample 3"])
        self.assertTrue(self.client.sismember(self.poll_texts_key_name, self.reverse_string("sample 1")))
        self.assertTrue(self.client.sismember(self.poll_texts_key_name, self.reverse_string("sample 2")))
        self.assertTrue(self.client.sismember(self.poll_texts_key_name, self.reverse_string("sample 3")))

        self.assertFalse(self.client.sismember(self.poll_texts_key_name, self.reverse_string("sample 4")))

    def test_that_only_inserted_text_exist(self):
        self.blacklist.poll_text(231, "valid text")

        self.assertFalse(self.blacklist.has_poll_text(231, "invalid text"))
        self.assertTrue(self.blacklist.has_poll_text(231, "valid text"))

    def test_that_poll_text_can_be_deleted(self):
        text_to_delete = "text to delete"

        self.blacklist.poll_text(231, text_to_delete)
        self.blacklist.poll_text(231, "text not to delete")
        self.assertTrue(self.blacklist.has_poll_text(231, text_to_delete))

        self.blacklist.delete_poll_text(231, text_to_delete)
        self.assertFalse(self.blacklist.has_poll_text(231, text_to_delete))

        self.assertTrue(self.blacklist.has_poll_text(231, "text not to delete"))

    def test_that_poll_contacts_can_be_black_listed(self):
        ones = "1111111"
        twos = "2222222"
        threes = "33333"

        self.blacklist.poll_contacts(231, [ones, twos])

        self.assertTrue(self.client.sismember(self.poll_contacts_key_name, ones))
        self.assertTrue(self.client.sismember(self.poll_contacts_key_name, twos))
        self.assertFalse(self.client.sismember(self.poll_contacts_key_name, threes))

    def test_that_inserted_poll_contact_exists(self):
        ones = "1111111"
        self.blacklist.poll_contacts(231, ones)
        self.assertTrue(self.blacklist.has_poll_contact(231, ones))

    def test_that_poll_contacts_can_be_deleted(self):
        ones = "1111111"
        twos = "2222222"
        threes = "33333"

        self.blacklist.poll_contacts(231, [ones, twos, threes])
        self.assertTrue(self.blacklist.has_poll_contact(231, ones))
        self.assertTrue(self.blacklist.has_poll_contact(231, twos))
        self.assertTrue(self.blacklist.has_poll_contact(231, threes))

        self.blacklist.delete_poll_contacts(231, [twos,threes])

        self.assertTrue(self.blacklist.has_poll_contact(231, ones))

        self.assertFalse(self.blacklist.has_poll_contact(231, twos))
        self.assertFalse(self.blacklist.has_poll_contact(231, threes))

