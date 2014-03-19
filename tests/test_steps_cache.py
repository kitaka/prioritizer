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

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_that_data_from_api_is_stored(self):
        cache = StepsCache()
        key_name = "my script"
        first_value = "step 1 1"
        second_value = "step 1 2"
        data = [first_value, second_value]
        encoded_data = {first_value: "encrypted_first_value", second_value: "encrypted_second_value"}
        cache.key_name = Mock(return_value=key_name)
        cache.get_steps_information = Mock(return_value=data)
        cache.encode = encode_mock(encoded_data)

        client = cache.get_redis_client()
        cache.add_script_steps_data(client)

        self.assertTrue(client.sismember(key_name, "encrypted_first_value"))
        self.assertTrue(client.sismember(key_name, "encrypted_second_value"))

    @patch('hashlib.md5', md5_mock)
    def test_that_encode_text_using_md5(self):
        cache = StepsCache()
        text = "important text"
        encoded_text = cache.encode(text)
        self.assertEquals(encoded_text, 'encrypted_value')

    def test_that_script_step_data_gets_deleted(self):
        cache = StepsCache()
        client = cache.get_redis_client()
        script_name = 'my_script'
        first_step = 'step 1 1'
        client.sadd(script_name, first_step)
        cache.key_name = Mock(return_value=script_name)
        cache.delete_script_steps_data(client)

        self.assertFalse(client.exists(script_name))

    def test_that_key_name_is_ureport(self):
        cache = StepsCache()
        self.assertEquals(cache.key_name(), "ureport-registration-steps")