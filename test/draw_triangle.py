#!/usr/bin/env python3

from graphics.base import Color, ColorDefine
from graphics.render import Rasterizer, RenderBuffer, ImageRenderer
from lib.math3d import Point
from utils import log


def Main_TestDrawTriangle():
    log.logger.info('Drawing triangle...')
    DrawTriangle('output/draw_triangle.png')

    topLeft = Point(100, 150)
    bottomRight = Point(650, 600)
    log.logger.info('Drawing triangle with clip region({}, {})...'.format(topLeft, bottomRight))
    DrawTriangle('output/draw_triangle_clip.png', topLeft, bottomRight)


def DrawTriangle(filename, clipRegionTopLeft=None, clipRegionBottomRight=None):
    buffer = RenderBuffer(color=ColorDefine.White)
    rasterizer = Rasterizer(buffer)

    if clipRegionTopLeft and clipRegionBottomRight:
        rasterizer.SetClipRegion(clipRegionTopLeft, clipRegionBottomRight)
        rasterizer.DrawRectangle(clipRegionTopLeft, clipRegionBottomRight, ColorDefine.Black)
    rasterizer.DrawTriangle(Point(0, 100), Point(200, 100), Point(300, 400), ColorDefine.Red)
    rasterizer.DrawTriangle(Point(600, 200), Point(550, 400), Point(750, 400), ColorDefine.Green)
    rasterizer.DrawTriangle(Point(200, 400), Point(100, 550), Point(350, 700), ColorDefine.Blue)
    rasterizer.DrawTriangle(Point(600, 450), Point(700, 650), Point(350, 750), ColorDefine.Blue)

    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
