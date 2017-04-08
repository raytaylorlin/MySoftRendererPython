#!/usr/bin/env python3

from math import cos, sin
from lib.math.Vector4 import Vector4


class Matrix4x4(object):
    Zero = [[0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]]

    Identity = [[1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]]

    def __init__(self, matrix=Zero):
        self.data = matrix

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
