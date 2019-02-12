import rsa
import time
import string
import random
import base64
import uuid
import os
from Crypto.Cipher import AES
from config.config import *


class UtilTool:
    """工具类"""

    @staticmethod
    def get_cur_time_stamp():
        return str(int(time.time()))

    @staticmethod
    def gen_ras_key(user_name=""):
        time_stamp = UtilTool.get_cur_time_stamp()

        (public_key, private_key) = rsa.newkeys(RSA_KEY_LEN)
        public_key_name = user_name + "_" + time_stamp + "_id_rsa.pub"
        private_key_name = user_name + "_" + time_stamp + "_id_rsa.pri"
        with open("./key_module/key_files/mine/" + public_key_name, 'w+') as f:
            f.write(public_key.save_pkcs1().decode())

        with open("./key_module/key_files/mine/" + private_key_name, 'w+') as f:
            f.write(private_key.save_pkcs1().decode())

        return public_key_name, private_key_name

    @staticmethod
    def gen_aes_key():
        return ''.join(random.sample(string.ascii_letters + string.digits, AES_KEY_LEN))

    # 读取公钥文件以加密信息
    @staticmethod
    def encrypt_rsa_by_public_file(public_file, msg):
        with open(public_file, 'rb') as public_file:
            p = public_file.read()

        public_key = rsa.PublicKey.load_pkcs1(p)
        rsa_en_msg = rsa.encrypt(msg.encode(), public_key)
        encrypted_text = str(base64.encodebytes(rsa_en_msg), encoding='utf-8')
        return encrypted_text

    # 读取私钥钥文件以解密信息
    @staticmethod
    def decrypt_rsa_by_private_file(private_file, msg):
        with open(private_file, 'rb') as private_file:
            p = private_file.read()
        private_key = rsa.PrivateKey.load_pkcs1(p)
        base64_decrypted = base64.decodebytes(msg.encode(encoding='utf-8'))
        return rsa.decrypt(base64_decrypted, private_key)

    # 加密方法
    @staticmethod
    def aes_encrypt(key, my_msg):
        # 初始化加密器
        aes = AES.new(UtilTool.add_to_16(key), AES.MODE_ECB)
        # 先进行aes加密
        encrypt_aes = aes.encrypt(UtilTool.add_to_16(my_msg))
        # 用base64转成字符串形式
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
        return encrypted_text

    # 解密方法
    @staticmethod
    def aes_decrypt(key, my_msg):
        # 初始化加密器
        aes = AES.new(UtilTool.add_to_16(key), AES.MODE_ECB)
        # 优先逆向解密base64成bytes
        base64_decrypted = base64.decodebytes(my_msg.encode(encoding='utf-8'))
        # 执行解密密并转码返回str
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
        return decrypted_text

    # str不是16的倍数那就补足为16的倍数
    @staticmethod
    def add_to_16(value):
        while len(value.encode('utf-8')) % 16 != 0:
            value += '\0'
        return str.encode(value)  # 返回bytes

    # 生成聊天id
    @staticmethod
    def gen_chat_id():
        return str(uuid.uuid1()) + str(int(time.time()))

    # 删除不用的密钥文件
    @staticmethod
    def remove_unused_file():
        paths=list()
        paths.append('./key_module/key_files/mine')
        paths.append('./key_module/key_files/friend')
        for path in paths:
            for file in os.listdir(path):
                path_file = os.path.join(path,file)
                if os.path.isfile(path_file):
                    os.remove(path_file)
