import hashlib

class Encoder:
    def encode(self,text):
        md5 = hashlib.md5()
        md5.update(text)
        return md5.digest()
