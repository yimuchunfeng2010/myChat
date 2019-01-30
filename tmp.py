import rsa
import random
import string
from config.config import *


class ChatInfo():
    """聊天信息"""
    aes_key = ""
    rsa_public_key = ""
    rsa_private_key = ""

    chat_name = ""
    nick_name = ""

    def __init__(self):
        """"初始化"""
        self.rsa_public_key, self.rsa_private_key = rsa.newkeys(RSA_KEY_LEN)
        self.aes_key = "".join(random.sample(string.digits + string.ascii_letters + "~!@#$%^&*()_+-=", AES_KEY_LEN))

    def set_aes_key(self, key):
        self.aes_key = key

    def get_aes_key(self, key):
        return self.aes_key

    def set_chat_name(self, chat_name):
        self.chat_name = chat_name

    def get_chat_name(self):
        return self.chat_name

    def set_rsa_key(self, public_key, private_key):
        self.rsa_public_key = public_key
        self.rsa_private_key = private_key

    def get_rsa_key(self):
        return self.rsa_public_key, self.rsa_private_key

    def gen_new_rsa_key(self):
        self.rsa_public_key, self.rsa_private_key = rsa.newkeys(RSA_KEY_LEN)
        return self.rsa_public_key, self.rsa_private_key


chat = ChatInfo()
print(type(chat.aes_key))
chatObj = list()
chatObj.append(ChatInfo())
chatObj.append(ChatInfo())

for i in chatObj:
    print(i.aes_key)
    print(i.rsa_private_key)
