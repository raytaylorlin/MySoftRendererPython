#!/usr/bin/env python3

import math
from PIL import Image
import utils.log as log
from lib.math3d import *


class Rasterizer(object):
    def __init__(self, buffer):
        self.buffer = buffer
        self.clipRegion = [Point(0, 0), Point(buffer.width, buffer.height)]

    def DrawLine(self, p1, p2, color):
        """
        使用Bresenahams算法画线
        参考：http://blog.csdn.net/ming1006/article/details/8006769
        """

        # assert isinstance(v1, Vertex)
        # assert isinstance(v2, Vertex)
        # assert isinstance(color, Color)

        # log.logger.debug('Draw line: ({}) ({}) {}'.format(p1, p2, color))

        currX, currY = round(p1.x), round(p1.y)
        # 计算步长方向及dx和dy绝对值
        dx, dy = round(p2.x - p1.x), round(p2.y - p1.y)
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

    def DrawRectangle(self, p1, p2, color):
        """画矩形线框"""
        bottomLeft = Point(p1.x, p2.y)
        topRight = Point(p2.x, p1.y)
        self.DrawLine(p1, topRight, color)
        self.DrawLine(p1, bottomLeft, color)
        self.DrawLine(p2, bottomLeft, color)
        self.DrawLine(p2, topRight, color)

    def DrawTriangle(self, p1, p2, p3):
        # 忽略三点共线的情况
        if math.isclose(p1.x, p2.x) and math.isclose(p2.x, p3.x) or \
                        math.isclose(p1.y, p2.y) and math.isclose(p2.y, p3.y):
            return

        # 将三个点按y1 y2 y3排序
        if p2.y < p1.y:
            p1, p2 = p2, p1
        if p3.y < p1.y:
            p1, p3 = p3, p1
        if p3.y < p2.y:
            p2, p3 = p3, p2

        # 测试裁剪
        minClipX = self.clipRegion[0].x
        minClipY = self.clipRegion[0].y
        maxClipX = self.clipRegion[1].x
        maxClipY = self.clipRegion[1].y
        if p3.y < minClipY or p1.y > maxClipY or \
                                        p1.x < minClipX and p2.x < minClipX and p3.x < minClipX or \
                                        p1.x > maxClipX and p2.x > maxClipX and p3.x > maxClipX:
            return

        if math.isclose(p1.y, p2.y):
            self.DrawTopFlatTriangle(p1, p2, p3)
        elif math.isclose(p2.y, p3.y):
            self.DrawBottomFlatTriangle(p1, p2, p3)
        else:
            # 由上面点的排序可知，p1-p3必为长边，在长边上找出分割点的X坐标
            splitX = p1.x + (p2.y - p1.y) * (p3.x - p1.x) / (p3.y - p1.y)
            splitColor = Color.Lerp(p1.color, p3.color, (p2.y - p1.y) / (p3.y - p1.y))
            splitPoint = Point(splitX, p2.y, splitColor)
            # 画被分割的上平底和下平顶三角形
            self.DrawBottomFlatTriangle(p1, splitPoint, p2)
            self.DrawTopFlatTriangle(p2, splitPoint, p3)

    def DrawBottomFlatTriangle(self, p1, p2, p3):
        """画平底三角形
        假定平底的两个顶点为v2和v3，上顶点为v1
        """

        def __Init(_p1, _p2, _p3):
            # 确保x2在左，x3在右
            if _p3.x < _p2.x:
                _p2, _p3 = _p3, _p2

            height = _p3.y - _p1.y
            dxLeft = (_p2.x - _p1.x) / height
            dxRight = (_p3.x - _p1.x) / height
            dcLeft = (_p2.color - _p1.color) / height
            dcRight = (_p3.color - _p1.color) / height
            xs = xe = _p1.x
            cs = ce = _p1.color
            return (xs, xe, dxLeft, dxRight), (cs, ce, dcLeft, dcRight)

        self.__DrawClipTriangle(p1, p2, p3, __Init)

    def DrawTopFlatTriangle(self, p1, p2, p3):
        """画平顶三角形
        假定平顶的两个顶点为p1和p2，下顶点为p3
        """

        def __Init(_p1, _p2, _p3):
            # 确保p1在左，p2在右
            if _p2.x < _p1.x:
                _p1, _p2 = _p2, _p1

            height = _p3.y - _p1.y
            dxLeft = (_p3.x - _p1.x) / height
            dxRight = (_p3.x - _p2.x) / height
            dcLeft = (_p3.color - _p1.color) / height
            dcRight = (_p3.color - _p2.color) / height
            xs, xe = _p1.x, _p2.x
            cs, ce = _p1.color, _p2.color
            return (xs, xe, dxLeft, dxRight), (cs, ce, dcLeft, dcRight)

        self.__DrawClipTriangle(p1, p2, p3, __Init)

    def __DrawClipTriangle(self, p1, p2, p3, initFunc):
        x1, y1, c1, x2, y2, c2, x3, y3, c3 = p1.x, p1.y, p1.color, p2.x, p2.y, p2.color, p3.x, p3.y, p3.color
        posInfo, colorInfo = initFunc(p1, p2, p3)
        xs, xe, dxLeft, dxRight = posInfo
        cs, ce, dcLeft, dcRight = colorInfo
        minClipX = self.clipRegion[0].x
        minClipY = self.clipRegion[0].y
        maxClipX = self.clipRegion[1].x
        maxClipY = self.clipRegion[1].y

        # 裁剪Y轴上顶点
        if y1 < minClipY:
            xs = xs + dxLeft * (minClipY - y1)
            xe = xe + dxRight * (minClipY - y1)
            cs = Color.Lerp(c1, c2, minClipY / (y3 - y1))
            ce = Color.Lerp(c1, c3, minClipY / (y3 - y1))
            y1 = minClipY
            iy1 = int(y1)
        else:
            iy1 = math.ceil(y1)
            xs = xs + dxLeft * (iy1 - y1)
            xe = xe + dxRight * (iy1 - y1)

        # 裁剪Y轴下顶点
        if y3 > maxClipY:
            y3 = maxClipY
            c3 = Color.Lerp(c1, c3, maxClipY / (y3 - y1))
            iy3 = int(y3) - 1
        else:
            iy3 = math.ceil(y3) - 1

        # X点都在裁剪范围内
        if minClipX <= x1 <= maxClipX and minClipX <= x2 <= maxClipX and minClipX <= x3 <= maxClipX:
            for loopY in range(iy1, iy3 + 1):
                self.__DrawHorizontalLine(round(xs), round(xe), loopY, cs, ce)
                xs += dxLeft
                xe += dxRight
                cs += dcLeft
                ce += dcRight
        else:
            # 裁剪X轴会稍微慢一些
            for loopY in range(iy1, iy3 + 1):
                left = xs
                right = xe
                leftC = cs
                rightC = ce
                xs += dxLeft
                xe += dxRight
                cs += dcLeft
                ce += dcRight
                if left < minClipX:
                    left = minClipX
                    leftC = Color.Lerp(cs, ce, minClipX / (xe - xs))
                    if right < minClipX:
                        continue
                if right > maxClipX:
                    right = maxClipX
                    rightC = Color.Lerp(cs, ce, maxClipX / (xe - xs))
                    if left > maxClipX:
                        continue
                self.__DrawHorizontalLine(round(left), round(right), loopY, leftC, rightC)

    def __DrawHorizontalLine(self, x1, x2, y, c1, c2):
        """画水平扫描线（颜色不同则对颜色插值）"""
        if x1 > x2:
            x1, x2 = x2, x1
            c1, c2 = c2, c1
        elif x1 == x2:
            return

        sameColor = c1 == c2
        if sameColor:
            for x in range(x1, x2):
                self.buffer.Set((x, y), c1)
        else:
            dc = (c2 - c1) / (x2 - x1)
            color = c1
            for x in range(x1, x2):
                self.buffer.Set((x, y), color)
                color += dc

    def SetClipRegion(self, p1, p2):
        """设置裁剪区域"""
        assert isinstance(p1, Point)
        assert isinstance(p2, Point)
        self.clipRegion[0] = p1
        self.clipRegion[1] = p2


class RenderBuffer(object):
    DefaultWidth = 800
    DefaultHeight = 800

    def __init__(self, width=DefaultWidth, height=DefaultHeight, color=Color()):
        self.width = width
        self.height = height
        self.data = [[color for i in range(self.width)] for j in range(self.height)]
        c = color.tuple
        self.raw = [c for i in range(self.width) for j in range(self.height)]

    def Get(self, pos):
        return self.data[pos[0]][pos[1]]

    def Set(self, pos, color):
        # assert isinstance(color, Color), 'The param color is not a instance of Color'
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.width or pos[1] >= self.height:
            return
        self.data[pos[0]][pos[1]] = color
        self.raw[pos[1] * self.width + pos[0]] = color.tuple

    def Clear(self, color=Color()):
        self.data = [[color for i in range(self.width)] for j in range(self.height)]
        c = color.tuple
        self.raw = [c for i in range(self.width) for j in range(self.height)]

    def GetData(self):
        result = []
        for y in range(self.height):
            for x in range(self.width):
                color = self.data[x][y]
                result.append((color.r, color.g, color.b, color.a))
        return result

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
        image.putdata(buffer.raw)
        # for i in range(image.size[0]):
        #     for j in range(image.size[1]):
        #         pixels[i, j] = buffer.data[i][j].tuple

        image.save(self.filename)


class OpenGLRenderer(RenderInterface):
    pass
