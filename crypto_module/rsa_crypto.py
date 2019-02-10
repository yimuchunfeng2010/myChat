import rsa
from config.config import *


# 生成rsa密钥对
def get_rsa_key(user_name):
    (public_key, private_key) = rsa.newkeys(RSA_KEY_LEN)
    public_key_name = user_name + "public.file"
    private_key_name = user_name + "private.file"
    # with open(public_key_name, 'w+') as f:
    #     f.write(public_key.save_pkcs1().decode())
    #
    # with open(private_key_name, 'w+') as f:
    #     f.write(private_key.save_pkcs1().decode())

    return public_key_name, private_key_name


# 加密

def encrypt_by_rsa(public_key, msg):
    message = msg.encode()
    return rsa.encrypt(message, public_key)


# 解密
def decrypt_by_rsa(private_key, msg):
    return rsa.decrypt(msg, private_key).decode()


# 读取公钥文件以加密信息

def encrypt_rsa_by_public_file(public_file, msg):
    with open(public_file, 'rb') as public_file:
        p = public_file.read()

    public_key = rsa.PublicKey.load_pkcs1(p)
    return rsa.encrypt(msg.encode(), public_key)


# 读取私钥钥文件以解密信息

def decrypt_rsa_by_private_file(private_file, msg):
    with open(private_file, 'rb') as private_file:
        p = private_file.read()

    private_key = rsa.PrivateKey.load_pkcs1(p)
    return rsa.decrypt(msg, private_key)


# 测试代码
# test_message = 'Now is better...............'
test_message = '2345'
publicKey, privateKey = get_rsa_key("123")
en_msg = encrypt_rsa_by_public_file(publicKey, test_message)
print('Before encrypted:', en_msg)

print(type(en_msg))
de_msg = decrypt_rsa_by_private_file(privateKey, en_msg)
print('After encrypted:', de_msg)
