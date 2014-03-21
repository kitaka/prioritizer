from models.encoder import Encoder
from models.priority_cache import PriorityCache


class BlacklistCache(PriorityCache):

    def __init__(self, client, cache_key_name):
        super(BlacklistCache, self).__init__(client, cache_key_name)

    def add_to_blacklist(self, text):
        encoded_text = self.encoder.encode(text)
        self.client.sadd(self.get_key_name(), encoded_text)
