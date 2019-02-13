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

# 消息来源类型
FROM_CHATROOM = '@@'  # 聊天室消息
FROM_FRIEND = '@'  # 好友消息

# 密钥协商特殊字符串
CHAT_START = '@'
CHAT_ID_START = '%CHAT_ID_START%'
CHAT_ID_ACK = '%CHAT_ID_ACK%'
AES_KEY = '%AES_KEY%'
CONNECTOR = '%__%'

# 密钥文件存放路径
MINE_KEY_PATH = "./key_module/key_files/mine/"
FRIEND_KEY_PATH = "./key_module/key_files/friend/"

# 密钥文件后缀
PUBLIC_KEY_SUFFIX = 'id_rsa.pub'

# 微信消息类型
WX_ATTACHMENT = 'Attachment'
WX_TEXT = 'Text'
