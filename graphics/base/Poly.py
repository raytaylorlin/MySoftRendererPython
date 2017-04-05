#!/usr/bin/env python3

from enum import IntFlag
from graphics.base.Material import Material
from lib.math.Vector4 import Vector4


class PolyState(IntFlag):
    Null = 0
    Active = 1
    Clipped = 2
    BackFace = 4
    Lit = 8


class Poly(object):
    def __init__(self):
        self.state = PolyState.Active
        self.material = Material()
        self.vList = []
        self.tvList = []
        self.normal = Vector4()

    def AddVertex(self, v):
        self.vList.append(v)
        self.tvList.append(v)