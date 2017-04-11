#!/usr/bin/env python3

from PIL import Image
import utils.log as log
from graphics.base import *
from lib.math3d import *


class Rasterizer(object):
    def __init__(self, buffer):
        self.buffer = buffer
        self.clipRegion = [(0, 0), (0, 0)]

    def DrawLine(self, p1, p2, color):
        """
        使用Bresenahams算法画线
        参考：http://blog.csdn.net/ming1006/article/details/8006769
        """

        assert isinstance(p1, Point)
        assert isinstance(p2, Point)
        assert isinstance(color, Color)

        log.logger.info('DrawLine: p1 = {0}, p2 = {1}, color = {2}'.format(p1, p2, color))
        currX, currY = p1.x, p1.y
        # 计算步长方向及dx和dy绝对值
        dx, dy = p2.x - p1.x, p2.y - p1.y
        xInc = 1 if dx >= 0 else -1
        yInc = 1 if dy >= 0 else -1
        dx, dy = abs(dx), abs(dy)
        # 两倍dx和dy
        dx2, dy2 = dx * 2, dy * 2

        # 斜率为0-1的情况
        if dx > dy:
            # 计算整数误差项（通过error = (dy / dx - 0.5) * dx2 = dy2 - dx所得，即把误差项扩大2倍dx）
            error = dy2 - dx
            for i in range(dx):
                self.buffer.Set((currX, currY), color)
                # 检查误差是否超出范围
                if error >= 0:
                    error -= dx2  # error = error - 1
                    currY += yInc

                error += dy2  # error = error + dy / dx
                currX += xInc
        else:
            error = dx2 - dy
            for i in range(dy):
                self.buffer.Set((currX, currY), color)
                if error >= 0:
                    error -= dy2
                    currX += xInc
                error += dx2
                currY += yInc

    def DrawTopFlatTriangle(self, p1, p2, p3, color):
        pass

    def DrawBottomFlatTriangle(self, p1, p2, p3, color):
        pass

    def DrawTriangle(self, p1, p2, p3, color):
        pass

    def SetClipRegion(self, p1, p2):
        self.clipRegion[0] = p1
        self.clipRegion[1] = p2


class RenderBuffer(object):
    DefaultWidth = 800
    DefaultHeight = 800

    def __init__(self, width=DefaultWidth, height=DefaultHeight, color=Color()):
        self.width = width
        self.height = height
        self.data = [[color for i in range(self.width)] for j in range(self.height)]

    def Get(self, pos):
        return self.data[pos[0]][pos[1]]

    def Set(self, pos, color):
        assert isinstance(color, Color), 'The param color is not a instance of Color'
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.width or pos[1] >= self.height:
            return
        self.data[pos[0]][pos[1]] = color

    def __str__(self):
        result = []
        for line in self.data:
            for item in line:
                result.append(str(item))
                result.append(' ')
            result.append('\n')
        return ''.join(result)


class RenderInterface(object):
    def Render(self, buffer):
        pass


class ImageRenderer(RenderInterface):
    def __init__(self, filename):
        self.filename = filename

    def Render(self, buffer):
        image = Image.new('RGBA', (buffer.width, buffer.height))
        pixels = image.load()
        for i in range(image.size[0]):
            for j in range(image.size[1]):
                pixels[i, j] = buffer.data[i][j].tuple

        image.save(self.filename)


class OpenGLRenderer(RenderInterface):
    pass
