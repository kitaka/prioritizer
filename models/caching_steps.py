from flask import json
import hashlib
import urllib2, base64
from models.encoder import Encoder


class StepsCache:

    def __init__(self, client, username, password, url):
        self.client = client
        self.username = username
        self.password = password
        self.url = url
        self.encoder = Encoder()

    def key_name(self):
        return "ureport-registration-steps"

    def add_script_steps_data(self):
        script_steps = self.get_steps_information()
        for value in script_steps:
            self.client.sadd(self.key_name(), self.encoder.encode(value))

    def get_steps_information(self):
        response = self.get_authorized_response(self.url)

        data = json.loads(response.read())
        return data["steps"]

    def delete_script_steps_data(self):
        self.client.delete(self.key_name())

    def get_authorized_response(self, url):
        request = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        response = urllib2.urlopen(request)
        return response
