# coding:utf-8
import itchat
import os
import sys

sys.path.append(os.getcwd() + '/constants')
from constants.wx_key_type import *
from constants.type import *
from itchat.content import *
import importlib

importlib.reload(sys)

Owner_user_name = ''


@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True,
                     isGroupChat=True, isMpChat=True)
def handle_receive_msg(msg):
    print_receive_msg(msg)


def print_receive_msg(msg):
    global Owner_user_name
    # print("Receive New Msg")
    if msg[WX_KEY_TYPE] == MSG_TYPE__TEXT:
        if msg[WX_KEY_FROMUSERNAME].startswith(FROM_CHATROOM):
            print(msg[WX_KEY_ACTUALNICKNAME], ": ", msg[WX_KEY_TEXT])
        else:
            if msg[WX_KEY_FROMUSERNAME] == Owner_user_name:
                print("我: " + msg[WX_KEY_CONTENT])
            else:
                # for k, v in msg.items():
                #     print(k, v)

                print(msg[WX_KEY_USER][WX_KEY_REMARKNAME], ": ", msg[WX_KEY_CONTENT])


def get_friends():
    friends = itchat.get_friends(update=True)  # 获取微信好友列表，如果设置update=True将从服务器刷新列表
    for i in friends:
        print(i)


def get_owner_user_name():
    friends = itchat.get_friends(update=True)
    owner = friends[0]
    return owner[WX_KEY_USERNAME]


itchat.auto_login(hotReload=True)
Owner_user_name = get_owner_user_name()
itchat.run()
