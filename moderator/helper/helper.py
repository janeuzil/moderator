class Params(object):
    def __init__(self):
        self.spark = object()
        self.db = object()
        self.me = object()
        self.cmd = object()
        self.ans = object()
        self.admin = str()
        self.moderators = str()
        self.lang = str()
        self.mention = str()
        self.var = [
            "MODERATOR_URL",
            "MODERATOR_LANG",
            "SPARK_ACCESS_TOKEN",
            "ADMIN_ROOM",
            "MODERATORS_ROOM",
            "DB_HOST",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWD"
        ]
        self.direct = "direct"
        self.group = "group"


class ServerExit(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
