#!/usr/bin/env python3

import math
from graphics.core.RenderBuffer import RenderBuffer
from lib.math.Matrix4x4 import Matrix4x4
from lib.math.Vector4 import Vector4


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
        result = Matrix4x4([[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 0],
                            [-self.pos.x, -self.pos.y, -self.pos.z, 1]])

        return result
