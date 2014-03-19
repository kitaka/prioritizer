import redis
import hashlib


class StepsCache:

    def get_redis_client(self):
        return redis.StrictRedis(host='localhost', port=6379, db=0)

    def is_value_in_set(self, client, set_name, value):
        return client.sismember(set_name, value)

    def add_script_steps_data(self, client):
        """"
        For the example we have choose set as main value structure.
        Set allows to store unique keys
        """""
        scripts_data = self.get_steps_information()
        for key in scripts_data.iterkeys():
            for value in scripts_data[key]:
                client.sadd(key, self.encode(value))

    def get_steps_information(self):
        return {}

    def encode(self, text):
        md5 = hashlib.md5()
        md5.update(text)
        return md5.digest()

    def delete_script_steps_data(self, client):
        scripts_data = self.get_steps_information()
        for key in scripts_data.iterkeys():
            client.delete(key)