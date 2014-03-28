
class ContentTypes():
    TEXT = "text"
    CONTACTS = "contacts"


class PriorityListFoundation():

    POLL_TEXT_KEY = "%s:poll_texts:%s"
    POLL_CONTACTS_KEY = "%s:poll_contacts:%s"

    def __init__(self, list_name, redis_client, encoder):
        self.redis_client = redis_client
        self.encoder = encoder
        self.list_name = list_name

    def has(self, poll_id, content_type, contents):
        key_name = self.get_key_name(poll_id, content_type)
        contents = self.filter_contents(content_type, contents)
        return self.redis_client.sismember(key_name, contents)

    def delete(self, poll_id, content_type, contents):
        contents = self.get_content_array(contents)
        key_name = self.get_key_name(poll_id, content_type)
        contents = self.filter_contents(content_type, contents)
        self.redis_client.srem(key_name, *contents)

    def add(self, poll_id, content_type, contents):
        contents = self.get_content_array(contents)
        key_name = self.get_key_name(poll_id, content_type)
        contents = self.filter_contents(content_type, contents)
        self.redis_client.sadd(key_name, *contents)

    def get_key_name(self, poll_id, content_type):
        if content_type == ContentTypes.TEXT:
            return self.POLL_TEXT_KEY % (self.list_name, poll_id)
        else:
            return self.POLL_CONTACTS_KEY % (self.list_name, poll_id)

    def get_content_array(self, contents):
        return [contents] if isinstance(contents, basestring) else contents

    def encode_contents(self, contents):
        if isinstance(contents, basestring):
            return self.encoder.encode(contents)
        return map(self.encoder.encode, contents)

    def filter_contents(self, content_type, contents):
        if content_type == ContentTypes.TEXT:
            contents = self.encode_contents(contents)
        return contents


class PriorityList(PriorityListFoundation):

    def __init__(self, list_name, redis_client, encoder):
        PriorityListFoundation.__init__(self, list_name, redis_client, encoder)

    def poll_text(self, poll_id, text):
        self.add(poll_id, ContentTypes.TEXT, text)

    def poll_contacts(self, poll_id, contacts):
        self.add(poll_id, ContentTypes.CONTACTS, contacts)

    def has_poll_text(self, poll_id, text):
        return self.has(poll_id, ContentTypes.TEXT, text)

    def has_poll_contact(self, poll_id, contact):
        return self.has(poll_id, ContentTypes.CONTACTS, contact)

    def delete_poll_text(self, poll_id, text):
        self.delete(poll_id, ContentTypes.TEXT, text)

    def delete_poll_contacts(self, poll_id, contacts):
        self.delete(poll_id, ContentTypes.CONTACTS, contacts)


class Blacklist(PriorityList):

    def __init__(self, redis_client, encoder):
        PriorityList.__init__(self, "blacklist", redis_client, encoder)


class Whitelist(PriorityList):

    def __init__(self, redis_client, encoder):
        PriorityList.__init__(self, "whitelist", redis_client, encoder)