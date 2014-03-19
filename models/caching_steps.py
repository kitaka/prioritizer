from flask import json
import redis
import hashlib
import urllib2, base64


class StepsCache:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def key_name(self):
        return "ureport-registration-steps"

    def get_redis_client(self):
        return redis.StrictRedis(host='localhost', port=6379, db=0)

    def add_script_steps_data(self, client):
        script_steps = self.get_steps_information()
        for value in script_steps:
            client.sadd(self.key_name(), self.encode(value))

    def get_steps_information(self):
        url = "http://localhost/script/steps"
        response = self.get_authorized_response(url)

        data = json.loads(response.read())
        return data["steps"]

    def encode(self, text):
        md5 = hashlib.md5()
        md5.update(text)
        return md5.digest()

    def delete_script_steps_data(self, client):
        client.delete(self.key_name())

    def get_authorized_response(self, url):
        request = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        response = urllib2.urlopen(request)
        return response
