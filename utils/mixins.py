#!/usr/bin/env python3


class BitMixin(object):
    """位操作mixin"""

    def __init__(self):
        self.state = 0

    def SetBit(self, flag):
        self.state |= flag

    def ResetBit(self, flag):
        self.state &= ~flag

    def Clear(self, defaultFlag=0):
        self.state = defaultFlag
