#!/usr/bin/env python3

import utils.log as log
import math
import copy
import collections
from enum import IntFlag, Enum

from lib.math3d import *
from graphics.base import *
from graphics.render import RenderBuffer
from graphics.lighting import *
from utils.mixins import BitMixin


class ECameraType(Enum):
    Euler = 0
    UVN = 1


class Camera(object):
    def __init__(self, pos=None, direction=None, cameraType=ECameraType.Euler,
                 lookAt=Vector4(), nearClipZ=0.3, farClipZ=1000,
                 fieldOfView=90, viewportWidth=RenderBuffer.DefaultWidth, viewportHeight=RenderBuffer.DefaultHeight):
        self.pos = pos or Vector4()
        self.direction = direction or Vector4()
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
        self.vertexToPolyDict = collections.defaultdict(list)
        self.textureVertexList = []
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
        vCopy.SetNormal(v.normal)
        self.vListTrans.append(vCopy)

    def AddPoly(self, p):
        self.polyList.append(p)

    def SetTransform(self, scale=1, eulerRotation=(0, 0, 0), worldPos=Vector4()):
        """设置基本变换"""
        self.SetScale(scale)
        self.SetEulerRotation(eulerRotation[0], eulerRotation[1], eulerRotation[2])
        self.SetWorldPosition(worldPos)
        self.CalculateRadius()

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


# endregion


# region 渲染列表
class ESortPolyMethod(Enum):
    Null = 0
    AverageZ = 1
    NearZ = 2
    FarZ = 3


class RenderList(object):
    def __init__(self, rasterizer, camera, sortPolyMethod=ESortPolyMethod.AverageZ):
        self.rasterizer = rasterizer
        self.camera = camera
        self.sortPolyMethod = sortPolyMethod
        self.polyList = []

    def AddObject(self, obj, useObjectMaterial=False):
        if not obj.IsEnabled():
            return

        # 剔除物体检测
        if self.camera.CullObject(obj):
            return

        obj.TransformModelToWorld()

        for poly in obj.polyList:
            if not poly.IsEnabled():
                continue

            # useObjectMaterial决定了使用物体的材质还是多边形的材质
            newPoly = Poly(obj.material if useObjectMaterial else poly.material)
            index = 0
            for i in poly.vIndexList:
                newPoly.AddVertex(i, obj.vListTrans[i], poly.tvList[index].textureCoord)
                index += 1
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

    def Sort(self):
        """简单的Z排序（画家算法），注意当多边形很长或互相贯通的时候，这种算法并不准确"""
        if self.sortPolyMethod == ESortPolyMethod.AverageZ:
            self.polyList.sort(key=lambda p: (p.tvList[0].pos.z + p.tvList[1].pos.z + p.tvList[2].pos.z) / 3, reverse=True)
        elif self.sortPolyMethod == ESortPolyMethod.NearZ:
            self.polyList.sort(key=lambda p: min(p.tvList[0].pos.z, p.tvList[1].pos.z, p.tvList[2].pos.z), reverse=True)
        elif self.sortPolyMethod == ESortPolyMethod.FarZ:
            self.polyList.sort(key=lambda p: max(p.tvList[0].pos.z, p.tvList[1].pos.z, p.tvList[2].pos.z), reverse=True)

    def RenderWire(self):
        """渲染线框"""
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            v0 = poly.tvList[0]
            v1 = poly.tvList[1]
            v2 = poly.tvList[2]
            self.rasterizer.DrawLine(Point(v0.pos.x, v0.pos.y), Point(v1.pos.x, v1.pos.y), poly.material.color)
            self.rasterizer.DrawLine(Point(v1.pos.x, v1.pos.y), Point(v2.pos.x, v2.pos.y), poly.material.color)
            self.rasterizer.DrawLine(Point(v2.pos.x, v2.pos.y), Point(v0.pos.x, v0.pos.y), poly.material.color)

    def CalculateLighting(self, lightList):
        """计算光照"""
        for poly in self.polyList:
            if (not poly.IsEnabled()) or (not poly.material.CanBeShaded()):
                continue

            log.logger.debug('Poly material: {}'.format(poly.material.mode))
            # 固定着色
            if poly.material.mode == EMaterialShadeMode.Constant:
                for v in poly.tvList:
                    v.color = poly.material.color
            # 恒定着色
            elif poly.material.mode == EMaterialShadeMode.Flat:
                resultColor = Color()
                for light in lightList:
                    light.Calculate(resultColor, poly)
                for v in poly.tvList:
                    v.color = resultColor
            # Gouraud着色（分别对每个顶点计算并着色）
            elif poly.material.mode == EMaterialShadeMode.Gouraud:
                resultColor = [Color(), Color(), Color()]
                for light in lightList:
                    light.Calculate(resultColor, poly)
                for i in range(3):
                    poly.tvList[i].color = resultColor[i]

    def ClipPoly(self, camera):
        """裁剪多边形"""
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            tanHalfFOV = math.tan(math.radians(camera.fieldOfView / 2))
            # 根据左右裁剪面进行剔除（不需裁剪）
            for v in poly.tvList:
                zTest = v.pos.z * tanHalfFOV
                if v.pos.x > zTest:
                    v.clipCode = EVertexClipCode.LargerThanXMax
                elif v.pos.x < -zTest:
                    v.clipCode = EVertexClipCode.LessThanXMin
                else:
                    v.clipCode = EVertexClipCode.BetweenXMinAndXMax
            if all(v.clipCode == EVertexClipCode.LargerThanXMax for v in poly.tvList) or \
                    all(v.clipCode == EVertexClipCode.LessThanXMin for v in poly.tvList):
                poly.SetBit(EPolyState.Clipped)
                continue

            # 根据上下裁剪面进行剔除（不需裁剪）
            for v in poly.tvList:
                zTest = v.pos.z * tanHalfFOV
                if v.pos.y > zTest:
                    v.clipCode = EVertexClipCode.LargerThanYMax
                elif v.pos.y < -zTest:
                    v.clipCode = EVertexClipCode.LessThanYMin
                else:
                    v.clipCode = EVertexClipCode.BetweenYMinAndYMax
            if all(v.clipCode == EVertexClipCode.LargerThanYMax for v in poly.tvList) or \
                    all(v.clipCode == EVertexClipCode.LessThanYMin for v in poly.tvList):
                poly.SetBit(EPolyState.Clipped)
                continue

            # 根据远裁剪面进行剔除（不需裁剪）
            numVertexInField = 0
            for v in poly.tvList:
                if v.pos.z > camera.farClipZ:
                    v.clipCode = EVertexClipCode.LargerThanZMax
                elif v.pos.z < camera.nearClipZ:
                    v.clipCode = EVertexClipCode.LessThanZMin
                else:
                    v.clipCode = EVertexClipCode.BetweenZMinAndZMax
                    numVertexInField += 1
            if all(v.clipCode == EVertexClipCode.LargerThanZMax for v in poly.tvList) or \
                    all(v.clipCode == EVertexClipCode.LessThanZMin for v in poly.tvList):
                poly.SetBit(EPolyState.Clipped)
                continue

            # 根据近裁剪面进行裁剪
            # 注意：裁剪多边形发生在顶点着色之前，所以不需要对颜色值进行裁剪
            if any(v.clipCode == EVertexClipCode.LessThanZMin for v in poly.tvList):
                # 简单情形：1个顶点在视锥体内，2个顶点在近剪裁面外
                if numVertexInField == 1:
                    # 第1步：找出视锥体内外的顶点
                    vIn, vOut = None, []
                    for v in poly.tvList:
                        if v.clipCode == EVertexClipCode.BetweenZMinAndZMax:
                            vIn = v
                        else:
                            vOut.append(v)

                    # 求解两个外部顶点应该裁剪到的目标点
                    for v in vOut:
                        line = v.pos - vIn.pos
                        t1Solution = (camera.nearClipZ - vIn.pos.z) / line.z
                        x1Solution = vIn.pos.x + line.x * t1Solution
                        y1Solution = vIn.pos.y + line.y * t1Solution
                        # 将解得的值覆盖原来的顶点
                        v.pos.x = x1Solution
                        v.pos.y = y1Solution
                        v.pos.z = camera.nearClipZ
                        # 裁剪纹理
                        if poly.material.texture:
                            uSolution = vIn.textureCoord.x + (v.textureCoord.x - vIn.textureCoord.x) * t1Solution
                            vSolution = vIn.textureCoord.y + (v.textureCoord.y - vIn.textureCoord.y) * t1Solution
                            v.textureCoord.x = uSolution
                            v.textureCoord.y = vSolution
                # 复杂情形：2个顶点在视锥体内，裁剪后是一个四边形，需要再分割出一个三角形
                elif numVertexInField == 2:
                    vIn, vOut = [], None
                    for v in poly.tvList:
                        if v.clipCode == EVertexClipCode.BetweenZMinAndZMax:
                            vIn.append(v)
                        else:
                            vOut = v

                    line1 = vIn[0].pos - vOut.pos
                    t1Solution = (camera.nearClipZ - vOut.pos.z) / line1.z
                    x1Solution = vOut.pos.x + line1.x * t1Solution
                    y1Solution = vOut.pos.y + line1.y * t1Solution

                    line2 = vIn[1].pos - vOut.pos
                    t2Solution = (camera.nearClipZ - vOut.pos.z) / line2.z
                    x2Solution = vOut.pos.x + line2.x * t2Solution
                    y2Solution = vOut.pos.y + line2.y * t2Solution

                    # 裁剪纹理
                    if poly.material.texture:
                        u1Solution = vIn[0].textureCoord.x + (vIn[0].textureCoord.x - vOut.textureCoord.x) * t1Solution
                        v1Solution = vIn[0].textureCoord.y + (vIn[0].textureCoord.y - vOut.textureCoord.y) * t1Solution
                        u2Solution = vIn[1].textureCoord.x + (vIn[1].textureCoord.x - vOut.textureCoord.x) * t2Solution
                        v2Solution = vIn[1].textureCoord.y + (vIn[1].textureCoord.y - vOut.textureCoord.y) * t2Solution

                    # 将解得的值覆盖原来的外部的顶点
                    vOut.pos.x = x1Solution
                    vOut.pos.y = y1Solution
                    vOut.pos.z = camera.nearClipZ
                    if poly.material.texture:
                        vOut.textureCoord.x = u1Solution
                        vOut.textureCoord.y = v1Solution

                    # 创建新的三角形
                    newV1 = copy.deepcopy(vIn[1])
                    newV2 = copy.deepcopy(vOut)
                    # WARNING: 这里顶点的法线直接用的多边形法线，但应该是不准确的
                    polyNormal = poly.GetNormal()
                    newV3 = Vertex(pos=Vector4(x2Solution, y2Solution, camera.nearClipZ),
                                   normal=Vector4(polyNormal.x, polyNormal.y, polyNormal.z),
                                   color=Color(vOut.color.r, vOut.color.g, vOut.color.b, vOut.color.a))
                    if poly.material.texture:
                        newV3.SetTextureCorrd(Point(u2Solution, v2Solution))
                    # newPoly = copy.deepcopy(poly)
                    newPoly = Poly()
                    newPoly.AddVertexWithoutIndex(newV1, newV1.textureCoord)
                    newPoly.AddVertexWithoutIndex(newV3, newV3.textureCoord)
                    newPoly.AddVertexWithoutIndex(newV2, newV2.textureCoord)
                    self.polyList.append(newPoly)

    def RenderSolid(self):
        for poly in self.polyList:
            if not poly.IsEnabled():
                continue

            v0 = poly.tvList[0]
            v1 = poly.tvList[1]
            v2 = poly.tvList[2]
            if not poly.material.texture:
                self.rasterizer.DrawTriangle(Point(v0.pos.x, v0.pos.y, v0.color),
                                             Point(v1.pos.x, v1.pos.y, v1.color),
                                             Point(v2.pos.x, v2.pos.y, v2.color))
            else:
                self.rasterizer.DrawTriangle(UVPoint(v0.pos.x, v0.pos.y, v0.color, v0.textureCoord.x, v0.textureCoord.y, poly.material),
                                             UVPoint(v1.pos.x, v1.pos.y, v1.color, v1.textureCoord.x, v1.textureCoord.y, poly.material),
                                             UVPoint(v2.pos.x, v2.pos.y, v2.color, v2.textureCoord.x, v2.textureCoord.y, poly.material))

    def PreRender(self, camera, lightList):
        self.CheckBackFace(camera)
        self.TransformWorldToCamera(camera)
        self.ClipPoly(camera)
        self.CalculateLighting(lightList)
        self.Sort()
        self.TransformCameraToPerspective(camera)
        self.TransformPerspectiveToScreen(camera)


# endregion
