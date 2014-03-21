from models.encoder import Encoder


class PriorityCache(object):
    def __init__(self, client, cache_key_name):
        self.client = client
        self.encoder = Encoder()
        self.cache_key_name = cache_key_name

    def get_key_name(self):
        return self.cache_key_name


