# coding:utf-8
import itchat
import os
import sys
import importlib
import threading
from constants.wx_key_type import *
from constants.type import *
from itchat.content import *

sys.path.append(os.getcwd() + '/constants')

importlib.reload(sys)

Owner_user_name = ''
mutex = threading.Lock()

msg_arr = []
cur_chatter = "Dragon"
friends_list = {}


@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True,
                     isGroupChat=True, isMpChat=True)
def listen(msg):
    print_receive_msg(msg)


def print_receive_msg(msg):
    global Owner_user_name
    if WX_KEY_TYPE not in msg:
        return
    print("Receive New Msg")
    if msg[WX_KEY_TYPE] == MSG_TYPE__TEXT:
        if msg[WX_KEY_FROMUSERNAME].startswith(FROM_CHATROOM):
            print(msg[WX_KEY_ACTUALNICKNAME], ": ", msg[WX_KEY_TEXT])
        else:
            if msg[WX_KEY_FROMUSERNAME] == Owner_user_name:
                print("我说: " + msg[WX_KEY_CONTENT])
            else:
                print(msg[WX_KEY_USER][WX_KEY_REMARKNAME], ": ", msg[WX_KEY_CONTENT])


def say():
    while True:
        msg = input()
        # 切换聊天对象
        if msg.startswith("Chat "):
            global cur_chatter
            cur_chatter = friends_list[msg.lstrip("Chat ")]
            continue
        print('我说：'+msg)
        itchat.send_msg(msg, toUserName=cur_chatter)


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


itchat.auto_login(hotReload=True)
init_mychat()
# 启动线程
t1 = threading.Thread(target=say)
t2 = threading.Thread(target=listen, args=(u'',))
t1.start()
t2.start()

itchat.run()
