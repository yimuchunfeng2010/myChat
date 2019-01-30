# coding:utf-8
import itchat
import os
import sys
import importlib
import threading
from constants.wx_key_type import *
from constants.type import *
from itchat.content import *
from proto.proto import *
from crypto_module.rsa_crypto import *
from crypto_module.aes_crypto import *

sys.path.append(os.getcwd() + '/constants')

importlib.reload(sys)

Owner_user_name = ''
mutex = threading.Lock()

msg_arr = []
cur_chatter = "Dragon"
friends_list = {}

gloabl_chat_info = dict()


@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True,
                     isGroupChat=True, isMpChat=True)
def listen(receive_msg):
    handle_receive_msg(receive_msg)


def handle_receive_msg(receive_msg):
    print("Receive New Msg")
    global Owner_user_name
    if WX_KEY_TYPE not in receive_msg or WX_KEY_TEXT not in receive_msg or WX_KEY_USERNAME not in receive_msg:
        return

    #  判断是否为AES密钥确认
    if receive_msg[WX_KEY_TEXT].startswith(SECRET_KEY_PREFIX) and receive_msg[WX_KEY_USERNAME] in gloabl_chat_info:
        gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].actual_ack_count += 1

        key_info_item = KeyItem()
        key_info_item.user_name = receive_msg[WX_KEY_USERNAME]
        key_info_item.actual_user_name = receive_msg[WX_KEY_USERNAME]  # todo 修改为取实际发言人
        key_info_item.aes_key = decrypt_by_rsa(gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].rsa_private_key,
                                               receive_msg[WX_KEY_TEXT])
        gloabl_chat_info[msg[WX_KEY_USERNAME]].key_info_list.append(key_info_item)

        # 若已获取足够确认信息，则向aes密钥协商完成，发送最终aes密钥
        if gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].actual_ack_count == \
                gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].except_ack_count:

            gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].aes_key = key_info_item.aes_key  # todo 暂时定为最后一个密钥为公用密钥
            for item in gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].key_info_list:
                send_msg = gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].aes_key
                send_msg = FINAL_AES_KEY_PREFIX + aes_encrypt(item.aes_key, send_msg)
                itchat.send_msg(send_msg, toUserName=cur_chatter)
            return

    # 判断是否为好友主动发起密钥协商
    if receive_msg[WX_KEY_TEXT].startswith(PUBLIC_KEY_PREFIX) and receive_msg[WX_KEY_USERNAME] not in gloabl_chat_info:

        new_chat = ChatInfo()
        gloabl_chat_info[WX_KEY_USERNAME] = new_chat  # 修改名称
        # rsa 公钥加密并发送给密钥协商发起方
        send_msg = encrypt_by_rsa(receive_msg[WX_KEY_TEXT].lstrip(PUBLIC_KEY_PREFIX), new_chat.rsa_public_key)
        itchat.send_msg(send_msg, toUserName=receive_msg[WX_KEY_FROMUSERNAME])  # todo 修改为实际发送者
        key_info = KeyItem()
        key_info.aes_key = new_chat.aes_key
        new_chat.key_info_list.append(key_info)

        mutex.acquire(timeout=10)
        gloabl_chat_info[msg[WX_KEY_USERNAME]] = new_chat
        mutex.release()

        return

    # 协商一致AES密钥
    if receive_msg[WX_KEY_TEXT].startswith(FINAL_AES_KEY_PREFIX) and receive_msg[WX_KEY_USERNAME] in gloabl_chat_info:
        de_aes_key = aes_decrypt(gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].key_info_list[0].aes_key, receive_msg[WX_KEY_TEXT].lstrip(FINAL_AES_KEY_PREFIX))
        gloabl_chat_info[receive_msg[WX_KEY_USERNAME]].aes_key = de_aes_key

    if receive_msg[WX_KEY_TYPE] == MSG_TYPE__TEXT:
        if receive_msg[WX_KEY_FROMUSERNAME].startswith(FROM_CHATROOM):
            print(receive_msg[WX_KEY_ACTUALNICKNAME], ": ", receive_msg[WX_KEY_TEXT])
        else:
            if receive_msg[WX_KEY_FROMUSERNAME] == Owner_user_name:
                print("我说: " + receive_msg[WX_KEY_CONTENT])
            else:
                print(receive_msg[WX_KEY_USER][WX_KEY_REMARKNAME], ": ", receive_msg[WX_KEY_CONTENT])


def say():
    while True:
        my_msg = input()
        # 切换聊天对象
        if my_msg.startswith("Chat "):
            global cur_chatter
            cur_chatter = friends_list[my_msg.lstrip("Chat ")]
            continue
        # 未启动加密，则启动加密协商
        if cur_chatter not in gloabl_chat_info:
            start_key_agreement(cur_chatter)

        # 协商完成
        while gloabl_chat_info[cur_chatter].aes_key != "":
            print('我说：' + my_msg)
            itchat.send_msg(my_msg, toUserName=cur_chatter)


def get_friends():
    friends = itchat.get_friends(update=True)  # 获取微信好友列表，如果设置update=True将从服务器刷新列表
    for i in friends:
        print(i)


def get_friends_chat_name(nick_name):
    if nick_name in friends_list.keys():
        return friends_list[nick_name]
    else:
        return ""


def get_owner_user_name():
    friends = itchat.get_friends(update=True)
    owner = friends[0]
    global Owner_user_name
    Owner_user_name = owner
    return owner[WX_KEY_USERNAME]


def init_friends():
    friends = itchat.get_friends(update=True)  # 获取微信好友列表，如果设置update=True将从服务器刷新列表
    global friends_list
    for f in friends:
        friends_list[f["NickName"]] = f["UserName"]

    global cur_chatter
    cur_chatter = friends_list["Dragon"]


def init_mychat():
    #  获取朋友列表
    init_friends()
    # 获取用户本身用户名
    get_owner_user_name()
    # 获取好友


# 发起协商，生成RSA密钥对，并将公钥发给好友

def start_key_agreement(user_name):
    new_chat = ChatInfo()
    send_msg = PUBLIC_KEY_PREFIX + new_chat.get_rsa_public_key()
    itchat.send_msg(send_msg, toUserName=user_name)
    mutex.acquire(timeout=10)
    if user_name.startsWith(FROM_CHATROOM):
        chatroom_info = itchat.search_chatrooms(userName=user_name)
        new_chat.except_ack_count = chatroom_info["MemberCount"] - 1  # 出去自身，所以-1
    else:
        new_chat.except_ack_count = 1
    gloabl_chat_info[user_name] = new_chat
    mutex.release()


itchat.auto_login(hotReload=True)
init_mychat()
# 启动线程
t1 = threading.Thread(target=say)
t2 = threading.Thread(target=listen, args=(u'',))
t1.start()
t2.start()

itchat.run()
