#!/usr/bin/env python3

from graphics.base import Color
from graphics.render import Rasterizer, RenderBuffer, ImageRenderer
from lib.math3d import Point


def TestDrawLine():
    buffer = RenderBuffer(color=Color(255, 255, 255))
    rasterizer = Rasterizer(buffer)
    rasterizer.DrawLine(Point(450, 400), Point(650, 500), Color(255, 0, 0))
    rasterizer.DrawLine(Point(350, 400), Point(150, 700), Color(255, 255, 0))
    rasterizer.DrawLine(Point(420, 500), Point(520, 300), Color(0, 0, 255))
    rasterizer.DrawLine(Point(250, 300), Point(150, 50), Color(255, 0, 255))
    rasterizer.DrawLine(Point(50, 400), Point(750, 400), Color(0, 0, 0))
    rasterizer.DrawLine(Point(400, 50), Point(400, 750), Color(0, 0, 0))

    renderer = ImageRenderer('output/draw_line.png')
    renderer.Render(buffer)
