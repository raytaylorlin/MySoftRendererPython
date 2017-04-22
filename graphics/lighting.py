#!/usr/bin/env python3

import utils.log as log
from lib.math3d import Vector4, Color


class Light(object):
    def __init__(self, color=None):
        self.isOn = True
        self.color = color or Color()

    def Calculate(self, resultColor, poly):
        log.logger.debug(
            'Result color: {}, light color: {}, poly color: {}'.format(resultColor, self.color, poly.material.color))

    def Turn(self, isOn):
        self.isOn = isOn


class AmbientLight(Light):
    """环境光"""

    def __init__(self, color=None):
        super(AmbientLight, self).__init__(color)

    def Calculate(self, resultColor, poly):
        if isinstance(resultColor, Color):
            Color.Multiply(resultColor, self.color, poly.material.color)
        elif isinstance(resultColor, list):
            for rc in resultColor:
                Color.Multiply(rc, self.color, poly.material.color)
        super(AmbientLight, self).Calculate(resultColor, poly)


class DirectionalLight(Light):
    """方向光"""

    def __init__(self, color=None, direction=None):
        super(DirectionalLight, self).__init__(color)
        self.direction = direction or Vector4()
        self.direction.Normalize()

    def Calculate(self, resultColor, poly):
        # 无穷远光源的计算模型：
        # I(d)dir = I0dir * Cldir （结果即为下方的Idifffuse）
        # 散射光计算公式；
        # Itotald = Rsdiffuse * Idiffuse * (n . l)

        if isinstance(resultColor, Color):
            self.__Calculate(resultColor, poly.GetNormal(), poly.material.color)
            super(DirectionalLight, self).Calculate(resultColor, poly)
        elif isinstance(resultColor, list):
            for i in range(3):
                self.__Calculate(resultColor[i], poly.tvList[i].normal, poly.material.color)

    def __Calculate(self, resultColor, normal, baseColor):
        dp = Vector4.Dot(normal, self.direction)
        if dp > 0:
            i = dp
            Color.Multiply(resultColor, self.color * i, baseColor)


class PointLight(Light):
    """点光源"""

    def __init__(self, color=None, pos=None, params=(1, 0, 0)):
        super(PointLight, self).__init__(color)
        self.pos = pos or Vector4()
        assert isinstance(params, tuple)
        # 二次衰减项系数（分别对应常数，一次项，二次项）
        self.params = params

    def Calculate(self, resultColor, poly):
        # 点光源计算模型：
        #              I0point * Clpoint
        #  I(d)point = ___________________
        #              kc +  kl*d + kq*d2
        #
        #  d = |p - s|

        if isinstance(resultColor, Color):
            self.__Calculate(resultColor, poly.GetNormal(), poly.tvList[0].pos, poly.material.color)
            super(PointLight, self).Calculate(resultColor, poly)
        elif isinstance(resultColor, list):
            for i in range(3):
                self.__Calculate(resultColor[i], poly.tvList[i].normal, poly.tvList[i].pos, poly.material.color)

    def __Calculate(self, resultColor, normal, pos, baseColor):
        l = self.pos - pos
        dist = l.sqrMagnitude
        dp = Vector4.Dot(normal, l)
        if dp > 0:
            a = self.params[0] + self.params[1] * dist + self.params[2] * dist * dist
            i = dp / dist / a
            Color.Multiply(resultColor, self.color * i, baseColor)
