from system_executor.system_object import  *


class SysMessage(SysObject):
    def __init__(self, src_name="", dst_name=""):
        self._src = src_name
        self._dst = dst_name
        self._msg_list = []

    def insert(self, msg):
        self._msg_list.append(msg)

    def retrieve(self):
        return self._msg_list

    def get_src(self):
        return self._src

    def get_dst(self):
        return self._dst
