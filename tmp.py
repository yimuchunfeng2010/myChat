from crypto_module.rsa_crypto import *

tmp_aes_key = '''!@#$%^&*()_+=-.,'''

tmp_public_key, tmp_private_key = get_rsa_key()

with open('public.pem','w+') as f:
    f.write(tmp_public_key.save_pkcs1().decode())

with open('private.pem','w+') as f:
    f.write(tmp_private_key.save_pkcs1().decode())


# 传输公钥文件