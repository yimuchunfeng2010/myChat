# coding:utf-8
import itchat
import os
import sys
import importlib
import threading
import json
from constants.wx_key_type import *
from constants.type import *
from itchat.content import *
from proto.proto import *
from crypto_module.rsa_crypto import *
from crypto_module.aes_crypto import *

sys.path.append(os.getcwd() + '/constants')

importlib.reload(sys)

owner_name = ''
mutex = threading.Lock()

msg_arr = []
cur_chatter = "Dragon"
friends_list = {}

global_chat_info = dict()


@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True,
                     isGroupChat=True, isMpChat=True)
def listen(receive_msg):
    print("Receive New Msg")
    print(receive_msg)
    global owner_name
    # 下载文件
    # receive_msg.text('./' + receive_msg['FileName'])
    # users = itchat.search_friends('曾元军')
    # userName = users[0]['UserName']
    # 下载文件

    # print(receive_msg.Text)
    # print(receive_msg.Type)
    # print(receive_msg.MsgId)
    # 获取群成员
    # print("AAA",receive_msg.User.MemberList[0])
    if WX_KEY_TYPE not in receive_msg or WX_KEY_TEXT not in receive_msg or WX_KEY_USERNAME not in receive_msg:
        print("invalid msg", receive_msg)
        return

    #  接收到好友RSA公钥文件，返回AES密钥，密钥协商步骤二
    if receive_msg[WX_KEY_TYPE] == MSG_TYPE__ATTACHMENT and msg['FileName'] == msg[WX_KEY_FROMUSERNAME] + "public.pem" \
            and receive_msg[WX_KEY_USERNAME] not in global_chat_info:
        response_key_agreement(receive_msg)
        return

    #  aes确认消息，返回密钥协商步骤三
    if receive_msg[WX_KEY_TEXT].startswith(SECRET_KEY_PREFIX) and receive_msg[WX_KEY_USERNAME] in global_chat_info:
        aes_ack(receive_msg)

    # 保存aes密钥, 密钥协商步骤四
    if receive_msg[WX_KEY_TEXT].startswith(FINAL_AES_KEY_PREFIX) and receive_msg[WX_KEY_USERNAME] in global_chat_info:
        save_aes(receive_msg)

    if global_chat_info[cur_chatter].is_ready is True:
        de_receive_msg = aes_decrypt(global_chat_info[cur_chatter].aes_key, receive_msg)
    else:
        de_receive_msg = receive_msg

    if de_receive_msg[WX_KEY_TYPE] == MSG_TYPE__TEXT:
        if de_receive_msg[WX_KEY_FROMUSERNAME].startswith(FROM_CHATROOM):
            print(de_receive_msg[WX_KEY_ACTUALNICKNAME], ": ", de_receive_msg[WX_KEY_TEXT])
        else:
            if de_receive_msg[WX_KEY_FROMUSERNAME] == owner_name:
                print("我说: " + de_receive_msg[WX_KEY_CONTENT])
            else:
                print(de_receive_msg[WX_KEY_USER][WX_KEY_REMARKNAME], ": ", de_receive_msg[WX_KEY_CONTENT])


def say():
    while True:
        global cur_chatter
        my_msg = input()
        # 切换聊天对象
        if my_msg.startswith("chat"):
            cur_chatter = friends_list[my_msg.lstrip("chat ")]
            continue

        # 未启动加密，则启动加密协商
        if my_msg.startswith("secret") and cur_chatter not in global_chat_info:
            start_key_agreement(cur_chatter)
            continue

        # 协商完成

        if cur_chatter in global_chat_info and global_chat_info[cur_chatter].is_ready:
            print('我说：' + my_msg)
            itchat.send_msg(my_msg, toUserName=cur_chatter)


def get_friends():
    friends = itchat.get_friends(update=True)  # 获取微信好友列表，如果设置update=True将从服务器刷新列表
    for friend in friends:
        print(friend)


def get_friends_chat_name(nick_name):
    if nick_name in friends_list.keys():
        return friends_list[nick_name]
    else:
        return ""


def get_owner_user_name():
    friends = itchat.get_friends(update=True)
    owner = friends[0]
    if WX_KEY_USERNAME in owner:
        return owner[WX_KEY_USERNAME]
    else:
        return ""


def init_friends():
    friends = itchat.get_friends(update=True)  # 获取微信好友列表，如果设置update=True将从服务器刷新列表
    global friends_list
    print("init_friends")
    for f in friends:
        friends_list[f["NickName"]] = f["UserName"]
        print(f)

    global cur_chatter

    cur_chatter = friends_list["娟娟"]
    print("娟娟", cur_chatter)


def init_mychat():
    #  获取朋友列表
    init_friends()
    # 获取用户本身用户名
    global owner_name
    owner_name = get_owner_user_name()


# 发起协商，生成RSA密钥对，并将公钥发给好友，密钥协商步骤一
def start_key_agreement(user_name):
    new_chat = ChatInfo()
    mutex.acquire(timeout=10)

    # 群聊
    if user_name.startswith(FROM_CHATROOM):
        chatroom_info = itchat.search_chatrooms(userName=user_name)
        new_chat.except_ack_count = chatroom_info["MemberCount"] - 1  # 除去自身，所以-1
    else:
        new_chat.except_ack_count = 1
    global_chat_info[user_name] = new_chat
    mutex.release()

    # 发送RSA公钥文件
    itchat.send_msg("@fil@%s" % new_chat.rsa_public_key, toUserName=user_name)


# 收到好友RSA公钥文件，响应密钥协商，本地生成AES密钥，并发送给好友， 密钥协商步骤二
def response_key_agreement(receive_msg):
    new_chat = ChatInfo()
    # rsa 公钥加密并发送给密钥协商发起方
    send_msg = SECRET_KEY_PREFIX + encrypt_by_rsa(receive_msg[WX_KEY_TEXT].lstrip(PUBLIC_KEY_PREFIX),
                                                  new_chat.rsa_public_key)
    itchat.send_msg(send_msg, toUserName=receive_msg[WX_KEY_FROMUSERNAME])  # todo 修改为实际发送者
    key_info = KeyItem()
    key_info.aes_key = new_chat.aes_key
    new_chat.key_info_list.append(key_info)

    mutex.acquire(timeout=10)
    global_chat_info[msg[WX_KEY_USERNAME]] = new_chat
    mutex.release()


# 收到好友AES密钥确认,密钥协商步骤三
def aes_ack(receive_msg):
    global_chat_info[receive_msg[WX_KEY_USERNAME]].actual_ack_count += 1

    key_info_item = KeyItem()
    key_info_item.user_name = receive_msg[WX_KEY_USERNAME]
    key_info_item.actual_user_name = receive_msg[WX_KEY_USERNAME]  # todo 修改为取实际发言人
    key_info_item.aes_key = decrypt_by_rsa(global_chat_info[receive_msg[WX_KEY_USERNAME]].rsa_private_key,
                                           receive_msg[WX_KEY_TEXT])
    global_chat_info[msg[WX_KEY_USERNAME]].key_info_list.append(key_info_item)

    # 若已获取足够确认信息，则向aes密钥协商完成，发送最终aes密钥
    if global_chat_info[receive_msg[WX_KEY_USERNAME]].actual_ack_count == \
            global_chat_info[receive_msg[WX_KEY_USERNAME]].except_ack_count:

        global_chat_info[receive_msg[WX_KEY_USERNAME]].aes_key = key_info_item.aes_key  # todo 暂时定为最后一个密钥为公用密钥
        for item in global_chat_info[receive_msg[WX_KEY_USERNAME]].key_info_list:
            send_msg = global_chat_info[receive_msg[WX_KEY_USERNAME]].aes_key
            send_msg = FINAL_AES_KEY_PREFIX + aes_encrypt(item.aes_key, send_msg)
            itchat.send_msg(send_msg, toUserName=cur_chatter)
        global_chat_info[[WX_KEY_USERNAME]].is_ready = True
        return


# 向所有聊天好友发送协商一致的aes密钥，密钥协商步骤四
def save_aes(receive_msg):
    de_aes_key = aes_decrypt(global_chat_info[receive_msg[WX_KEY_USERNAME]].key_info_list[0].aes_key,
                             receive_msg[WX_KEY_TEXT].lstrip(FINAL_AES_KEY_PREFIX))
    global_chat_info[receive_msg[WX_KEY_USERNAME]].aes_key = de_aes_key
    global_chat_info[receive_msg[WX_KEY_USERNAME]].is_ready = True


def prn_obj(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)  # hotReload=True
    init_mychat()
    # 启动线程
    t1 = threading.Thread(target=say)
    t2 = threading.Thread(target=listen, args=(u'',))
    t1.start()
    t2.start()

    itchat.run()
