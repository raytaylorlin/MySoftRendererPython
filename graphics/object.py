#!/usr/bin/env python3

import copy
import math
from enum import IntFlag, Enum
from lib.math3d import *
from graphics.base import Poly, EPolyState
from graphics.render import RenderBuffer


class Camera(object):
    def __init__(self, pos=Vector4(), direction=Vector4(), nearClipZ=0.3, farClipZ=1000,
                 fieldOfView=90, viewportWidth=RenderBuffer.DefaultWidth, viewportHeight=RenderBuffer.DefaultHeight):
        self.pos = pos
        self.direction = direction
        self.u = self.v = self.n = Vector4()

        self.aspectRatio = float(viewportWidth) / viewportHeight
        self.viewPlaneWidth = 2.0
        self.viewPlaneHeight = 2.0 / self.aspectRatio

        self.viewDist = 0.5 * self.viewPlaneWidth * math.tan(math.radians(fieldOfView / 2))
        self.fieldOfView = fieldOfView
        self.nearClipZ = nearClipZ
        self.farClipZ = farClipZ
        self.viewportWidth = viewportWidth
        self.viewportHeight = viewportHeight

    def GetEulerMatrix(self):
        rotate = Matrix4x4.GetRotateMatrix(-self.direction.x, -self.direction.y, -self.direction.z)
        translate = Matrix4x4([[1, 0, 0, 0],
                               [0, 1, 0, 0],
                               [0, 0, 1, 0],
                               [-self.pos.x, -self.pos.y, -self.pos.z, 1]])
        result = translate * rotate
        return result


# region 游戏物体
class EGameObjectState(IntFlag):
    """物体状态枚举"""
    Null = 0
    Active = 1
    Visible = 2
    Culled = 4


class EGameObjectAttribute(IntFlag):
    """物体属性枚举"""
    Null = 0
    SingleFrame = 1
    MultiFrame = 2
    Textures = 4


class GameObject(object):
    def __init__(self):
        self.state = EGameObjectState.Active | EGameObjectState.Visible
        self.attr = EGameObjectAttribute.Null
        self.name = ''
        self.worldPos = Vector4()
        self.vListLocal = []
        self.vListTrans = []
        self.polyList = []

        # 平均半径和最大半径
        self.averageRadius = 0
        self.maxRadius = 0

    def IsEnabled(self):
        return self.state & EGameObjectState.Active and \
               self.state & EGameObjectState.Visible and \
               not self.state & EGameObjectState.Culled

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


# endregion


# region 渲染列表
class ESortPolyMethod(Enum):
    AverageZ = 0
    NearZ = 1
    FarZ = 2


class RenderList(object):
    def __init__(self, rasterizer):
        self.rasterizer = rasterizer
        self.polyList = []

    def AddObject(self, obj, insertLocal=True):
        if not obj.IsEnabled():
            return
        for poly in obj.polyList:
            if not poly.IsEnabled():
                continue

            newPoly = Poly()
            for i in poly.vIndexList:
                newPoly.AddVertex(i, obj.vListLocal[i] if insertLocal else obj.vListTrans[i])
            self.polyList.append(newPoly)

    def TransformWorldToCamera(self, camera):
        """世界坐标变换到相机坐标"""
        matrix = camera.GetEulerMatrix()
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue
            for vertex in poly.tvList:
                vertex.pos = vertex.pos * matrix

    def TransformCameraToPerspective(self, camera):
        """相机坐标变换到透视坐标"""
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            for vertex in poly.tvList:
                z = vertex.pos.z
                vertex.pos.x = camera.viewDist * vertex.pos.x / z
                vertex.pos.y = camera.viewDist * vertex.pos.y * camera.aspectRatio / z

    def TransformPerspectiveToScreen(self, camera):
        """透视坐标变换到屏幕坐标"""
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            alpha = 0.5 * camera.viewportWidth - 0.5
            beta = 0.5 * camera.viewportHeight - 0.5

            for vertex in poly.tvList:
                z = vertex.pos.z
                vertex.pos.x = alpha + alpha * vertex.pos.x
                vertex.pos.y = beta - beta * vertex.pos.y

    def CheckBackFace(self, camera):
        """检测所有多边形的背面，以进行背面消除"""
        for poly in self.polyList:
            poly.Clear(EPolyState.Active)

            normal = poly.GetNormal()
            v = camera.pos - poly.tvList[0].pos
            if Vector4.Dot(v, normal) <= 0:
                poly.SetBit(EPolyState.BackFace)

    def RenderWire(self):
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            v0 = poly.tvList[0].pos
            v1 = poly.tvList[1].pos
            v2 = poly.tvList[2].pos
            self.rasterizer.DrawLine(Point(round(v0.x), round(v0.y)),
                                     Point(round(v1.x), round(v1.y)),
                                     poly.material.color)
            self.rasterizer.DrawLine(Point(round(v1.x), round(v1.y)),
                                     Point(round(v2.x), round(v2.y)),
                                     poly.material.color)
            self.rasterizer.DrawLine(Point(round(v2.x), round(v2.y)),
                                     Point(round(v0.x), round(v0.y)),
                                     poly.material.color)

# endregion
