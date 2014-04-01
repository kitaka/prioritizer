from unittest import TestCase
from flask import Flask
from mock import Mock, patch
from mockredis import mock_strict_redis_client
from models.blacklist_filter import BlacklistFilter
from models.encoder import Encoder
from models.priority import Priority
from models.prioritylist import Blacklist
from models.smsc_router import SMSCRouter
import requests


class TestSMSCRouter(TestCase):

    def setUp(self):
        self.app_config = self.get_app_config()
        self.smsc_router = SMSCRouter(self.app_config)

    def test_that_for_message_with_low_priority_the_low_priority_smsc_id_is_used(self):
        url = self.smsc_router.generate_url("message", "111111,222222", Priority.LOW)
        smsc_id = url.split('&')[-1].split('=')[-1]

        self.assertEqual(smsc_id, self.app_config["KANNEL_LOW_PRIORITY_SMSC"])

    def test_that_for_message_with_high_priority_the_low_priority_smsc_id_is_used(self):
        url = self.smsc_router.generate_url("message", "111111,222222", Priority.HIGH)
        smsc_id = url.split('&')[-1].split('=')[-1]

        self.assertEqual(smsc_id, self.app_config["KANNEL_HIGH_PRIORITY_SMSC"])

    def test_that_make_http_request_message_gets_called_with_generated_url(self):
        self.smsc_router.make_http_request = Mock()
        self.smsc_router.generate_url = Mock(return_value="mocked_url")
        self.smsc_router.route(self.get_request_args(), Priority.HIGH)
        self.smsc_router.make_http_request.assert_called_with("mocked_url")

    @patch("requests.get")
    def test_that_requests_get_method_gets_called_by_make_http_request(self, mocked_requests_get):
        any_url = "http://random.url"
        self.smsc_router.make_http_request(any_url)
        mocked_requests_get.assert_called_with(any_url)

    @patch("requests.get", side_effect=requests.exceptions.HTTPError())
    def test_that_an_http_error_exception_gets_caught(self, mocked_requests_get):
        any_url = "invalid_url"

        try:
            self.smsc_router.make_http_request(any_url)
        except Exception, e:
            self.fail("Exception was not caught")


    def get_app_config(self):
        app = Flask(__name__)
        app.config.from_object('settings')
        return app.config

    def get_request_args(self):
        return {"text":"any message", "receivers":"111111,222222,3333333"}
