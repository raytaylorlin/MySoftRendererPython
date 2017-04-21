#!/usr/bin/env python3

import random
from math import cos, sin, radians, sqrt


class Matrix4x4(object):
    """4*4矩阵"""

    def __init__(self, matrix=None):
        self.data = [[0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]] if matrix is None else matrix

    def __mul__(self, other):
        if isinstance(other, Vector4):
            result = Vector4()
            resultData = result.data
            for i in range(4):
                s = 0
                for j in range(4):
                    s += self.data[i][j] * other.data[j]
                resultData[i] = s
            return result

        elif isinstance(other, Matrix4x4):
            result = Matrix4x4()
            resultData = result.data
            for row in range(4):
                for col in range(4):
                    s = 0
                    for i in range(4):
                        s += self.data[row][i] * other.data[i][col]
                    resultData[row][col] = s
            return result

        else:
            raise Exception('The param other is not Vector4 or Matrix4x4 type')

    @staticmethod
    def GetRotateMatrix(thetaX, thetaY, thetaZ):
        # 先转换成弧度
        thetaX = radians(thetaX)
        thetaY = radians(thetaY)
        thetaZ = radians(thetaZ)
        mx = [[1, 0, 0, 0],
              [0, cos(thetaX), sin(thetaX), 0],
              [0, -sin(thetaX), cos(thetaX), 0],
              [0, 0, 0, 1]]
        my = [[cos(thetaY), 0, -sin(thetaY), 0],
              [0, 1, 0, 0],
              [sin(thetaY), 0, cos(thetaY), 0],
              [0, 0, 0, 1]]
        mz = [[cos(thetaZ), sin(thetaZ), 0, 0],
              [-sin(thetaZ), cos(thetaZ), 0, 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1]]
        seq = 0

        # 1，2，4分别表示在X，Y，Z轴有旋转
        if thetaX != 0:
            seq |= 1
        if thetaY != 0:
            seq |= 2
        if thetaZ != 0:
            seq |= 4

        rotateDict = {
            0: lambda: Matrix4x4.Identity,
            1: lambda: Matrix4x4(mx),
            2: lambda: Matrix4x4(my),
            4: lambda: Matrix4x4(mz),
            3: lambda: Matrix4x4(mx) * Matrix4x4(my),  # xy旋转
            5: lambda: Matrix4x4(mx) * Matrix4x4(mz),  # xz旋转
            6: lambda: Matrix4x4(mx) * Matrix4x4(my),  # yz旋转
            7: lambda: Matrix4x4(mx) * Matrix4x4(my) * Matrix4x4(mz)  # xyz旋转
        }
        func = rotateDict.get(seq)
        return func()


Matrix4x4.Zero = Matrix4x4([[0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [0, 0, 0, 0]])

Matrix4x4.Identity = Matrix4x4([[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1]])


class Vector4(object):
    """4D向量"""

    Zero = [0, 0, 0, 1]

    def __init__(self, x=0, y=0, z=0, w=1):
        self.data = [x, y, z, w]

    @property
    def x(self):
        return self.data[0]

    @x.setter
    def x(self, value):
        self.data[0] = value

    @property
    def y(self):
        return self.data[1]

    @y.setter
    def y(self, value):
        self.data[1] = value

    @property
    def z(self):
        return self.data[2]

    @z.setter
    def z(self, value):
        self.data[2] = value

    @property
    def w(self):
        return self.data[3]

    @w.setter
    def w(self, value):
        self.data[3] = value

    @property
    def magnitude(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    @property
    def sqrMagnitude(self):
        return sqrt(self.magnitude)

    @property
    def normalized(self):
        temp = Vector4(self.x, self.y, self.z)
        temp.Normalize()
        return temp

    @property
    def vector(self):
        return self.x, self.y, self.z, self.w

    def Normalize(self):
        if self.x == 0 and self.y == 0 and self.z == 0:
            return
        mag = self.sqrMagnitude
        self.x /= mag
        self.y /= mag
        self.z /= mag

    def IsZero(self):
        return self.x == 0 and self.y == 0 and self.z == 0

    def __add__(self, other):
        return Vector4(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector4(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Vector4(self.x * other, self.y * other, self.z * other)
        if isinstance(other, Vector4):
            s = 0
            for i in range(4):
                s += self.data[i] + other.data[i]
            return s
        elif isinstance(other, Matrix4x4):
            result = Vector4()
            resultData = result.data
            for col in range(4):
                s = 0
                for row in range(4):
                    s += self.data[row] * other.data[row][col]
                resultData[col] = s
            return result
        else:
            raise Exception('The param other is not int, Vector4 or Matrix4x4 type')

    def __str__(self):
        return str(self.vector)

    @staticmethod
    def Dot(u, v):
        return u.x * v.x + u.y * v.y + u.z * v.z

    @staticmethod
    def Cross(u, v):
        return Vector4(u.y * v.z - u.z * v.y, u.z * v.x - u.x * v.z, u.x * v.y - u.y * v.x)


class Color(object):
    """颜色"""

    def __init__(self, r=0, g=0, b=0, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @property
    def tuple(self):
        return round(self.r), round(self.g), round(self.b), round(self.a)

    @staticmethod
    def Multiply(result, color1, color2):
        r = color1.r * color2.r // 256
        g = color1.g * color2.g // 256
        b = color1.b * color2.b // 256
        result.r = min(result.r + r, 255)
        result.g = min(result.g + g, 255)
        result.b = min(result.b + b, 255)

    @staticmethod
    def Lerp(a, b, t):
        if t < 0:
            t = 0
        elif t > 1:
            t = 1
        return Color(a.r + (b.r - a.r) * t, a.g + (b.g - a.g) * t, a.b + (b.b - a.b) * t, a.a + (b.a - a.a) * t)

    @staticmethod
    def Random(transparent=False):
        return Color(random.randrange(255), random.randrange(255), random.randrange(255),
                     random.randrange(255) if transparent else 255)

    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b, self.a)

    def __sub__(self, other):
        return Color(self.r - other.r, self.g - other.g, self.b - other.b, self.a)

    def __mul__(self, other):
        return Color(self.r * other, self.g * other, self.b * other, self.a)

    def __truediv__(self, other):
        return Color(self.r / other, self.g / other, self.b / other, self.a)

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def __str__(self):
        return str((self.r, self.g, self.b, self.a))


class ColorDefine(object):
    Black = Color(0, 0, 0)
    White = Color(255, 255, 255)
    Red = Color(255, 0, 0)
    Green = Color(0, 255, 0)
    Blue = Color(0, 0, 255)
    Yellow = Color(255, 255, 0)
    Cyan = Color(0, 255, 255)
    Magenta = Color(255, 0, 255)


class Point(object):
    """简单2D点定义"""

    def __init__(self, x=0, y=0, color=ColorDefine.Black):
        self.x = x
        self.y = y
        self.color = color

    def __str__(self):
        return '{} {}'.format((self.x, self.y), self.color)
