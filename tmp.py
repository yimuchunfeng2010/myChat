from proto.proto import *

aes_key = UtilTool.gen_aes_key()

orgin_msg = 'xkNz25L6FQDPn4UEojHtaepABircdYbW'
print("orgin ",orgin_msg)
receive_msg = dict()
public_key = './crypto_module/key_files/friend/@d2c155385e1170a421472a3bd15c2f9a4e2578509cdb230c67a7591459b29631_1549727825_id_rsa.pub'
en_msg = UtilTool.encrypt_rsa_by_public_file(public_key, orgin_msg)

aes_msg = "****" + en_msg.decode("ISO-8859-1")
print(aes_msg)

pre_msg = aes_msg.lstrip("****")
pre_msg = pre_msg.encode("ISO-8859-1")
print("pre_msg", pre_msg)
private_key = './crypto_module/key_files/mine/@d2c155385e1170a421472a3bd15c2f9a4e2578509cdb230c67a7591459b29631_1549727825_id_rsa.pri'

msg = UtilTool.decrypt_rsa_by_private_file(private_key, pre_msg)
print(msg)
