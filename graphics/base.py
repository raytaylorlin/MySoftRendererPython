#!/usr/bin/env python3

from enum import IntFlag
from lib.math3d import *
from utils.mixins import BitMixin


class EMaterialShadeMode(IntFlag):
    """材质着色模式"""

    Null = 0
    Constant = 1
    Flat = 2
    Phong = 4
    Gouraud = 8
    Texture = 16


class ETextureFilterMode(IntFlag):
    """纹理滤波模式"""
    Point = 0
    Bilinear = 1


class Material(object):
    """材质"""

    def __init__(self):
        self.mode = EMaterialShadeMode.Flat
        self.textureFilterMode = ETextureFilterMode.Point
        self.color = ColorDefine.White
        self.ka = self.kd = self.ks = 0.0
        self.texture = None
        self.textureSize = (0, 0)

    def CanBeShaded(self):
        return self.mode != EMaterialShadeMode.Null


class EPolyState(IntFlag):
    """多边形状态"""
    Null = 0
    Active = 1
    Clipped = 2
    BackFace = 4
    Lit = 8


class Poly(BitMixin):
    """多边形"""

    def __init__(self, material=None):
        super(Poly, self).__init__()
        self.state = EPolyState.Active
        self.material = material or Material()
        self.vList = []
        self.tvList = []
        self.vIndexList = []
        self.normal = Vector4()

    def IsEnabled(self):
        return self.state & EPolyState.Active and \
               not self.state & EPolyState.Clipped and \
               not self.state & EPolyState.BackFace

    def AddVertex(self, i, v, tc=None):
        self.vList.append(v)
        # 复制顶点的数据
        vCopy = Vertex()
        vCopy.SetPosition(v.pos)
        vCopy.SetNormal(v.normal)
        if tc:
            vCopy.SetTextureCorrd(tc)
        self.tvList.append(vCopy)
        self.vIndexList.append(i)

    def AddVertexWithoutIndex(self, v, tc=None):
        self.vList.append(v)
        # 复制顶点的数据
        vCopy = Vertex()
        vCopy.SetPosition(v.pos)
        vCopy.SetNormal(v.normal)
        if tc:
            vCopy.SetTextureCorrd(tc)
        self.tvList.append(vCopy)

    # def Clone(self, objTransList):
    #     newPoly = Poly()
    #     for i in self.vIndexList:
    #         newPoly.AddVertex(i, objTransList[i])
    #         newPoly.material = self.material
    #         newPoly.normal = self.normal
    #     return newPoly

    def GetNormal(self):
        if self.normal.IsZero():
            v01 = self.tvList[1].pos - self.tvList[0].pos
            v02 = self.tvList[2].pos - self.tvList[0].pos
            self.normal = Vector4.Cross(v01, v02)
            self.normal.Normalize()
        return self.normal


class EVertexAdjustFlag(IntFlag):
    """顶点变换状态"""
    Null = 0
    InvertX = 1
    InvertY = 2
    InvertZ = 4
    SwapYZ = 8
    SwapXZ = 16
    SwapXY = 32


class EVertexClipCode(IntFlag):
    """顶点裁剪状态"""
    Null = 0x0000
    LargerThanXMax = 0x0001
    LessThanXMin = 0x0002
    BetweenXMinAndXMax = 0x0004

    LargerThanYMax = 0x0010
    LessThanYMin = 0x0020
    BetweenYMinAndYMax = 0x0040

    LargerThanZMax = 0x0100
    LessThanZMin = 0x0200
    BetweenZMinAndZMax = 0x0400


class Vertex(object):
    """顶点"""

    def __init__(self, pos=None, normal=None, textureCoord=None, color=None):
        self.pos = pos or Vector4()
        self.normal = normal or Vector4()
        self.textureCoord = textureCoord or Point(0, 0)
        self.color = color or Color()
        self.clipCode = EVertexClipCode.Null

    def SetPosition(self, pos):
        if isinstance(pos, Vector4):
            self.pos.x = pos.x
            self.pos.y = pos.y
            self.pos.z = pos.z
            self.pos.w = pos.w
        elif isinstance(pos, tuple) or isinstance(pos, list):
            self.pos.x = pos[0]
            self.pos.y = pos[1]
            self.pos.z = pos[2]

    def SetNormal(self, normal):
        self.normal.x = normal.x
        self.normal.y = normal.y
        self.normal.z = normal.z
        self.normal.w = normal.w

    def SetTextureCorrd(self, tc):
        self.textureCoord.x = tc.x
        self.textureCoord.y = tc.y
        self.textureCoord.color = tc.color

    def Adjust(self, flag):
        if flag & EVertexAdjustFlag.InvertX:
            self.pos.x = -self.pos.x
        elif flag & EVertexAdjustFlag.InvertY:
            self.pos.y = -self.pos.y
        elif flag & EVertexAdjustFlag.InvertZ:
            self.pos.z = -self.pos.z
        elif flag & EVertexAdjustFlag.SwapYZ:
            self.pos.y, self.pos.z = self.pos.z, self.pos.y
        elif flag & EVertexAdjustFlag.SwapXZ:
            self.pos.x, self.pos.z = self.pos.z, self.pos.x
        elif flag & EVertexAdjustFlag.SwapXY:
            self.pos.x, self.pos.y = self.pos.y, self.pos.x

    def __str__(self):
        return 'Pos: {}, Normal: {}, Texture: {}'.format(self.pos, self.normal, self.textureCoord)
