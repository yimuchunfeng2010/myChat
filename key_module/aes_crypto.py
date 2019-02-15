# AES-demo

import base64
from Crypto.Cipher import AES

'''
采用AES对称加密算法
'''


# str不是16的倍数那就补足为16的倍数
def add_to_16(value):
    while len(value.encode('utf-8')) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes


# 加密方法
def aes_encrypt(key, my_msg):
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 先进行aes加密
    print("AA len",len(add_to_16(my_msg)))
    encrypt_aes = aes.encrypt(add_to_16(my_msg))
    # 用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    return encrypted_text


# 解密方法
def aes_decrypt(key, my_msg):
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(my_msg.encode(encoding='utf-8'))
    # 执行解密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return decrypted_text


if __name__ == '__main__':
    # 密文
    aes_key = '''S@@?~&i/wWP=\&[;Ju7a/E9[~qKp$8Fu'''
    tmp_user_id = '''@3d6a4a27b9683f1bef514f5745f1ad1e5177622b6e4a77c901be3a5a26d0cfc8'''
    msg = '@3d6a4a27b9683f1bef514f5745f1ad1e5177622b6e4a77c901be3a5a26d0cfc8jT+Cm2nDBDjzKkihAw582ZA/XT+kBW3X3rwrl/panIk='

    en_msg = aes_encrypt(aes_key, aes_key)
    print("加密后： ", en_msg)
    tmp_en_msg = tmp_user_id+en_msg
    pre_msg =tmp_en_msg.lstrip(tmp_user_id)
    de_msg = aes_decrypt(aes_key, pre_msg)
    print("解密后： ", de_msg)
