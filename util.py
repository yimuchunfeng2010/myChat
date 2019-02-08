import os


def code_lines_count(path):
    code_lines = 0
    comm_lines = 0
    space_lines = 0
    for root, dirs, files in os.walk(path):
        for item in files:
            file_abs_path = os.path.join(root, item)
            postfix = os.path.splitext(file_abs_path)[1]
            if postfix == '.py':

                with open(file_abs_path, 'rb') as fp:
                    while True:
                        line = fp.readline()
                        if not line:

                            break
                        elif line.strip().startswith(b'#'):

                            comm_lines += 1
                        elif line.strip().startswith(b"'''") or line.strip().startswith(b'"""'):
                            comm_lines += 1
                            if line.count(b'"""') == 1 or line.count(b"'''") == 1:
                                while True:
                                    line = fp.readline()

                                    comm_lines += 1
                                    if (b"'''" in line) or (b'"""' in line):
                                        break
                        elif line.strip():

                            code_lines += 1
                        else:

                            space_lines += 1

    return code_lines, comm_lines, space_lines


if __name__ == '__main__':
    abs_dir = os.getcwd()
    x, y, z = code_lines_count(abs_dir)
    print("code_lines: ", x)
    print("comm_lines: ", y)
    print("blank_lines: ", z)




# 多线程接受用户输入，并输出打印
# # coding=utf-8
# import threading
# from time import ctime, sleep
#
# mutex = threading.Lock()
#
# msg_arr = ["zeng: haha", "li: zzz", "oo:112"]
#
#
# def say(func):
#     while True:
#         if 0 != len(msg_arr):
#             mutex.acquire(timeout=10)
#             print(msg_arr[0])
#             del msg_arr[0]
#             mutex.release()
#
#
# def listen(func):
#     while True:
#         msg = input()
#         msg = '我说：' + msg
#         # print(msg)
#         mutex.acquire(timeout=10)
#         msg_arr.append(msg)
#         mutex.release()
#
#
#
# threads = []
# t1 = threading.Thread(target=say, args=(u'爱情买卖',))
# threads.append(t1)
# t2 = threading.Thread(target=listen, args=(u'阿凡达',))
# threads.append(t2)
#
# if __name__ == '__main__':
#     # for t in threads:
#     #     t.setDaemon(True)
#     #     t.start()
#     t1.start()
#     t2.start()


# 发送文件
# itchat.send("@fil@%s" % './tmp.py',toUserName='filehelper')

# 微信好友消息
# {'MsgId': '9210430947494305964',
# 'FromUserName': '@a06cf3bd7628c92de8800964b541c7c40749d17ab8e0982466c3c5cfbe1a1991',
# 'ToUserName': '@2416b0c37fdb9fd0c8c0516ccd85ce64',
# 'MsgType': 1,
# 'Content': '如果没有这个方法，微信加密就搞不成咯',
# 'Status': 3,
# 'ImgStatus': 1,
# 'CreateTime': 1548943585,
# 'VoiceLength': 0,
# 'PlayLength': 0,
# 'FileName': '',
# 'FileSize': '',
# 'MediaId': '',
# 'Url': '',
# 'AppMsgType': 0,
# 'StatusNotifyCode': 0,
# 'StatusNotifyUserName': '',
# 'RecommendInfo': {'UserName': '',
# 'NickName': '',
# 'QQNum': 0,
# 'Province': '',
# 'City': '',
# 'Content': '',
# 'Signature': '',
# 'Alias': '',
# 'Scene': 0,
# 'VerifyFlag': 0,
# 'AttrStatus': 0,
# 'Sex': 0,
# 'Ticket': '',
# 'OpCode': 0},
# 'ForwardFlag': 0,
# 'AppInfo': {'AppID': '',
# 'Type': 0},
# 'HasProductId': 0,
# 'Ticket': '',
# 'ImgHeight': 0,
# 'ImgWidth': 0,
# 'SubMsgType': 0,
# 'NewMsgId': 9210430947494305964,
# 'OriContent': '',
# 'EncryFileName': '',
# 'User': <User: {'MemberList': <ContactList: []>,
# 'Uin': 0,
# 'UserName': '@2416b0c37fdb9fd0c8c0516ccd85ce64',
# 'NickName': '水草下的阳光',
# 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=680940750&username=@2416b0c37fdb9fd0c8c0516ccd85ce64&skey=@crypt_d24390c6_37250534949df2a9bf45dce782b29357',
# 'ContactFlag': 3,
# 'MemberCount': 0,
# 'RemarkName': '代平',
# 'HideInputBarFlag': 0,
# 'Sex': 1,
# 'Signature': '两袖清风，不带走一片云彩',
# 'VerifyFlag': 0,
# 'OwnerUin': 0,
# 'PYInitial': 'SCXDYG',
# 'PYQuanPin': 'shuicaoxiadeyangguang',
# 'RemarkPYInitial': 'DP',
# 'RemarkPYQuanPin': 'daiping',
# 'StarFriend': 0,
# 'AppAccountFlag': 0,
# 'Statues': 0,
# 'AttrStatus': 33629351,
# 'Province': '四川',
# 'City': '成都',
# 'Alias': '',
# 'SnsFlag': 17,
# 'UniFriend': 0,
# 'DisplayName': '',
# 'ChatRoomId': 0,
# 'KeyWord': 'a89',
# 'EncryChatRoomId': '',
# 'IsOwner': 0}>,
# 'Type': 'Text',
# 'Text': '如果没有这个方法，微信加密就搞不成咯'}

# 微信群消息格式
# {
#     'MsgId': '3965400580896024772',
#     'FromUserName': '@1b816e97b5d16bf354020ece0e2fe82304458439b9f0407ed072fbb15ed764de',
#     'ToUserName': '@@309dbd163eb04c822f84678fc62eac4b5653e9ea798ed21350b6ae7f0308668c',
#     'MsgType': 1,
#     'Content': '测试',
#     'Status': 3,
#     'ImgStatus': 1,
#     'CreateTime': 1548984495,
#     'VoiceLength': 0,
#     'PlayLength': 0,
#     'FileName': '',
#     'FileSize': '',
#     'MediaId': '',
#     'Url': '',
#     'AppMsgType': 0,
#     'StatusNotifyCode': 0,
#     'StatusNotifyUserName': '',
#     'ForwardFlag': 0,
#     'HasProductId': 0,
#     'Ticket': '',
#     'ImgHeight': 0,
#     'ImgWidth': 0,
#     'SubMsgType': 0,
#     'NewMsgId': 3965400580896024772,
#     'OriContent': '',
#     'EncryFileName': '',
#     'ActualNickName': '起风了',
#     'IsAt': False,
#     'ActualUserName': '@1b816e97b5d16bf354020ece0e2fe82304458439b9f0407ed072fbb15ed764de',
#     'Type': 'Text',
#     'Text': '测试'
#             'RecommendInfo':
# {
#     'UserName': '',
#     'NickName': '',
#     'QQNum': 0,
#     'Province': '',
#     'City': '',
#     'Content': '',
#     'Signature': '',
#     'Alias': '',
#     'Scene': 0,
#     'VerifyFlag': 0,
#     'AttrStatus': 0,
#     'Sex': 0,
#     'Ticket': '',
#     'OpCode': 0
# },
#
# 'AppInfo':
# {
#     'AppID': '',
#     'Type': 0
# },
#
# 'User':
# <
# Chatroom:
# {
#     'UserName': '@@309dbd163eb04c822f84678fc62eac4b5653e9ea798ed21350b6ae7f0308668c',
#     'NickName': '微信测试',
#     'Sex': 0,
#     'HeadImgUpdateFlag': 1,
#     'ContactType': 0,
#     'Alias': '',
#     'ChatRoomOwner': '@1b816e97b5d16bf354020ece0e2fe82304458439b9f0407ed072fbb15ed764de',
#     'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgetheadimg?seq=0&username=@@309dbd163eb04c822f84678fc62eac4b5653e9ea798ed21350b6ae7f0308668c&skey=@crypt_d24390c6_4236348f4e5d91b6892eb20e6293ddc0',
#     'ContactFlag': 2,
#     'MemberCount': 3,
#     'HideInputBarFlag': 0,
#     'Signature': '',
#     'VerifyFlag': 0,
#     'RemarkName': '',
#     'Statues': 1,
#     'AttrStatus': 0,
#     'Province': '',
#     'City': '',
#     'SnsFlag': 0,
#     'KeyWord': '',
#     'OwnerUin': 0,
#     'IsAdmin': None,
#     'MemberList':
# <
# ContactList:
# [
# < ChatroomMember:
# {
#     'MemberList': < ContactList: [] >,
#                                  'Uin': 0,
# 'UserName': '@390d78bd89d8138531efe73b482eae92e1598b4df1579117dcd2f31d6192760d',
# 'NickName': '娟娟',
# 'AttrStatus': 4197,
# 'PYInitial': '',
# 'PYQuanPin': '',
# 'RemarkPYInitial': '',
# 'RemarkPYQuanPin': '',
# 'MemberStatus': 0,
# 'DisplayName': '',
# 'KeyWord': ''
# }
# >,
# < ChatroomMember:
# {
#     'MemberList': < ContactList: [] >,
#                                  'Uin': 0,
# 'UserName': '@1b816e97b5d16bf354020ece0e2fe82304458439b9f0407ed072fbb15ed764de',
# 'NickName': '起风了',
# 'AttrStatus': 33558565,
# 'PYInitial': '',
# 'PYQuanPin': '',
# 'RemarkPYInitial': '',
# 'RemarkPYQuanPin': '',
# 'MemberStatus': 0,
# 'DisplayName': '',
# 'KeyWord': ''
# }
# >,
# < ChatroomMember:
# {
#     'MemberList': < ContactList: [] >,
#                                  'Uin': 0,
# 'UserName': '@cf4b56269349ee36266f9641add860777f463f05279cd8491a9427b881f94ca8',
# 'NickName': '正宗二货',
# 'AttrStatus': 4133,
# 'PYInitial': '',
# 'PYQuanPin': '',
# 'RemarkPYInitial': '',
# 'RemarkPYQuanPin': '',
# 'MemberStatus': 0,
# 'DisplayName': '',
# 'KeyWord': ''
# }
# >
# ]
# >,
#
# 'Self':
# <
# ChatroomMember:
# {
#     'MemberList': < ContactList: [] >,
#                                  'Uin': 0,
# 'UserName': '@1b816e97b5d16bf354020ece0e2fe82304458439b9f0407ed072fbb15ed764de',
# 'NickName': '起风了',
# 'AttrStatus': 33558565,
# 'PYInitial': '',
# 'PYQuanPin': '',
# 'RemarkPYInitial': '',
# 'RemarkPYQuanPin': '',
# 'MemberStatus': 0,
# 'DisplayName': '',
# 'KeyWord': ''
# }
# >
# }
# >,
# }



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

    # 获取文件名
    # ret = receive_msg.text('./' + receive_msg['FileName'])
    # print("AAAA", receive_msg['FileName'])




  # if de_receive_msg[WX_KEY_TYPE] == MSG_TYPE__TEXT:
    #     if de_receive_msg[WX_KEY_FROMUSERNAME].startswith(FROM_CHATROOM):
    #         print(de_receive_msg[WX_KEY_ACTUALNICKNAME], ": ", de_receive_msg[WX_KEY_TEXT])
    #     else:
    #         if de_receive_msg[WX_KEY_FROMUSERNAME] == owner_name:
    #             print("我说: " + de_receive_msg[WX_KEY_CONTENT])
    #         else:
    #             print(de_receive_msg[WX_KEY_USER][WX_KEY_REMARKNAME], ": ", de_receive_msg[WX_KEY_CONTENT])
