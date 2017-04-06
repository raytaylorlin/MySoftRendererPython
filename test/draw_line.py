#!/usr/bin/env python3

from graphics.base.Color import Color
from graphics.core.Rasterizer import Rasterizer
from graphics.core.RenderBuffer import RenderBuffer
from graphics.core.RenderInterface import ImageRenderer
from lib.math.Point import Point


def TestDrawLine():
    buffer = RenderBuffer()
    rasterizer = Rasterizer(buffer)
    rasterizer.DrawLine(Point(450, 400), Point(650, 500), Color(255, 0, 0))
    rasterizer.DrawLine(Point(350, 400), Point(150, 700), Color(255, 255, 0))
    rasterizer.DrawLine(Point(420, 500), Point(520, 300), Color(0, 0, 255))
    rasterizer.DrawLine(Point(250, 300), Point(150, 50), Color(255, 0, 255))
    rasterizer.DrawLine(Point(50, 400), Point(750, 400), Color(255, 255, 255))
    rasterizer.DrawLine(Point(400, 50), Point(400, 750), Color(255, 255, 255))

    renderer = ImageRenderer('output/drawline.png')
    renderer.Render(buffer)
