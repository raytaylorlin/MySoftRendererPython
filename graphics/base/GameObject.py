#!/usr/bin/env python3

from enum import IntFlag


class GameObjectState(IntFlag):
    Null = 0
    Active = 1
    Visible = 2
    Culled = 4


class GameObjectAttribute(IntFlag):
    Null = 0
    SingleFrame = 1
    MultiFrame = 2
    Textures = 4


class GameObject(object):
    def __init__(self):
        self.state = GameObjectState.Active | GameObjectState.Visible
        self.attr = GameObjectAttribute.Null
        self.name = ''
        self.vListLocal = []
        self.vListTrans = []
        self.polyList = []

        # 平均半径和最大半径
        self.averageRadius = 0
        self.maxRadius = 0

    def AddVertex(self, v):
        self.vListLocal.append(v)
        self.vListTrans.append(v)

    def AddPoly(self, p):
        self.polyList.append(p)

    def Scale(self, s):
        """仅缩放局部坐标，最好在加载完物体之后调用"""
        for v in self.vListLocal:
            v.pos.x *= s
            v.pos.y *= s
            v.pos.z *= s

    def CalculateRadius(self):
        sumDistance = 0
        maxDistance = 0
        for v in self.vListLocal:
            d = v.pos.sqrMagnitude()
            sumDistance += d
            if d > maxDistance:
                maxDistance = d
        self.averageRadius = sumDistance / len(self.vListLocal)
        self.maxRadius = maxDistance
