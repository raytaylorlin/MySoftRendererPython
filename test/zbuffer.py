#!/usr/bin/env python3

from graphics.object import *
from graphics.base import *
from graphics.render import *
from lib.reader.cob import COBReader
from lib.reader.plg import PLGReader

outputDir = 'output/zbuffer'


def Main_TestZBuffer():
    import os
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    camera, texturedCube, normalCube, buffer, zbuffer, renderList, lightList = Init()

    for objZ in range(60, 150, 10):
        log.logger.info('Rendering object z = {}...'.format(objZ))
        RenderOneFrame(camera, texturedCube, normalCube, buffer, zbuffer, renderList, lightList, objZ)


def Init():
    camera = Camera()

    texturedCube = COBReader('res/cube_flat_textured.cob').LoadObject(
        adjustFlag=EVertexAdjustFlag.SwapXY)
    texturedCube.SetTransform(scale=25, eulerRotation=(-45, 45, 0), worldPos=Vector4(0, 0, 100))
    texturedCube.material.color = ColorDefine.Black

    normalCube = PLGReader('res/cube.plg').LoadObject()
    normalCube.SetTransform(scale=5, eulerRotation=(0, 45, 0), worldPos=Vector4(0, 0, 100))
    normalCube.material.color = ColorDefine.White

    buffer = RenderBuffer(color=ColorDefine.Black)
    # 可以将下面置为None看看错误的效果
    zbuffer = ZBuffer()
    lightList = [
        AmbientLight(ColorDefine.Gray),
        DirectionalLight(ColorDefine.White, direction=Vector4(-1, 0.5, -1))
    ]
    renderList = RenderList(Rasterizer(buffer, zbuffer), camera)

    return camera, texturedCube, normalCube, buffer, zbuffer, renderList, lightList


def RenderOneFrame(camera, texturedCube, normalCube, buffer, zbuffer, renderList, lightList, objZ):
    buffer.Clear(color=ColorDefine.Black)
    if zbuffer:
        zbuffer.Clear()

    texturedCube.SetWorldPosition(Vector4(0, 0, objZ))
    renderList.Reset()
    renderList.AddObject(texturedCube)
    renderList.AddObject(normalCube, useObjectMaterial=True)
    renderList.PreRender(camera, lightList)
    renderList.RenderSolid()

    filename = outputDir + '/z_{}.png'.format(objZ)
    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
