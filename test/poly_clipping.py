#!/usr/bin/env python3

from graphics.object import *
from graphics.base import *
from graphics.render import *
from lib.reader.cob import COBReader

outputDir = 'output/poly_clipping'


def Main_TestDrawClippingPoly():
    import os
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    camera, obj, buffer, renderList, lightList = Init()

    for objZ in range(70, 30, -5):
        log.logger.info('Rendering object z = {}...'.format(objZ))
        RenderOneFrame(camera, obj, buffer, renderList, lightList, objZ)


def Init():
    camera = Camera(nearClipZ=50, farClipZ=1000)

    obj = COBReader('res/hammer.cob').LoadObject(
        adjustFlag=EVertexAdjustFlag.SwapYZ, textureFilterMode=ETextureFilterMode.Bilinear)

    obj.material.color = ColorDefine.Black

    buffer = RenderBuffer(color=ColorDefine.Black)
    lightList = [
        AmbientLight(ColorDefine.Gray),
        DirectionalLight(ColorDefine.White, direction=Vector4(-1, 0, -1))
    ]
    renderList = RenderList(Rasterizer(buffer), camera)

    return camera, obj, buffer, renderList, lightList


def RenderOneFrame(camera, obj, buffer, renderList, lightList, objZ):
    buffer.Clear(color=ColorDefine.Black)
    renderList.Reset()
    obj.SetTransform(scale=10, eulerRotation=(0, 135, 0), worldPos=Vector4(0, 0, objZ))
    renderList.AddObject(obj)
    renderList.PreRender(camera, lightList)
    renderList.RenderSolid()

    filename = outputDir + '/z_{}.png'.format(objZ)
    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
