#!/usr/bin/env python3

import copy
from enum import IntFlag
from graphics.base.Material import Material
from lib.math.Vector4 import Vector4
from utils.BitMixin import BitMixin


class PolyState(IntFlag):
    Null = 0
    Active = 1
    Clipped = 2
    BackFace = 4
    Lit = 8


class Poly(BitMixin):
    def __init__(self):
        self.state = PolyState.Active
        self.material = Material()
        self.vList = []
        self.tvList = []
        self.vIndexList = []
        self.normal = Vector4()

    def IsEnabled(self):
        return self.state & PolyState.Active and \
               not self.state & PolyState.Clipped and \
               not self.state & PolyState.BackFace

    def AddVertex(self, i, v):
        self.vList.append(v)
        self.tvList.append(copy.deepcopy(v))
        self.vIndexList.append(i)

    def GetNormal(self):
        if self.normal.IsZero():
            v01 = self.tvList[1].pos - self.tvList[0].pos
            v02 = self.tvList[2].pos - self.tvList[0].pos
            self.normal = Vector4.Cross(v01, v02)
        return self.normal
