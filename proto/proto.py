import rsa
from proto.util import *
from config.config import *


class ChatInfo():
    """聊天信息"""

    # 密钥信息
    aes_key = ""
    rsa_public_key_name = ""
    rsa_private_key_name = ""

    # 主聊天者(发起加密聊天的好友)
    chat_master = ""

    # 期望确认消息个数
    except_ack_count = 0

    # 实际已确认消息个数
    actual_ack_count = 0

    # 密钥数组
    key_info_list = list()

    # 协商成功标志
    is_ready = False

    # 时间戳
    time = ""

    def __init__(self):
        """"初始化"""
        self.is_ready = False
        self.except_ack_count = 0
        self.actual_ack_count = 0

        self.rsa_public_key, self.rsa_private_key = rsa.newkeys(RSA_KEY_LEN)

    def set_aes_key(self, key):
        self.aes_key = key

    def get_aes_key(self):
        return self.aes_key

    def set_rsa_key(self, public_key, private_key):
        self.rsa_public_key = public_key
        self.rsa_private_key = private_key

    def get_rsa_key(self):
        return self.rsa_public_key, self.rsa_private_key

    def get_rsa_public_key(self):
        return self.rsa_public_key

    def get_rsa_private_key(self):
        return self.rsa_private_key

    def gen_new_rsa_key(self):
        self.rsa_public_key, self.rsa_private_key = rsa.newkeys(RSA_KEY_LEN)
        return self.rsa_public_key, self.rsa_private_key


class ChatRoomInfo:
    '''微信群信息'''
    use_name = ""
    nick_name = ""
    member_count = 0
    def __init__(self):
        pass


class FriendInfo:
    '''微信好友信息'''
    use_name = ""
    nick_name = ""
    remark_name = ""

    def __init__(self):
        pass

class KeyInfo:
    aes_key = ""
    user_name = ""
    time_stamp = ""

    def __init__(self):
        pass


# 测试代码
chat = ChatInfo()
print(type(chat.aes_key))
chatObj = list()
chatObj.append(ChatInfo())
chatObj.append(ChatInfo())

for i in chatObj:
    print(i.aes_key)
    print(i.rsa_private_key)
