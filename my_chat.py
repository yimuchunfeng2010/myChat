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
from crypto_module.aes_crypto import *

sys.path.append(os.getcwd() + '/constants')

importlib.reload(sys)

owner_name = ''
mutex = threading.Lock()

msg_arr = []
cur_chatter = "微信测试"
friends_list = {}

global_chat_info = dict()

# 聊天室信息
global_chat_room_info = dict()

# 好友信息
global_friend_info = dict()


def say():
    while True:
        global cur_chatter
        my_msg = input()
        # 切换聊天对象
        if my_msg.startswith("chat"):
            cur_chatter = friends_list[my_msg.lstrip("chat ")]
            continue

        # 未启动加密，则启动加密协商，
        if my_msg.startswith("secret") and cur_chatter not in global_chat_info:
            start_key_agreement(cur_chatter)
            continue

        print('我说：' + my_msg)
        # 协商完成,加密通信，否则不加密
        if cur_chatter in global_chat_info and global_chat_info[cur_chatter].is_ready is True:
            aes_encrypt(global_chat_info[cur_chatter].aes_key, my_msg)

        itchat.send_msg(my_msg, toUserName=cur_chatter)


@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, VIDEO], isFriendChat=True,
                     isGroupChat=True, isMpChat=True)
def listen(receive_msg):
    print("Receive New Msg")
    print(receive_msg)
    global owner_name

    #  收到aes密钥，返回密钥协商步骤三
    if receive_msg.Text.startswith("****"):
        if receive_msg.ToUserName not in global_chat_info:
            print("密钥协商异常")
            return
        else:
            aes_ack(receive_msg)

    # 保存aes密钥, 密钥协商步骤四
    if receive_msg.Text.startswith(owner_name) and receive_msg.FromUserName in global_chat_info:
        save_aes(receive_msg)

    if global_chat_info[cur_chatter].is_ready is True:
        de_receive_msg = aes_decrypt(global_chat_info[cur_chatter].aes_key, receive_msg)
    else:
        de_receive_msg = receive_msg

    print(de_receive_msg)


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


# 密钥协商步骤二， 收到rsa公钥文件，本地生成aes秘钥并用rsa公钥加密发送给加密通信协商发起者
@itchat.msg_register([ATTACHMENT], isFriendChat=True, isGroupChat=True, isMpChat=True)
def pro_rsa_pub(receive_msg):
    if receive_msg['FileName'].endswith("id_rsa.pub"):
        # 接收到rsa公钥文件
        receive_msg.text('./crypto_module/key_files' + receive_msg['FileName'])
        # 记录公钥文件名(存在初始协商或者正在聊天中两种场景)
        if cur_chatter in global_chat_info:
            global_chat_info[cur_chatter].rsa_public_key_name = receive_msg['FileName']
        else:
            new_chat = ChatInfo()
            new_chat.rsa_public_key = receive_msg['FileName']
            global_chat_info[cur_chatter] = new_chat

        # 生成aes公钥
        key_info = KeyInfo()
        key_info.aes_key = UtilTool.gen_aes_key()
        key_info.time_stamp = str(int(time.time()))

        global_chat_info[cur_chatter].key_info_list.append(key_info)

        # 用rsa 公钥加密 aes 密钥
        aes_msg = UtilTool.encrypt_rsa_by_public_file('./crypto_module/key_files' + receive_msg['FileName'],
                                                      key_info.aes_key)

        # **** 特殊字符，表示后序消息内容是rsa公钥加密过的aes密钥信息
        aes_msg = "****" + aes_msg
        # 发送信息
        itchat.send_msg(aes_msg, toUserName=receive_msg.FromUserName)
    else:
        print("receive file： ", receive_msg['FileName'])


# 收到好友AES密钥确认,密钥协商步骤三
def aes_ack(receive_msg):
    global_chat_info[receive_msg.ToUserName].actual_ack_count += 1

    key_info = KeyInfo()
    key_info.user_name = receive_msg.FromUserName
    key_info.time_stamp = UtilTool.get_cur_time_stamp()

    # 解密aes密钥
    key_info.aes_key = UtilTool.decrypt_rsa_by_private_file(
        global_chat_info[receive_msg.FromUserName].rsa_private_key_name, receive_msg.Text.lstrip("****"))

    global_chat_info[msg[receive_msg.FromUserName]].key_info_list.append(key_info)

    # 若已获取足够确认信息，则向aes密钥协商完成，发送最终aes密钥
    if global_chat_info[receive_msg.FromUserName].actual_ack_count == \
            global_chat_info[receive_msg.FromUserName].except_ack_count:

        if len(global_chat_info[receive_msg.FromUserName].key_info_list) == 0:
            print("aes empty")
            return
        global_chat_info[receive_msg.FromUserName].aes_key = key_info.aes_key  # todo 暂时定为最后一个密钥为公用密钥

        # 将公用aes密钥用每个好友各自的aes加密后发送
        for item in global_chat_info[receive_msg[WX_KEY_USERNAME]].key_info_list:
            send_msg = UtilTool.aes_encrypt(item.aes_key, global_chat_info[receive_msg.FromUserName].aes_key)
            send_msg = item.user_name + send_msg
            itchat.send_msg(send_msg, toUserName=receive_msg[WX_KEY_USERNAME])
        global_chat_info[[WX_KEY_USERNAME]].is_ready = True
        return


# 向所有聊天好友发送协商一致的aes密钥，密钥协商步骤四
def save_aes(receive_msg):
    de_aes_key = aes_decrypt(global_chat_info[receive_msg.FromUserName].key_info_list[0].aes_key,
                             receive_msg.Text.lstrip(owner_name))
    global_chat_info[receive_msg[WX_KEY_USERNAME]].aes_key = de_aes_key
    global_chat_info[receive_msg[WX_KEY_USERNAME]].is_ready = True


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
        new_friend = FriendInfo()
        new_friend.use_name = f.UserName
        new_friend.nick_name = f.NickName
        new_friend.remark_name = f.RemarkName
        global_friend_info[f.UserName] = new_friend

    global cur_chatter

    itchat.get_chatrooms(update=True)
    cur_chatter = friends_list["微信测试"]
    print("娟娟", cur_chatter)


# 获取聊天室信息
def init_chatrooms():
    rooms = itchat.get_chatrooms(update=True)
    for _, val in enumerate(rooms):
        chat_room = ChatRoomInfo()
        chat_room.nick_name = val.NickName
        chat_room.use_name = val.UserName
        chat_room.member_count = val.MemberCount
        global_chat_room_info[val.NickName] = chat_room


def init_mychat():
    #  获取朋友列表
    init_friends()
    # 获取用户本身用户名
    global owner_name
    owner_name = get_owner_user_name()

itchat.search_chatrooms(name="微信测试")
if __name__ == '__main__':
    itchat.auto_login(hotReload=True)  # hotReload=True
    init_mychat()
    # 启动线程
    t1 = threading.Thread(target=say)
    t2 = threading.Thread(target=listen, args=(u'',))
    t1.start()
    t2.start()

    itchat.run()
