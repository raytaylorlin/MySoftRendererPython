#!/usr/bin/env python3
from graphics.base import Color
from lib.math3d import Vector4


class Light(object):
    def __init__(self, color=Color()):
        self.isOn = True
        self.color = color

    def Calculate(self, resultColor, poly):
        return self.color

    def Turn(self, isOn):
        self.isOn = isOn


class AmbientLight(Light):
    """环境光"""
    def __init__(self, color=Color()):
        super(AmbientLight, self).__init__(color)

    def Calculate(self, resultColor, poly):
        Color.Multiply(resultColor, self.color, poly.material.color)


class DirectionalLight(Light):
    """方向光"""
    def __init__(self, color=Color(), direction=Vector4()):
        super(DirectionalLight, self).__init__(color)
        self.direction = direction
        self.direction.Normalize()

    def Calculate(self, resultColor, poly):
        # 无穷远光源的计算模型：
        # I(d)dir = I0dir * Cldir （结果即为下方的Idifffuse）
        # 散射光计算公式；
        # Itotald = Rsdiffuse * Idiffuse * (n . l)
        n = poly.GetNormal()
        dp = Vector4.Dot(n, self.direction)
        if dp > 0:
            Color.Multiply(resultColor, self.color * dp, poly.material.color)

        return self.color


class PointColor(Light):
    """点光源"""
    def __init__(self, color=Color(), pos=Vector4(), params=(1, 0, 0)):
        super(PointColor, self).__init__(color)
        self.pos = pos
        assert isinstance(params, tuple)
        self.params = params

    def Calculate(self, result, base):
        return self.color
