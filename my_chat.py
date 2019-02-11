# coding:utf-8
import itchat
import os
import sys
import importlib
import threading
from goto import with_goto
from constants.wx_key_type import *
from constants.type import *
from itchat.content import *
from proto.proto import *

sys.path.append(os.getcwd() + '/constants')

importlib.reload(sys)

owner_name = ''
mutex = threading.Lock()

msg_arr = []
cur_chatter_name = "起风了"
# cur_chatter_name = "贝贝奶奶"

cur_chatter = ""
friends_list = {}

global_chat_info = dict()

global_name_id_map = dict()

# 聊天室信息
global_chat_room_info = dict()

# 好友信息
global_friend_info = dict()


@with_goto
def say():
    while True:
        label.start
        global cur_chatter
        my_msg = input()
        # 切换聊天对象
        if my_msg.startswith("$chat"):
            global friends_list
            # cur_chatter = friends_list[my_msg.lstrip("$chat ")]
            # todo 暂时不切换聊天对象
            cur_chatter = friends_list[cur_chatter_name]

            # 判断是否已经加密
            if cur_chatter in global_name_id_map and global_name_id_map[cur_chatter] in global_chat_info and \
                    global_chat_info[global_name_id_map[cur_chatter]].is_ready is True:
                cur_chatter = friends_list[cur_chatter_name]
            else:
                # todo 未启动加密，则启动加密协商，

                # todo 首先测试对方是否支持加密聊天

                # 协商聊天id
                send_chat_id(cur_chatter)
                # 等待chat_id协商完成，超时则返回
                cnt = 0
                while global_chat_info[global_name_id_map[cur_chatter]].is_chat_id_ready is False:
                    time.sleep(1)
                    # 10s超时
                    if cnt >= 5:
                        print("等待聊天id协商完成超时")
                        goto.start

                print("密钥协商步骤一")
                start_key_agreement(global_name_id_map[cur_chatter])

                cnt = 0
                while global_chat_info[global_name_id_map[cur_chatter]].is_ready is not True:
                    time.sleep(1)
                    # 10s超时
                    if cnt >= 10:
                        print("等待聊天协商完成超时,程序异常退出")
                        goto.start
        if my_msg.startswith("$chat"):
            goto.start

        print('我：' + my_msg)
        # 协商完成,加密通信
        if cur_chatter in global_name_id_map:
            chat_id = global_name_id_map[cur_chatter]
            if chat_id in global_chat_info and global_chat_info[chat_id].is_ready is True:
                cur_msg = UtilTool.aes_encrypt(global_chat_info[chat_id].aes_key, my_msg)
                itchat.send_msg(cur_msg, toUserName=cur_chatter)


# 微信消息类型 TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, VIDEO
@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True, isMpChat=True)
@with_goto
def listen(receive_msg):
    print("Receive New Msg:", receive_msg)
    global owner_name

    if not hasattr(receive_msg, 'Text'):
        return
        # 接收到chat_id
    if receive_msg.Text.startswith("%%%%"):
        chat_id = receive_msg.Text.lstrip("%%%%")
        new_chat = ChatInfo()
        new_chat.chat_user_name = receive_msg.FromUserName
        new_chat.is_chat_id_ready = True
        global_chat_info[chat_id] = new_chat

        global_name_id_map[receive_msg.FromUserName] = chat_id

        # 发送确认消息
        itchat.send_msg("!!!!" + receive_msg.Text.lstrip("%%%%"), toUserName=receive_msg.FromUserName)
        return
    # 接受到chat_id确认消息
    if receive_msg.Text.startswith("!!!!"):
        chat_id = receive_msg.Text.lstrip("!!!!")
        if chat_id in global_chat_info:
            print("chat id 协商完成")
            global_chat_info[chat_id].is_chat_id_ready = True

        else:
            print("聊天ID协商异常，程序退出,id", chat_id)
        return

    #  收到aes密钥，返回密钥协商步骤三
    if receive_msg.Text.startswith("****"):
        print("密钥协商步骤三")
        if receive_msg.FromUserName not in global_name_id_map:
            print("密钥协商异常, 程序退出")
        else:
            aes_ack(receive_msg)
        return

    # 保存aes密钥, 密钥协商步骤四
    if receive_msg.Text.startswith(owner_name) and receive_msg.FromUserName in global_name_id_map:
        print("密钥协商步骤四")
        save_aes(receive_msg)
        print("密钥协商完成，开始加密通信")
        return

    if receive_msg.FromUserName in global_name_id_map:
        chat_id = global_name_id_map[receive_msg.FromUserName]
        if global_chat_info[chat_id].is_ready is True:
            de_receive_msg = UtilTool.aes_decrypt(global_chat_info[chat_id].aes_key, receive_msg.Text)
        else:
            de_receive_msg = receive_msg
    else:
        de_receive_msg = receive_msg

    if receive_msg.FromUserName in global_friend_info:
        if global_friend_info[receive_msg.FromUserName].remark_name != '':
            chatter = global_friend_info[receive_msg.FromUserName].remark_name
        else:
            chatter = global_friend_info[receive_msg.FromUserName].nick_name
    print(chatter, "： ", de_receive_msg)


# 发起协商，生成RSA密钥对，并将公钥发给好友，密钥协商步骤一
def start_key_agreement(chat_id):
    # 生成RSA密钥对
    if chat_id in global_chat_info:
        user_name = global_chat_info[chat_id].chat_user_name
    else:
        print("未找到用户名")
        return
    public_key_name, private_key_name = UtilTool.gen_ras_key(user_name)
    mutex.acquire(timeout=10)

    # 群聊天以群组名作为聊天id, 好友聊天则以两个好友用户名为id
    if user_name.startswith(FROM_CHATROOM):
        chat_room_info = itchat.search_chatrooms(userName=user_name)
        global_chat_info[chat_id].except_ack_count = chat_room_info["MemberCount"] - 1
    else:
        global_chat_info[chat_id].except_ack_count = 1

    global_chat_info[chat_id].rsa_private_key_name = "./crypto_module/key_files/mine/" + private_key_name
    global_chat_info[chat_id].rsa_public_key_name = "./crypto_module/key_files/mine/" + public_key_name
    mutex.release()

    # 发送RSA公钥文件
    itchat.send_file(global_chat_info[chat_id].rsa_public_key_name, toUserName=user_name)


# 密钥协商步骤二， 收到rsa公钥文件，本地生成aes秘钥并用rsa公钥加密发送给加密通信协商发起者
@itchat.msg_register([ATTACHMENT], isFriendChat=True, isGroupChat=True, isMpChat=True)
def pro_rsa_pub(receive_msg):
    print("密钥协商步骤二")
    print("receive file, ", receive_msg)
    if hasattr(receive_msg, "Content") and "id_rsa.pub" in receive_msg.Content:
        # 接收到rsa公钥文件
        receive_msg.text('./crypto_module/key_files/friend/' + receive_msg['FileName'])

        # 记录公钥文件名(存在初始协商或者正在聊天中两种场景)
        if receive_msg.FromUserName in global_name_id_map:
            global_chat_info[global_name_id_map[receive_msg.FromUserName]].rsa_public_key_name = receive_msg.FileName

            # 生成aes公钥
            key_info = KeyInfo()
            key_info.aes_key = UtilTool.gen_aes_key()
            key_info.time_stamp = str(int(time.time()))

            global_chat_info[global_name_id_map[receive_msg.FromUserName]].key_info_list.append(key_info)

            # 用rsa 公钥加密 aes 密钥
            aes_msg = UtilTool.encrypt_rsa_by_public_file('./crypto_module/key_files/friend/' + receive_msg['FileName'],
                                                          key_info.aes_key)

            # **** 特殊字符，表示后序消息内容是rsa公钥加密过的aes密钥信息
            aes_msg = "****" + aes_msg + "####" + owner_name

            itchat.send_msg(aes_msg, toUserName=receive_msg.FromUserName)
    else:
        print("receive file： ", receive_msg.FileName)


# 收到好友AES密钥确认,密钥协商步骤三
def aes_ack(receive_msg):
    chat_id = global_name_id_map[receive_msg.FromUserName]
    global_chat_info[chat_id].actual_ack_count += 1

    key_info = KeyInfo()

    key_info.time_stamp = UtilTool.get_cur_time_stamp()

    tmp_msg = receive_msg.Text
    tmp_msg = tmp_msg.lstrip("****")
    index = tmp_msg.find('####')
    pre_msg = tmp_msg[:index]
    key_info.user_name = tmp_msg[index + 4:]

    pre_msg = pre_msg

    de_aes_key = UtilTool.decrypt_rsa_by_private_file(global_chat_info[chat_id].rsa_private_key_name, pre_msg)
    key_info.aes_key = de_aes_key.decode()

    global_chat_info[chat_id].key_info_list.append(key_info)

    # 若已获取足够确认信息，则向aes密钥协商完成，发送最终aes密钥
    if global_chat_info[chat_id].actual_ack_count == \
            global_chat_info[chat_id].except_ack_count:

        if len(global_chat_info[chat_id].key_info_list) == 0:
            print("aes empty")
            return
        global_chat_info[chat_id].aes_key = key_info.aes_key  # todo 暂时定为最后一个密钥为公用密钥

        # 将公用aes密钥用每个好友各自的aes加密后发送
        for item in global_chat_info[chat_id].key_info_list:
            send_msg = UtilTool.aes_encrypt(item.aes_key, global_chat_info[chat_id].aes_key)
            send_msg = item.user_name + send_msg
            itchat.send_msg(send_msg, toUserName=receive_msg.FromUserName)
        print("密钥协商完成，开始加密聊天")
        global_chat_info[chat_id].is_ready = True
        return


# 向所有聊天好友发送协商一致的aes密钥，密钥协商步骤四
def save_aes(receive_msg):
    chat_id = global_name_id_map[receive_msg.FromUserName]
    de_aes_key = UtilTool.aes_decrypt(global_chat_info[chat_id].key_info_list[0].aes_key, receive_msg.Text.lstrip(owner_name))
    global_chat_info[chat_id].aes_key = de_aes_key
    global_chat_info[chat_id].is_ready = True
    print("密钥协商完成，开始加密聊天")


def get_friends():
    friends = itchat.get_friends(update=True)  # 获取微信好友列表，如果设置update=True将从服务器刷新列表


def get_friends_chat_name(nick_name):
    if nick_name in friends_list.keys():
        return friends_list[nick_name]
    else:
        return ""


def get_owner_user_name():
    global owner_name
    friends = itchat.get_friends(update=True)
    owner = friends[0]
    if WX_KEY_USERNAME in owner:
        owner_name = owner[WX_KEY_USERNAME]
    else:
        owner_name = ""


def init_friends():
    friends = itchat.get_friends(update=True)  # 获取微信好友列表，如果设置update=True将从服务器刷新列表
    global friends_list
    for f in friends:
        if f.RemarkName != "":
            friends_list[f.RemarkName] = f.UserName
        else:
            friends_list[f.NickName] = f.UserName

        new_friend = FriendInfo()
        new_friend.use_name = f.UserName
        new_friend.nick_name = f.NickName
        new_friend.remark_name = f.RemarkName
        global_friend_info[f.UserName] = new_friend

        global_name_id_map[f.UserName] = ""
    global cur_chatter

    itchat.get_chatrooms(update=True)
    cur_chatter = friends_list[cur_chatter_name]


# 获取聊天室信息
def init_chatrooms():
    rooms = itchat.get_chatrooms(update=True)
    for _, val in enumerate(rooms):
        chat_room = ChatRoomInfo()
        chat_room.nick_name = val.NickName
        chat_room.use_name = val.UserName
        chat_room.member_count = val.MemberCount
        global_chat_room_info[val.NickName] = chat_room
        global_name_id_map[val.UserName] = ""


def init_mychat():
    #  获取朋友列表
    init_friends()
    # 获取用户本身用户名
    get_owner_user_name()

    # 删除无用的密钥文件
    UtilTool.remove_unused_file()

    print("init success")


def send_chat_id(user_name):
    chat_id = UtilTool.gen_chat_id()
    itchat.send_msg("%%%%" + chat_id, toUserName=user_name)

    new_chat = ChatInfo()
    new_chat.chat_user_name = user_name
    new_chat.is_chat_id_ready = False
    global_chat_info[chat_id] = new_chat

    global_name_id_map[user_name] = chat_id

    return


if __name__ == '__main__':
    itchat.auto_login()  # hotReload=True
    init_mychat()
    # 启动线程
    t1 = threading.Thread(target=say)
    t2 = threading.Thread(target=listen, args=(u'',))
    t1.start()
    t2.start()

    itchat.run()
