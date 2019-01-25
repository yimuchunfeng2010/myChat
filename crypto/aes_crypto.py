from Crypto.Cipher import AES
import base64


# 用aes加密，再用base64  encode
def aes_encrypt(data):
    import base64
    key = "0987654321"  # todo 临时密钥， 加密时使用的key，只能是长度16,24和32的字符串
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    cipher = AES.new(key)
    encrypted = cipher.encrypt(pad(data))  # aes加密
    result = base64.b64encode(encrypted)  # base64 encode
    return result


# 把加密的数据，用base64  decode，再用aes解密
def aes_decode(data):
    key = "0987654321"
    unpad = lambda s: s[0:-ord(s[-1])]
    cipher = AES.new(key)
    result2 = base64.b64decode(data)
    decrypted = unpad(cipher.decrypt(result2))
    return decrypted


en_msg = aes_encrypt("aaaa")
print("加密后: ", en_msg)

de_msg = aes_decode(en_msg)

print("解密后: ", de_msg)
