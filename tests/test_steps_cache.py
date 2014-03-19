from unittest import TestCase
from mock import patch, Mock, MagicMock
from mockredis import mock_strict_redis_client
from models.caching_steps import StepsCache


def md5_mock():
    md5 = Mock()
    md5.update = Mock()
    md5.digest = Mock(return_value='encrypted_value')
    return md5

def encode_mock(encode_values):
    def side_effect(args):
        return encode_values[args]
    mock = MagicMock(side_effect=side_effect)
    return mock


class TestStepsCache(TestCase):

    def setUp(self):
        self.cache = StepsCache("username", "password")

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_that_data_from_api_is_stored(self):

        key_name = "my script"
        first_value = "step 1 1"
        second_value = "step 1 2"
        data = [first_value, second_value]
        encoded_data = {first_value: "encrypted_first_value", second_value: "encrypted_second_value"}
        self.cache.key_name = Mock(return_value=key_name)
        self.cache.get_steps_information = Mock(return_value=data)
        self.cache.encode = encode_mock(encoded_data)

        client = self.cache.get_redis_client()
        self.cache.add_script_steps_data(client)

        self.assertTrue(client.sismember(key_name, "encrypted_first_value"))
        self.assertTrue(client.sismember(key_name, "encrypted_second_value"))

    @patch('hashlib.md5', md5_mock)
    def test_that_encode_text_using_md5(self):
        text = "important text"
        encoded_text = self.cache.encode(text)
        self.assertEquals(encoded_text, 'encrypted_value')

    def test_that_script_step_data_gets_deleted(self):
        client = self.cache.get_redis_client()
        script_name = 'my_script'
        first_step = 'step 1 1'
        client.sadd(script_name, first_step)
        self.cache.key_name = Mock(return_value=script_name)
        self.cache.delete_script_steps_data(client)

        self.assertFalse(client.exists(script_name))

    def test_that_key_name_is_ureport(self):
        self.assertEquals(self.cache.key_name(), "ureport-registration-steps")

    @patch('base64.encodestring')
    @patch('urllib2.Request')
    @patch('urllib2.urlopen')
    def test_authorized_response(self, urlopen_mock, request_class_mock, encoded_str_mock):
        request_mock = Mock()
        add_header = Mock()
        request_mock.add_header = add_header
        request_class_mock.return_value = request_mock
        fake_response = "response"
        urlopen_mock.return_value = fake_response
        auth_data = "user:passwd"
        encoded_str_mock.return_value = auth_data

        self.assertEquals(self.cache.get_authorized_response("my_http_address"), fake_response)
        urlopen_mock.assert_called_once_with(request_mock)
        request_mock.add_header.assert_called_once_with('Authorization', 'Basic %s' % auth_data)