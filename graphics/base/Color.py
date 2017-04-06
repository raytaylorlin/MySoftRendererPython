#!/usr/bin/env python3


class Color(object):
    def __init__(self, r=0, g=0, b=0, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @property
    def tuple(self):
        return self.r, self.g, self.b, self.a

    def __str__(self):
        return str((self.r, self.g, self.b, self.a))
