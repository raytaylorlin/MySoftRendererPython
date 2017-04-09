#!/usr/bin/env python3
import math


class Vector4(object):
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
        return math.sqrt(self.magnitude)

    @property
    def normalized(self):
        temp = Vector4(self.x, self.y, self.z)
        temp.Normalize()
        return temp

    @property
    def vector(self):
        return self.x, self.y, self.z, self.w

    def Normalize(self):
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
        return Vector4(self.x * other, self.y * other, self.z * other)

    def __str__(self):
        return str(self.vector)

    @staticmethod
    def Dot(u, v):
        return u.x * v.x + u.y * v.y + u.z * v.z

    @staticmethod
    def Cross(u, v):
        return Vector4(u.y * v.z - u.z * v.y, u.z * v.x - u.x * v.z, u.x * v.y - u.y * v.x)
