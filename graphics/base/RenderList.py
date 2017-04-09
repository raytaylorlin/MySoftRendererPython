#!/usr/bin/env python3

from enum import Enum
import copy

from graphics.base.Poly import Poly, PolyState
from lib.math.Point import Point
from lib.math.Vector4 import Vector4


class SortPolyMethod(Enum):
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
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            matrix = camera.GetEulerMatrix()
            for vertex in poly.tvList:
                vertex.pos = matrix * vertex.pos

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
            poly.Clear(PolyState.Active)

            normal = poly.GetNormal()
            v = camera.pos - poly.tvList[0].pos
            if Vector4.Dot(v, normal) <= 0:
                poly.SetBit(PolyState.BackFace)

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
