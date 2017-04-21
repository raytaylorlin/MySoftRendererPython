#!/usr/bin/env python3

import os
from graphics.base import Vertex
from graphics.render import Rasterizer, RenderBuffer, ImageRenderer
from lib.math3d import Point, Color, ColorDefine
from utils import log

outputDir = 'output/triangle'


def Main_TestDrawTriangle():
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    log.logger.info('Drawing triangle...')
    DrawTriangle(outputDir + '/simple.png')

    topLeft = Point(100, 150)
    bottomRight = Point(650, 600)
    log.logger.info('Drawing triangle with clip region({}, {})...'.format(topLeft, bottomRight))
    DrawTriangle(outputDir + '/simple_clip.png', topLeft, bottomRight)


def DrawTriangle(filename, clipRegionTopLeft=None, clipRegionBottomRight=None):
    buffer = RenderBuffer(color=ColorDefine.White)
    rasterizer = Rasterizer(buffer)

    # 设置并画裁剪框
    if clipRegionTopLeft and clipRegionBottomRight:
        rasterizer.SetClipRegion(clipRegionTopLeft, clipRegionBottomRight)
        rasterizer.DrawRectangle(clipRegionTopLeft, clipRegionBottomRight, ColorDefine.Black)
    rasterizer.DrawTriangle(Point(0, 100, ColorDefine.Red),
                            Point(200, 100, ColorDefine.Red),
                            Point(300, 400, ColorDefine.Red))
    rasterizer.DrawTriangle(Point(600, 200, ColorDefine.Green),
                            Point(550, 400, ColorDefine.Green),
                            Point(750, 400, ColorDefine.Green))
    rasterizer.DrawTriangle(Point(200, 400, ColorDefine.Blue),
                            Point(100, 550, ColorDefine.Blue),
                            Point(350, 700, ColorDefine.Blue))
    rasterizer.DrawTriangle(Point(600, 450, ColorDefine.Blue),
                            Point(700, 650, ColorDefine.Blue),
                            Point(350, 750, ColorDefine.Blue))

    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
