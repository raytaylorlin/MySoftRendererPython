#!/usr/bin/env python3

from enum import IntFlag
import copy
from lib.math.Vector4 import Vector4


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
        self.worldPos = Vector4()
        self.vListLocal = []
        self.vListTrans = []
        self.polyList = []

        # 平均半径和最大半径
        self.averageRadius = 0
        self.maxRadius = 0

    def IsEnabled(self):
        return self.state & GameObjectState.Active and \
               self.state & GameObjectState.Visible and \
               not self.state & GameObjectState.Culled

    def AddVertex(self, v):
        self.vListLocal.append(v)
        self.vListTrans.append(copy.deepcopy(v))

    def AddPoly(self, p):
        self.polyList.append(p)

    def Scale(self, s):
        """仅缩放局部坐标，最好在加载完物体之后调用"""
        for v in self.vListLocal:
            v.pos.x *= s
            v.pos.y *= s
            v.pos.z *= s

    def SetWorldPosition(self, worldPos):
        """设置世界坐标"""
        assert isinstance(worldPos, Vector4)
        self.worldPos = worldPos
        self.TransformModelToWorld()

    def CalculateRadius(self):
        """计算平均半径和最大半径"""
        sumDistance = 0
        maxDistance = 0
        for v in self.vListLocal:
            d = v.pos.sqrMagnitude()
            sumDistance += d
            if d > maxDistance:
                maxDistance = d
        self.averageRadius = sumDistance / len(self.vListLocal)
        self.maxRadius = maxDistance

    def TransformModelToWorld(self):
        """模型坐标变换到世界坐标"""
        for i in range(len(self.vListLocal)):
            self.vListTrans[i].pos = self.vListLocal[i].pos + self.worldPos
