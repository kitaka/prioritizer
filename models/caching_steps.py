from flask import json
import hashlib
import urllib2, base64
from models.encoder import Encoder
from models.priority_cache import PriorityCache


class StepsCache(PriorityCache):

    def __init__(self, client, username, password, url, cache_key_name):
        super(StepsCache, self).__init__(client, cache_key_name)
        self.username = username
        self.password = password
        self.url = url

    def add_script_steps_data(self):
        script_steps = self.get_steps_information()
        for value in script_steps:
            self.client.sadd(self.get_key_name(), self.encoder.encode(value))

    def get_steps_information(self):
        response = self.get_authorized_response(self.url)

        data = json.loads(response.read())
        return data["steps"]

    def delete_script_steps_data(self):
        self.client.delete(self.get_key_name())

    def has_text(self, text):
        return self.client.sismember(self.get_key_name(), self.encoder.encode(text))

    def get_authorized_response(self, url):
        request = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        response = urllib2.urlopen(request)
        return response
