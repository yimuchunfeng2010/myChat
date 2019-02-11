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

# global_cur_chatter_name = "起风了"
global_cur_chatter_name = "贝贝奶奶"

global_cur_chatter = ""
friends_list = {}

global_chat_info = dict()

global_name_id_map = dict()

# 聊天室信息
global_chat_room_info = dict()

# 好友信息
global_friend_info = dict()


@with_goto
def say():
    global global_cur_chatter
    while True:
        print('我: ', end='')
        my_msg = input()

        # 选择/切换聊天对象
        if my_msg.startswith(CHAT_START):
            user_name = my_msg.lstrip("$chat ")
            pro_key_agreement(user_name)
            continue

        # 协商完成,加密通信
        if is_key_agreement_ready():
            chat_id = global_name_id_map[global_cur_chatter]
            # 加密信息
            en_msg = UtilTool.aes_encrypt(global_chat_info[chat_id].aes_key, my_msg)
            itchat.send_msg(en_msg, toUserName=global_cur_chatter)
        else:
            print("密钥协商未完成，请等待协商完成")


# 微信消息类型 TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, VIDEO
@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True, isMpChat=True)
@with_goto
def listen(receive_msg):
    print('Receive New Msg:', receive_msg)
    global owner_name

    if not hasattr(receive_msg, 'Text'):
        return
        # 接收到chat_id
    if receive_msg.Text.startswith(CHAT_ID_START):
        chat_id = receive_msg.Text.lstrip(CHAT_ID_START)
        new_chat = ChatInfo()
        new_chat.chat_user_name = receive_msg.FromUserName
        new_chat.is_id_ready = True
        global_chat_info[chat_id] = new_chat

        global_name_id_map[receive_msg.FromUserName] = chat_id

        # 发送确认消息
        itchat.send_msg(CHAT_ID_ACK + receive_msg.Text.lstrip(CHAT_ID_START), toUserName=receive_msg.FromUserName)
        return
    # 接受到chat_id确认消息
    if receive_msg.Text.startswith(CHAT_ID_ACK):
        chat_id = receive_msg.Text.lstrip(CHAT_ID_ACK)
        if chat_id in global_chat_info:
            print('chat id 协商完成')
            global_chat_info[chat_id].is_id_ready = True

        else:
            print('聊天ID协商异常，程序退出', chat_id)
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
    if receive_msg.Text.startswith(owner_name) and receive_msg.FromUserName in global_name_id_map:
        print('密钥协商步骤四')
        key_agreement_step_four(receive_msg)
        print('密钥协商完成，开始加密聊天')
        return

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
    if global_cur_chatter == '':
        print('someone:', de_receive_msg)
    else:
        print(chatter, '：', de_receive_msg)


# 发起协商，生成RSA密钥对，并将公钥发给好友，密钥协商步骤一
def key_agreement_step_one(chat_id):
    # 生成RSA密钥对
    if chat_id in global_chat_info:
        user_name = global_chat_info[chat_id].chat_user_name
    else:
        print('未找到用户名')
        return
    public_key_name, private_key_name = UtilTool.gen_ras_key(user_name)
    mutex.acquire(timeout=10)

    # 计算预期确认消息数
    if user_name.startswith(FROM_CHATROOM):
        chat_room_info = itchat.search_chatrooms(userName=user_name)
        global_chat_info[chat_id].except_ack_count = chat_room_info['MemberCount'] - 1
    else:
        global_chat_info[chat_id].except_ack_count = 1

    # 记录密钥
    global_chat_info[chat_id].rsa_private_key_name = MINE_KEY_PATH + private_key_name
    global_chat_info[chat_id].rsa_public_key_name = MINE_KEY_PATH + public_key_name
    mutex.release()

    # 发送RSA公钥文件
    itchat.send_file(global_chat_info[chat_id].rsa_public_key_name, toUserName=user_name)


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
            key_info = KeyInfo()
            key_info.aes_key = UtilTool.gen_aes_key()
            key_info.time_stamp = str(int(time.time()))

            global_chat_info[global_name_id_map[receive_msg.FromUserName]].key_info_list.append(key_info)

            # 用rsa公钥加密aes密钥, 接收方用rsa私钥进行解密
            aes_msg = UtilTool.encrypt_rsa_by_public_file(FRIEND_KEY_PATH + receive_msg['FileName'],
                                                          key_info.aes_key)

            # AES_KEY，表示后序消息内容是rsa公钥加密过的aes密钥信息
            aes_msg = AES_KEY + aes_msg + CONNECTOR + owner_name

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

    key_info = KeyInfo()
    key_info.user_name = my_msg[index + len(CONNECTOR):]
    key_info.time_stamp = UtilTool.get_cur_time_stamp()
    key_info.aes_key = aes_key.decode()

    # 加入aes密钥列表
    global_chat_info[chat_id].key_info_list.append(key_info)

    # 若已获取足够确认信息，则向aes密钥协商完成，发送最终aes密钥
    if global_chat_info[chat_id].actual_ack_count == \
            global_chat_info[chat_id].except_ack_count:

        if len(global_chat_info[chat_id].key_info_list) == 0:
            print('aes empty')
            return
        global_chat_info[chat_id].aes_key = key_info.aes_key  # todo 暂时定为最后一个密钥为公用密钥

        # 将公用aes密钥用每个好友各自的aes加密后发送
        for item in global_chat_info[chat_id].key_info_list:
            key_msg = UtilTool.aes_encrypt(item.aes_key, global_chat_info[chat_id].aes_key)
            send_msg = item.user_name + key_msg
            itchat.send_msg(send_msg, toUserName=receive_msg.FromUserName)

        print("密钥协商完成，开始加密聊天")
        global_chat_info[chat_id].is_chat_ready = True
        return


# 向所有聊天好友发送协商一致的aes密钥，密钥协商步骤四
def key_agreement_step_four(receive_msg):
    chat_id = global_name_id_map[receive_msg.FromUserName]
    de_aes_key = UtilTool.aes_decrypt(global_chat_info[chat_id].key_info_list[0].aes_key,
                                      receive_msg.Text.lstrip(owner_name))
    global_chat_info[chat_id].aes_key = de_aes_key
    global_chat_info[chat_id].is_chat_ready = True


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
    global global_cur_chatter

    itchat.get_chatrooms(update=True)
    global_cur_chatter = friends_list[global_cur_chatter_name]


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

    print('init success')


def id_agreement(user_name):
    chat_id = UtilTool.gen_chat_id()
    itchat.send_msg(CHAT_ID_START + chat_id, toUserName=user_name)

    new_chat = ChatInfo()
    new_chat.chat_user_name = user_name
    new_chat.is_id_ready = False
    global_chat_info[chat_id] = new_chat

    global_name_id_map[user_name] = chat_id

    return


def pro_key_agreement(user_name):
    #  查询user_id
    global friends_list
    global global_cur_chatter
    s_chatter = friends_list[user_name]

    # 判断是否已经加密
    if s_chatter in global_name_id_map and global_name_id_map[s_chatter] in global_chat_info and \
            global_chat_info[global_name_id_map[s_chatter]].is_chat_ready is True:
        # 密钥协商已完成，直接切换用户
        global_cur_chatter = s_chatter
    else:
        # 协商聊天id
        id_agreement(s_chatter)
        # 等待chat_id协商完成，超时则返回
        cnt = 0
        while global_chat_info[global_name_id_map[s_chatter]].is_id_ready is False:
            time.sleep(1)
            # 5s超时
            if cnt >= 5:
                print("聊天ID超时")
                return

        print("密钥协商步骤一")
        key_agreement_step_one(global_name_id_map[s_chatter])

        cnt = 0
        while global_chat_info[global_name_id_map[s_chatter]].is_chat_ready is not True:
            time.sleep(1)
            # 10s超时
            if cnt >= 10:
                print("等待聊天协商完成超时,程序异常退出")
                return
        # 密钥协商成功，切换当前聊天对象
        global_cur_chatter = s_chatter


def is_key_agreement_ready():
    if global_cur_chatter in global_name_id_map:
        chat_id = global_name_id_map[global_cur_chatter]
        if chat_id in global_chat_info and global_chat_info[chat_id].is_chat_ready is True:
            return True
    else:
        return False

if __name__ == '__main__':
    itchat.auto_login()  # hotReload=True
    init_mychat()
    # 启动线程
    t1 = threading.Thread(target=say)
    t2 = threading.Thread(target=listen, args=(u'',))
    t1.start()
    t2.start()

    itchat.run()
