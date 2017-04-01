#!/usr/bin/env python3

from graphics.core.Color import Color
from graphics.core.RenderInterface import ImageRenderer


class RenderBuffer(object):
    DefaultWidth = 800
    DefaultHeight = 800

    def __init__(self, width=DefaultWidth, height=DefaultHeight):
        self.width = width
        self.height = height
        self.data = [[Color() for i in range(self.width)] for j in range(self.height)]

    def Get(self, pos):
        return self.data[pos[0]][pos[1]]

    def Set(self, pos, color):
        if isinstance(color, Color) or (isinstance(color, tuple) and len(color) == 4):
            self.data[pos[0]][pos[1]] = color
        else:
            raise Exception('The param color is not a instance of Color or 4-tuple')

    def __str__(self):
        result = []
        for line in self.data:
            for item in line:
                result.append(str(item))
                result.append(' ')
            result.append('\n')
        return ''.join(result)
