#!/usr/bin/env python3

from enum import IntFlag
import copy

from lib.math.Matrix4x4 import Matrix4x4
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

    def SetTransform(self, scale=1, eulerRotation=(0, 0, 0), worldPos=Vector4()):
        """设置基本变换"""

        # 先缩放，再旋转，后平移
        self.Scale(scale)
        self.SetEulerRotation(eulerRotation[0], eulerRotation[1], eulerRotation[2])
        self.SetWorldPosition(worldPos)

    def Scale(self, scale, transformLocal=False):
        """仅缩放局部坐标，最好在加载完物体之后调用"""
        vList = self.vListLocal if transformLocal else self.vListTrans
        for v in vList:
            v.pos.x *= scale
            v.pos.y *= scale
            v.pos.z *= scale

    def SetWorldPosition(self, worldPos, transformLocal=False):
        """设置世界坐标"""
        assert isinstance(worldPos, Vector4)
        self.worldPos = worldPos
        self.TransformModelToWorld(transformLocal)

    def SetEulerRotation(self, x=0, y=0, z=0, transformLocal=False):
        """设置旋转（使用欧拉角）"""
        rotationMatrix = Matrix4x4.GetRotateMatrix(x, y, z)
        self.TransformByMatrix(rotationMatrix)

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

    def TransformModelToWorld(self, transformLocal=False):
        """模型坐标变换到世界坐标"""
        vSourceList = self.vListLocal if transformLocal else self.vListTrans
        for i in range(len(vSourceList)):
            self.vListTrans[i].pos = self.worldPos + vSourceList[i].pos

    def TransformByMatrix(self, matrix, transformLocal=False):
        """使用一个矩阵来变换坐标"""
        assert isinstance(matrix, Matrix4x4)

        vSourceList = self.vListLocal if transformLocal else self.vListTrans
        for i in range(len(vSourceList)):
            self.vListTrans[i].pos = matrix * vSourceList[i].pos
