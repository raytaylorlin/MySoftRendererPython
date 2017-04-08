#!/usr/bin/env python3

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

        else:
            raise Exception('The param other is not Vector4 or Matrix4x4 type')
