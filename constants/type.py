# 微信消息类型
MSG_TYPE__TEXT = 'Text'  # 文本消息
MSG_TYPE__FRIENDS = 'Friends'  # 好友推荐
MSG_TYPE__ATTACHMENT = 'Attachment'  # 附件
MSG_TYPE__VIDEO = 'Video'  # 视频
MSG_TYPE__PICTURE = 'Picture'  # 图片
MSG_TYPE__RECORDING = 'Recording'  # 音频
MSG_TYPE__CARD = 'Video'  # 名片
MSG_TYPE__MAP = 'Video'  # 地图
MSG_TYPE__SHARING = 'Video'  # 分享

MSG_TYPE = [MSG_TYPE__TEXT, MSG_TYPE__FRIENDS, MSG_TYPE__ATTACHMENT, MSG_TYPE__VIDEO, MSG_TYPE__PICTURE,
            MSG_TYPE__RECORDING, MSG_TYPE__CARD, MSG_TYPE__MAP, MSG_TYPE__SHARING]

# 特殊字符串
PUBLIC_KEY_PREFIX = '$@@$'  # RSA公钥前缀
SECRET_KEY_PREFIX = '@$$@'  # AES密钥前缀
FINAL_AES_KEY_PREFIX = '%**%' # 协商一致AES密钥前缀

# 消息来源类型
FROM_CHATROOM = '@@' # 聊天室消息
FROM_FRIEND = '@' # 好友消息