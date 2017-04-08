#!/usr/bin/env python3

from graphics.base.Color import Color


class RenderBuffer(object):
    DefaultWidth = 800
    DefaultHeight = 800

    def __init__(self, width=DefaultWidth, height=DefaultHeight, color=Color()):
        self.width = width
        self.height = height
        self.data = [[color for i in range(self.width)] for j in range(self.height)]

    def Get(self, pos):
        return self.data[pos[0]][pos[1]]

    def Set(self, pos, color):
        assert isinstance(color, Color), 'The param color is not a instance of Color'
        self.data[pos[0]][pos[1]] = color

    def __str__(self):
        result = []
        for line in self.data:
            for item in line:
                result.append(str(item))
                result.append(' ')
            result.append('\n')
        return ''.join(result)
