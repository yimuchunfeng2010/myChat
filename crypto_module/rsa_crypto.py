import rsa
from config.config import *


# 生成rsa密钥对
def get_rsa_key():
    (public_key, private_key) = rsa.newkeys(RSA_KEY_LEN)
    return public_key, private_key


# 加密

def encrypt_by_rsa(public_key, msg):
    message = msg.encode()
    return rsa.encrypt(message, public_key)


# 解密
def decrypt_by_rsa(private_key, msg):
    return rsa.decrypt(msg, private_key).decode()

# 测试代码
message = 'Now is better...............'
publicKey, privateKey = get_rsa_key()
en_msg = encrypt_by_rsa(publicKey, message)
print('Before encrypted:', en_msg)

de_msg = decrypt_by_rsa(privateKey, en_msg)
print('After encrypted:', de_msg)
