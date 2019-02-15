# -*- coding: utf-8 -*-
import itchat
import time
from constants.type import *
from constants.enum import *
from proto.info import *
from proto.util import UtilTool

"""密钥协议文件"""


class IdAgreement(object):
    """ID协商"""

    def __init__(self):
        pass

    # 发起id协商
    @staticmethod
    def id_agreement(user_id, in_my_info):
        chat_id = UtilTool.gen_chat_id()
        itchat.send_msg(CHAT_ID_START + chat_id, toUserName=user_id)

        new_chat = ChatUnit()
        new_chat.user_id = user_id
        new_chat.is_id_ready = False
        new_chat.set_agreement_step(ID_STEEP_ONE)
        in_my_info.set_chat_id_to_chat_info(chat_id, new_chat)

        in_my_info.set_user_id_to_chat_id(user_id, chat_id)

        return

    # 响应确认id协商
    @staticmethod
    def id_ack(receive_msg, in_my_info):
        chat_id = receive_msg.Text.lstrip(CHAT_ID_START)
        new_chat = ChatUnit()
        new_chat.user_id = receive_msg.FromUserName
        new_chat.is_id_ready = True
        new_chat.set_agreement_step(ID_STEEP_TWO)

        in_my_info.set_chat_id_to_chat_info(chat_id, new_chat)

        in_my_info.set_user_id_to_chat_id(receive_msg.FromUserName, chat_id)

        # 发送确认消息
        itchat.send_msg(CHAT_ID_ACK + receive_msg.Text.lstrip(CHAT_ID_START), toUserName=receive_msg.FromUserName)

    @staticmethod
    def is_key_agreement_ready(in_my_info, cur_chatter_id):
        if in_my_info.check_user_id_to_chat_id(cur_chatter_id):
            chat_id = in_my_info.get_user_id_to_chat_id(cur_chatter_id)
            if in_my_info.check_chat_id_to_chat_info(chat_id):
                chat_info = in_my_info.get_chat_id_to_chat_info(chat_id)
                if chat_info.is_chat_ready is True:
                    return True
        else:
            return False


class KeyAgreement(object):
    """密钥协商"""

    def __init__(self):
        pass

    # 发起协商，生成RSA密钥对，并将公钥发给好友，密钥协商步骤一
    @staticmethod
    def key_agreement_step_one(chat_id, in_my_info):
        # 生成RSA密钥对
        if in_my_info.check_chat_id_to_chat_info(chat_id) is False:
            print('未找到用户名')
            return

        chat_info = in_my_info.get_chat_id_to_chat_info(chat_id)
        user_id = chat_info.user_id

        public_key_name, private_key_name = UtilTool.gen_rsa_key(user_id)

        # 记录密钥
        chat_info.rsa_private_key_name = MINE_KEY_PATH + private_key_name
        chat_info.rsa_public_key_name = MINE_KEY_PATH + public_key_name

        # 更新密钥协商步骤
        chat_info.set_agreement_step(KEY_STEEP_ONE)

        # 发送RSA公钥文件
        itchat.send_file(chat_info.rsa_public_key_name, toUserName=user_id)

    # # 密钥协商步骤二， 收到rsa公钥文件，本地生成aes秘钥并用rsa公钥加密发送给加密通信协商发起者
    @staticmethod
    def key_agreement_step_two(receive_msg, in_my_id, in_my_info):
        print('密钥协商步骤二')
        print('receive file', receive_msg)
        if hasattr(receive_msg, 'Content') and PUBLIC_KEY_SUFFIX in receive_msg.Content:
            # 接收到rsa公钥文件
            receive_msg.text(FRIEND_KEY_PATH + receive_msg['FileName'])

            # 记录公钥文件名(存在初始协商或者正在聊天中两种场景)
            if in_my_info.check_user_id_to_chat_id(receive_msg.FromUserName):
                chat_id = in_my_info.get_user_id_to_chat_id(receive_msg.FromUserName)

                # 生成aes公钥
                key_info = KeyInfo("", UtilTool.gen_aes_key(), UtilTool.get_cur_time_stamp())

                chat_info = in_my_info.get_chat_id_to_chat_info(chat_id)
                chat_info.rsa_public_key_name = receive_msg.FileName
                chat_info.key_info_list.append(key_info)

                # 更新密钥协商步骤
                chat_info.set_agreement_step(KEY_STEEP_TWO)

                # 用rsa公钥加密aes密钥, 接收方用rsa私钥进行解密
                aes_msg = UtilTool.encrypt_rsa_by_public_file(FRIEND_KEY_PATH + receive_msg['FileName'],
                                                              key_info.aes_key)

                # AES_KEY，表示后序消息内容是rsa公钥加密过的aes密钥信息
                aes_msg = AES_KEY + aes_msg + CONNECTOR + in_my_id
                itchat.send_msg(aes_msg, toUserName=receive_msg.FromUserName)
        else:
            print("receive file： ", receive_msg.FileName)

    # 收到好友AES密钥确认,密钥协商步骤三
    @staticmethod
    def key_agreement_step_three(receive_msg, in_my_info):
        chat_id = in_my_info.get_user_id_to_chat_id(receive_msg.FromUserName)
        chat_info = in_my_info.get_chat_id_to_chat_info(chat_id)
        chat_info.actual_ack_count += 1

        # 更新密钥协商步骤
        chat_info.set_agreement_step(KEY_STEEP_THR)

        my_msg = receive_msg.Text.lstrip(AES_KEY)
        index = my_msg.find(CONNECTOR)
        en_msg = my_msg[:index]

        aes_key = UtilTool.decrypt_rsa_by_private_file(chat_info.rsa_private_key_name, en_msg)

        key_info = KeyInfo(my_msg[index + len(CONNECTOR):], aes_key.decode(), UtilTool.get_cur_time_stamp())

        # 加入aes密钥列表
        chat_info.key_info_list.append(key_info)

        # 若已获取足够确认信息，则向aes密钥协商完成，发送最终aes密钥
        if chat_info.actual_ack_count == chat_info.expect_ack_count:
            if len(chat_info.key_info_list) == 0:
                print('aes empty')
                return
            chat_info.aes_key = key_info.aes_key  # todo 暂时定为最后一个密钥为公用密钥

            # 将公用aes密钥用每个好友各自的aes加密后发送
            for item in chat_info.key_info_list:
                key_msg = UtilTool.aes_encrypt(item.aes_key, chat_info.aes_key)
                send_msg = item.user_id + key_msg

                itchat.send_msg(send_msg, toUserName=receive_msg.FromUserName)

            print("密钥协商完成，开始加密聊天")
            chat_info.is_chat_ready = True
            chat_info.chat_master = True
            chat_info.time = UtilTool.get_cur_time_stamp()
            #  设置密钥协商步骤为已完成
            chat_info.set_agreement_step(KEY_STEEP_FOUR)

            # 恢复初始状态
            chat_info.set_agreement_step(AGREEMENT_INIT)

            return

    # 向所有聊天好友发送协商一致的aes密钥，密钥协商步骤四
    @staticmethod
    def key_agreement_step_four(receive_msg, in_my_id, in_my_info):
        chat_id = in_my_info.get_user_id_to_chat_id(receive_msg.FromUserName)
        chat_info = in_my_info.get_chat_id_to_chat_info(chat_id)

        de_aes_key = UtilTool.aes_decrypt(chat_info.key_info_list[0].aes_key,
                                          receive_msg.Text[len(in_my_id):])
        chat_info.aes_key = de_aes_key
        chat_info.is_chat_ready = True
        chat_info.time = UtilTool.get_cur_time_stamp()

        # 更新密钥协商步骤
        chat_info.set_agreement_step(KEY_STEEP_FOUR)

        # 完成密钥协商，恢复状态
        chat_info.set_agreement_step(AGREEMENT_INIT)

    #  发起密钥协商
    @staticmethod
    def launch_key_agreement(user_name, in_my_info):
        #  查询user_id
        if in_my_info.check_user_name_to_user_id(user_name) is False:
            print("用户不存在，请输入正确的用户名")
            return

        user_id = in_my_info.get_user_name_to_user_id(user_name)

        # 判断是否已经加密
        if in_my_info.check_user_id_to_chat_id(user_id) and in_my_info.check_chat_id_to_chat_info(user_id):
            chat_id = in_my_info.get_user_id_to_chat_id(user_id)
            chat_info = in_my_info.get_chat_id_to_chat_info(chat_id)
            if chat_info.is_chat_ready is True:  # 加密已完成，直接切换
                # 密钥协商已完成，直接切换用户
                pass

            if chat_info.is_chat_ready is False and chat_info.is_agreement_processing() is True:
                print("密钥协商中，请稍等")
        else:

            # 协商聊天id及测试好友加密聊天在线人数
            IdAgreement.id_agreement(user_id, in_my_info)

            # 等待好友响应id_ack
            time.sleep(ID_WAIT_TIME)

            chat_id = in_my_info.get_user_id_to_chat_id(user_id)
            chat_info = in_my_info.get_chat_id_to_chat_info(chat_id)

            if chat_info.expect_ack_count == 0:
                print("当前无好友加密聊天在线")
                return

            # 设置id_ready 状态
            chat_info.is_id_ready = True
            print("ID协商完成")

            print("密钥协商步骤一")
            KeyAgreement.key_agreement_step_one(in_my_info.get_user_id_to_chat_id(user_id), in_my_info)

            cnt = 0
            while chat_info.is_chat_ready is not True:
                time.sleep(1)
                # 10s超时
                if cnt >= KEY_WAIT_TIME:
                    print("等待聊天协商完成超时,程序异常退出")
                    return
        # 密钥协商成功，切换当前聊天对象
        return user_id
