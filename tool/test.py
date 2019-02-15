from proto.info import *

# 本文件用于验证测试python代码
aes_key = UtilTool.gen_aes_key()

orgin_msg = 'ljiNEqXDYUhJ0xsB8AO364cvGzTZPabF'
print("orgin ",orgin_msg)
receive_msg = dict()
public_key = './key_module/key_files/friend/@2beab99b63ee693f5c53fa90f08721bb7ec0006556e58fc3ef28ad781a2b7e7d_1549769155_id_rsa.pub'
en_msg = UtilTool.encrypt_rsa_by_public_file(public_key, orgin_msg)

aes_msg = "****" + en_msg.decode("ISO-8859-1")
print(aes_msg)

pre_msg = aes_msg[len("****")]

pre_msg = pre_msg.encode("ISO-8859-1")
print("pre_msg", pre_msg)
private_key = './key_module/key_files/mine/@2beab99b63ee693f5c53fa90f08721bb7ec0006556e58fc3ef28ad781a2b7e7d_1549769155_id_rsa.pri'

msg = UtilTool.decrypt_rsa_by_private_file(private_key, pre_msg)
print(msg)
