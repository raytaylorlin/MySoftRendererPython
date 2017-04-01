#!/usr/bin/env python3
import math


class Vector4(object):
    Zero = [0, 0, 0, 1]

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.w = 1

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
        return (self.x, self.y, self.z, self.w)

    def Normalize(self):
        mag = self.sqrMagnitude
        self.x /= mag
        self.y /= mag
        self.z /= mag

    def __add__(self, other):
        return Vector4(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector4(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Vector4(self.x * other, self.y * other, self.z * other)

    @staticmethod
    def Dot(u, v):
        return u.x * v.x + u.y * v.y + u.z * v.z

    @staticmethod
    def Cross(u, v):
        return Vector4(u.y * v.z - u.z * v.y, u.z * v.x - u.x * v.z, u.x * v.y - u.y * v.x)
