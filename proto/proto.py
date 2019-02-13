# -*- coding: utf-8 -*-
import itchat
from constants.type import *
from proto.info import *

""""密钥协议文件"""


class IdAgreement(object):

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
