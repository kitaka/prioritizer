import redis
import hashlib


class StepsCache:

    def key_name(self):
        return "ureport-registration-steps"

    def get_redis_client(self):
        return redis.StrictRedis(host='localhost', port=6379, db=0)

    def add_script_steps_data(self, client):
        script_steps = self.get_steps_information()
        for value in script_steps:
            client.sadd(self.key_name(), self.encode(value))

    def get_steps_information(self):
        return {}

    def encode(self, text):
        md5 = hashlib.md5()
        md5.update(text)
        return md5.digest()

    def delete_script_steps_data(self, client):
        client.delete(self.key_name())