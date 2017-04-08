#!/usr/bin/env python3

from graphics.base.Color import Color
from lib.math.Vector4 import Vector4


class Vertex(object):
    def __init__(self):
        self.pos = Vector4()
        self.normal = Vector4()
        self.textureCoord = (0, 0)
        self.color = Color()

    def SetPosition(self, pos):
        self.pos.x = pos[0]
        self.pos.y = pos[1]
        self.pos.z = pos[2]

    def __str__(self):
        return 'Pos: {0}'.format(self.pos)
