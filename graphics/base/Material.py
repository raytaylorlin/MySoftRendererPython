#!/usr/bin/env python3

from enum import IntFlag
from graphics.core.Color import Color


class MaterialShadeMode(IntFlag):
    Null = 0
    Constant = 1
    Flat = 2
    Phong = 4
    Texture = 8


class Material(object):
    def __init__(self):
        self.attr = MaterialShadeMode.Null
        self.color = Color()
        self.ka = self.kd = self.ks = 0.0
