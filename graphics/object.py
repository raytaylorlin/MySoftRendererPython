#!/usr/bin/env python3

import utils.log as log
import math
from enum import IntFlag, Enum

from lib.math3d import *
from graphics.base import Poly, EPolyState, Vertex, Color, Material
from graphics.render import RenderBuffer
from graphics.lighting import *
from utils.mixins import BitMixin


class ECameraType(Enum):
    Euler = 0
    UVN = 1


class Camera(object):
    def __init__(self, pos=Vector4(), direction=Vector4(), cameraType=ECameraType.Euler,
                 lookAt=Vector4(), nearClipZ=0.3, farClipZ=1000,
                 fieldOfView=90, viewportWidth=RenderBuffer.DefaultWidth, viewportHeight=RenderBuffer.DefaultHeight):
        self.pos = pos
        self.direction = direction
        self.u = self.v = self.n = Vector4()
        self.cameraType = cameraType
        self.lookAt = lookAt

        self.aspectRatio = float(viewportWidth) / viewportHeight
        self.viewPlaneWidth = 2.0
        self.viewPlaneHeight = 2.0 / self.aspectRatio

        self.viewDist = 0.5 * self.viewPlaneWidth * math.tan(math.radians(fieldOfView / 2))
        self.fieldOfView = fieldOfView
        self.nearClipZ = nearClipZ
        self.farClipZ = farClipZ
        self.viewportWidth = viewportWidth
        self.viewportHeight = viewportHeight

    def GetViewMatrix(self):
        result = None
        if self.cameraType == ECameraType.Euler:
            rotate = Matrix4x4.GetRotateMatrix(-self.direction.x, -self.direction.y, -self.direction.z)
            translate = Matrix4x4([[1, 0, 0, 0],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, 0],
                                   [-self.pos.x, -self.pos.y, -self.pos.z, 1]])
            result = translate * rotate
        elif self.cameraType == ECameraType.UVN:
            n = self.lookAt - self.pos
            v = Vector4(0, 1, 0)
            u = Vector4.Cross(v, n)
            v = Vector4.Cross(n, u)
            u.Normalize()
            v.Normalize()
            n.Normalize()

            translate = Matrix4x4([[1, 0, 0, 0],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, 0],
                                   [-self.pos.x, -self.pos.y, -self.pos.z, 1]])
            rotate = Matrix4x4([[u.x, v.x, n.x, 0],
                                [u.y, v.y, n.y, 0],
                                [u.z, v.z, n.z, 0],
                                [0, 0, 0, 1]])
            result = translate * rotate
        else:
            raise Exception('Unknown camera type {}'.format(self.cameraType))

        return result

    def CullObject(self, obj):
        """根据相机的变换，剔除掉物体"""

        # 首先将物体的世界坐标变换到相机坐标，再用相机坐标和剪裁面比较

        matrix = self.GetViewMatrix()
        spherePos = obj.worldPos * matrix
        culled = False
        cullPlane = ''

        # 检测远近剪裁面
        if spherePos.z - obj.maxRadius > self.farClipZ or spherePos.z + obj.maxRadius < self.nearClipZ:
            culled = True
            cullPlane = 'Z'
        # 用右剪裁面和左剪裁面检测包围球上最左边和最右边的点
        zTest = 0.5 * self.viewPlaneWidth * spherePos.z / self.viewDist
        if spherePos.x - obj.maxRadius > zTest or spherePos.x + obj.maxRadius < -zTest:
            culled = True
            cullPlane = 'X'
        # 用上剪裁面和下剪裁面检测包围球上最下边和最上边的点
        zTest = 0.5 * self.viewPlaneHeight * spherePos.z / self.viewDist
        if spherePos.y - obj.maxRadius > zTest or spherePos.y + obj.maxRadius < -zTest:
            culled = True
            cullPlane = 'Y'

        if culled:
            obj.SetBit(EGameObjectState.Culled)
            log.logger.debug('Cull object at pos %s, cull plane = %s', obj.worldPos, cullPlane)
        return culled


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


class GameObject(BitMixin):
    def __init__(self):
        super(GameObject, self).__init__()
        self.state = EGameObjectState.Active | EGameObjectState.Visible
        self.attr = EGameObjectAttribute.Null
        self.name = ''
        self.worldPos = Vector4()
        self.rotation = Vector4()
        self.scale = 1

        self.vListLocal = []
        self.vListTrans = []
        self.polyList = []
        self.material = Material()

        # 平均半径和最大半径
        self.averageRadius = 0
        self.maxRadius = 0

    def IsEnabled(self):
        return self.state & EGameObjectState.Active and \
               self.state & EGameObjectState.Visible and \
               not self.state & EGameObjectState.Culled

    def Reset(self):
        self.state = EGameObjectState.Active | EGameObjectState.Visible
        self.attr = EGameObjectAttribute.Null

    def AddVertex(self, v):
        self.vListLocal.append(v)
        vCopy = Vertex()
        vCopy.SetPosition(v.pos)
        self.vListTrans.append(vCopy)

    def AddPoly(self, p):
        self.polyList.append(p)

    def SetTransform(self, scale=1, eulerRotation=(0, 0, 0), worldPos=Vector4()):
        """设置基本变换"""
        self.SetScale(scale)
        self.SetEulerRotation(eulerRotation[0], eulerRotation[1], eulerRotation[2])
        self.SetWorldPosition(worldPos)

    def SetScale(self, scale):
        """仅缩放局部坐标，最好在加载完物体之后调用"""
        self.scale = scale

    def SetWorldPosition(self, worldPos):
        """设置世界坐标"""
        self.worldPos = worldPos

    def SetEulerRotation(self, x=0, y=0, z=0):
        """设置旋转（使用欧拉角）"""
        self.rotation = Vector4(x, y, z)

    def CalculateRadius(self):
        """计算平均半径和最大半径"""
        sumDistance = 0
        maxDistance = 0
        for v in self.vListLocal:
            scaleVector = v.pos * self.scale
            d = scaleVector.sqrMagnitude
            sumDistance += d
            if d > maxDistance:
                maxDistance = d
        self.averageRadius = sumDistance / len(self.vListLocal)
        self.maxRadius = maxDistance
        log.logger.debug('Average radius = {}, max radius = {}'.format(self.averageRadius, self.maxRadius))

    def TransformModelToWorld(self):
        """模型坐标变换到世界坐标"""
        for i in range(len(self.vListLocal)):
            # 缩放
            vScale = self.vListLocal[i].pos * self.scale
            # 旋转
            rotationMatrix = Matrix4x4.GetRotateMatrix(self.rotation.x, self.rotation.y, self.rotation.z)
            vRotation = vScale * rotationMatrix
            # 平移
            vTranslate = self.worldPos + vRotation

            self.vListTrans[i].pos = vTranslate
            log.logger.debug('world pos = {}, vListTrans[i].pos = {}'.format(self.worldPos, self.vListTrans[i].pos))

    def TransformByMatrix(self, matrix, transformLocal=False):
        """使用一个矩阵来变换坐标"""
        assert isinstance(matrix, Matrix4x4)

        vSourceList = self.vListLocal if transformLocal else self.vListTrans
        for i in range(len(vSourceList)):
            self.vListTrans[i].pos = matrix * vSourceList[i].pos


# endregion


# region 渲染列表
class ESortPolyMethod(Enum):
    Null = 0
    AverageZ = 1
    NearZ = 2
    FarZ = 3


class RenderList(object):
    def __init__(self, rasterizer, sortPolyMethod=ESortPolyMethod.AverageZ):
        self.rasterizer = rasterizer
        self.polyList = []

    def AddObject(self, obj):
        if not obj.IsEnabled():
            return

        obj.TransformModelToWorld()

        for poly in obj.polyList:
            if not poly.IsEnabled():
                continue

            newPoly = Poly(obj.material)
            for i in poly.vIndexList:
                newPoly.AddVertex(i, obj.vListTrans[i])
            self.polyList.append(newPoly)

    def Reset(self):
        self.polyList.clear()

    def TransformWorldToCamera(self, camera):
        """世界坐标变换到相机坐标"""
        matrix = camera.GetViewMatrix()
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue
            for vertex in poly.tvList:
                vertex.pos = vertex.pos * matrix
                log.logger.debug('Vertex.pos = {}'.format(vertex.pos))

    def TransformCameraToPerspective(self, camera):
        """相机坐标变换到透视坐标"""
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            for vertex in poly.tvList:
                tempX = vertex.pos.x
                tempY = vertex.pos.y

                z = vertex.pos.z
                vertex.pos.x = camera.viewDist * vertex.pos.x / z
                vertex.pos.y = camera.viewDist * vertex.pos.y * camera.aspectRatio / z
                if vertex.pos.x < -1 or vertex.pos.x > 1 or vertex.pos.y < -1 or vertex.pos.y > 1:
                    log.logger.debug('Vertex pos {} out of uniform coord'.format(vertex))

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
        """渲染线框"""
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

    def CalculateLighting(self, lightList):
        """计算光照"""
        for poly in self.polyList:
            if (not poly.IsEnabled()) or (not poly.material.CanBeShaded()):
                continue

            resultColor = Color()
            for light in lightList:
                light.Calculate(resultColor, poly)
            poly.material.color = resultColor

    def RenderSolid(self):
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            v0 = poly.tvList[0].pos
            v1 = poly.tvList[1].pos
            v2 = poly.tvList[2].pos
            self.rasterizer.DrawTriangle(Point(v0.x, v0.y), Point(v1.x, v1.y), Point(v2.x, v2.y), poly.material.color)

# endregion
