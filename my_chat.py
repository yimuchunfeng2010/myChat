# -*- coding: utf-8 -*-
import itchat
import sys
import importlib
import threading
from constants.type import *
from itchat.content import *
from proto.info import *

sys.path.append(os.getcwd() + '/constants')

importlib.reload(sys)

my_id = ''
mutex = threading.Lock()

global_cur_chatter_name = "AA"
# global_cur_chatter_name = "贝贝奶奶"

global_cur_chatter_id = ""

# 好友信息表(包括群) remark_name -> user_id
global_friends_list = dict()

# 聊天信息 chat_id -> chat_info()
global_chat_info = dict()

# 用户ID与聊天ID映射表 user_id -> chat_id
global_name_id_map = dict()

# 好友信息 user_id -> friend_info()
global_friend_info = dict()


def say():
    global global_cur_chatter_id
    while True:
        my_msg = input()
        print('我: ', end='')

        # 选择/切换聊天对象
        if my_msg.startswith(CHAT_START):
            user_name = my_msg.lstrip(CHAT_START)
            launch_key_agreement(user_name)
            continue

        # 协商完成,加密通信
        if is_key_agreement_ready():
            chat_id = global_name_id_map[global_cur_chatter_id]
            # 加密信息
            en_msg = UtilTool.aes_encrypt(global_chat_info[chat_id].aes_key, my_msg)
            itchat.send_msg(en_msg, toUserName=global_cur_chatter_id)
        else:
            print("密钥协商未完成，请等待协商完成")


# 微信消息类型 TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, VIDEO
@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True, isMpChat=True)
def listen(receive_msg):
    print('Receive New Msg:', receive_msg)
    global my_id

    if not hasattr(receive_msg, 'Text'):
        return

    # 接收到chat_id
    if receive_msg.Text.startswith(CHAT_ID_START):
        id_ack(receive_msg)
        return

    # 接受到chat_id确认消息
    if receive_msg.Text.startswith(CHAT_ID_ACK):
        chat_id = receive_msg.Text.lstrip(CHAT_ID_ACK)
        if chat_id in global_chat_info:
            global_chat_info[chat_id].expect_ack_count += 1
        else:
            print('聊天ID协商异常，程序退出')
        return

    #  收到aes密钥，返回密钥协商步骤三
    if receive_msg.Text.startswith(AES_KEY):
        print('密钥协商步骤三')
        if receive_msg.FromUserName not in global_name_id_map:
            print('密钥协商异常, 程序退出')
        else:
            key_agreement_step_three(receive_msg)
        return

    # 保存aes密钥, 密钥协商步骤四
    if receive_msg.Text.startswith(my_id) and receive_msg.FromUserName in global_name_id_map:
        print('密钥协商步骤四')
        key_agreement_step_four(receive_msg)
        print('密钥协商完成，开始加密聊天')
        return

    # 开始加密聊天
    encrypt_chat(receive_msg)


# 发起id协商
def id_agreement(user_id):
    chat_id = UtilTool.gen_chat_id()
    itchat.send_msg(CHAT_ID_START + chat_id, toUserName=user_id)

    new_chat = ChatUnit()
    new_chat.user_id = user_id
    new_chat.is_id_ready = False
    global_chat_info[chat_id] = new_chat

    global_name_id_map[user_id] = chat_id

    return


# 响应确认id协商
def id_ack(receive_msg):
    global global_chat_info
    global global_name_id_map

    chat_id = receive_msg.Text.lstrip(CHAT_ID_START)
    new_chat = ChatUnit()
    new_chat.user_id = receive_msg.FromUserName
    new_chat.is_id_ready = True
    global_chat_info[chat_id] = new_chat

    global_name_id_map[receive_msg.FromUserName] = chat_id

    # 发送确认消息
    itchat.send_msg(CHAT_ID_ACK + receive_msg.Text.lstrip(CHAT_ID_START), toUserName=receive_msg.FromUserName)


# 发起协商，生成RSA密钥对，并将公钥发给好友，密钥协商步骤一
def key_agreement_step_one(chat_id):
    # 生成RSA密钥对
    if chat_id in global_chat_info:
        user_id = global_chat_info[chat_id].user_id
    else:
        print('未找到用户名')
        return
    public_key_name, private_key_name = UtilTool.gen_ras_key(user_id)
    mutex.acquire(timeout=10)

    # 记录密钥
    global_chat_info[chat_id].rsa_private_key_name = MINE_KEY_PATH + private_key_name
    global_chat_info[chat_id].rsa_public_key_name = MINE_KEY_PATH + public_key_name
    mutex.release()

    # 发送RSA公钥文件
    itchat.send_file(global_chat_info[chat_id].rsa_public_key_name, toUserName=user_id)


# 密钥协商步骤二， 收到rsa公钥文件，本地生成aes秘钥并用rsa公钥加密发送给加密通信协商发起者
@itchat.msg_register([ATTACHMENT], isFriendChat=True, isGroupChat=True, isMpChat=True)
def key_agreement_step_two(receive_msg):
    print('密钥协商步骤二')
    print('receive file', receive_msg)
    if hasattr(receive_msg, 'Content') and PUBLIC_KEY_SUFFIX in receive_msg.Content:
        # 接收到rsa公钥文件
        receive_msg.text(FRIEND_KEY_PATH + receive_msg['FileName'])

        # 记录公钥文件名(存在初始协商或者正在聊天中两种场景)
        if receive_msg.FromUserName in global_name_id_map:
            global_chat_info[global_name_id_map[receive_msg.FromUserName]].rsa_public_key_name = receive_msg.FileName

            # 生成aes公钥
            key_info = KeyInfo("", UtilTool.gen_aes_key(), UtilTool.get_cur_time_stamp())

            global_chat_info[global_name_id_map[receive_msg.FromUserName]].key_info_list.append(key_info)

            # 用rsa公钥加密aes密钥, 接收方用rsa私钥进行解密
            aes_msg = UtilTool.encrypt_rsa_by_public_file(FRIEND_KEY_PATH + receive_msg['FileName'],
                                                          key_info.aes_key)

            # AES_KEY，表示后序消息内容是rsa公钥加密过的aes密钥信息
            aes_msg = AES_KEY + aes_msg + CONNECTOR + my_id

            itchat.send_msg(aes_msg, toUserName=receive_msg.FromUserName)
    else:
        print("receive file： ", receive_msg.FileName)


# 收到好友AES密钥确认,密钥协商步骤三
def key_agreement_step_three(receive_msg):
    chat_id = global_name_id_map[receive_msg.FromUserName]
    global_chat_info[chat_id].actual_ack_count += 1

    my_msg = receive_msg.Text.lstrip(AES_KEY)
    index = my_msg.find(CONNECTOR)
    en_msg = my_msg[:index]

    aes_key = UtilTool.decrypt_rsa_by_private_file(global_chat_info[chat_id].rsa_private_key_name, en_msg)

    key_info = KeyInfo(my_msg[index + len(CONNECTOR):], aes_key.decode(), UtilTool.get_cur_time_stamp())

    # 加入aes密钥列表
    global_chat_info[chat_id].key_info_list.append(key_info)

    # 若已获取足够确认信息，则向aes密钥协商完成，发送最终aes密钥
    if global_chat_info[chat_id].actual_ack_count == \
            global_chat_info[chat_id].expect_ack_count:

        if len(global_chat_info[chat_id].key_info_list) == 0:
            print('aes empty')
            return
        global_chat_info[chat_id].aes_key = key_info.aes_key  # todo 暂时定为最后一个密钥为公用密钥

        # 将公用aes密钥用每个好友各自的aes加密后发送
        for item in global_chat_info[chat_id].key_info_list:
            key_msg = UtilTool.aes_encrypt(item.aes_key, global_chat_info[chat_id].aes_key)
            send_msg = item.user_id + key_msg
            itchat.send_msg(send_msg, toUserName=receive_msg.FromUserName)

        print("密钥协商完成，开始加密聊天")
        global_chat_info[chat_id].is_chat_ready = True
        global_chat_info[chat_id].chat_master = True
        global_chat_info[chat_id].time = UtilTool.get_cur_time_stamp()

        return


# 向所有聊天好友发送协商一致的aes密钥，密钥协商步骤四
def key_agreement_step_four(receive_msg):
    chat_id = global_name_id_map[receive_msg.FromUserName]
    de_aes_key = UtilTool.aes_decrypt(global_chat_info[chat_id].key_info_list[0].aes_key,
                                      receive_msg.Text.lstrip(my_id))
    global_chat_info[chat_id].aes_key = de_aes_key
    global_chat_info[chat_id].is_chat_ready = True
    global_chat_info[chat_id].time = UtilTool.get_cur_time_stamp()


def init_friends():
    #  获取好友信息
    global global_friends_list
    global my_id
    friends = itchat.get_friends(update=True)  # 获取微信好友列表，如果设置update=True将从服务器刷新列表
    my_id = friends[0].UserName

    for friend in friends:
        if friend.RemarkName != "":
            global_friends_list[friend.RemarkName] = friend.UserName
        else:
            global_friends_list[friend.NickName] = friend.UserName

        global_friend_info[friend.UserName] = FriendInfo(friend.UserName, friend.NickName, friend.RemarkName, 1)

        global_name_id_map[friend.UserName] = ""


def init_rooms():
    # 获取群信息
    rooms = itchat.get_chatrooms(update=True)
    for room in rooms:
        if room.RemarkName != "":
            global_friends_list[room.RemarkName] = room.UserName
        else:
            global_friends_list[room.NickName] = room.UserName

        global_friend_info[room.UserName] = FriendInfo(room.UserName, room.NickName, room.RemarkName, room.MemberCount)

        global_name_id_map[room.UserName] = ""


def init_current_friend():
    global global_cur_chatter_id
    global_cur_chatter_id = global_friends_list[global_cur_chatter_name]


def init_mychat():
    # 初始化朋友列表
    init_friends()

    # 初始化好友群信息
    init_rooms()

    # 初始化当前聊天好友
    init_current_friend()

    # 删除无用的密钥文件
    UtilTool.remove_unused_file()

    print('init success')


def launch_key_agreement(user_name):
    #  查询user_id
    global global_friends_list
    global global_cur_chatter_id
    if user_name in global_friends_list:
        user_id = global_friends_list[user_name]
    else:
        print("用户不存在，请输入正确的用户名")
        return

    # 判断是否已经加密
    if user_id in global_name_id_map and global_name_id_map[user_id] in global_chat_info and \
            global_chat_info[global_name_id_map[user_id]].is_chat_ready is True:
        # 密钥协商已完成，直接切换用户
        global_cur_chatter_id = user_id
    else:

        # 协商聊天id及测试好友加密聊天在线人数
        id_agreement(user_id)

        # 延时10s,以等待好友响应id_ack
        time.sleep(10)

        if global_chat_info[global_name_id_map[user_id]].expect_ack_count == 0:
            print("当前无好友加密聊天在线")
            return

        # 设置id_ready 状态
        global_chat_info[global_name_id_map[user_id]].is_id_ready = True
        print("ID协商完成")

        print("密钥协商步骤一")
        key_agreement_step_one(global_name_id_map[user_id])

        cnt = 0
        while global_chat_info[global_name_id_map[user_id]].is_chat_ready is not True:
            time.sleep(1)
            # 10s超时
            if cnt >= 10:
                print("等待聊天协商完成超时,程序异常退出")
                return
        # 密钥协商成功，切换当前聊天对象
        global_cur_chatter_id = user_id


def is_key_agreement_ready():
    if global_cur_chatter_id in global_name_id_map:
        chat_id = global_name_id_map[global_cur_chatter_id]
        if chat_id in global_chat_info and global_chat_info[chat_id].is_chat_ready is True:
            return True
    else:
        return False


def encrypt_chat(receive_msg):
    global global_name_id_map
    global global_chat_info
    global global_friend_info
    global global_cur_chatter_id

    if receive_msg.FromUserName in global_name_id_map:
        chat_id = global_name_id_map[receive_msg.FromUserName]
        if global_chat_info[chat_id].is_chat_ready is True:
            de_receive_msg = UtilTool.aes_decrypt(global_chat_info[chat_id].aes_key, receive_msg.Text)
        else:
            de_receive_msg = receive_msg
    else:
        de_receive_msg = receive_msg

    chatter = ''
    if receive_msg.FromUserName in global_friend_info:
        if global_friend_info[receive_msg.FromUserName].remark_name != '':
            chatter = global_friend_info[receive_msg.FromUserName].remark_name
        else:
            chatter = global_friend_info[receive_msg.FromUserName].nick_name
    if global_cur_chatter_id == '':
        print('someone:', de_receive_msg)
    else:
        print(chatter, '：', de_receive_msg)


if __name__ == '__main__':
    itchat.auto_login()  # hotReload=True
    init_mychat()
    # 启动线程
    t1 = threading.Thread(target=say)
    t2 = threading.Thread(target=listen, args=(u'',))
    t1.start()
    t2.start()

    itchat.run()
