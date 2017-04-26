#!/usr/bin/env python3

import os
from graphics.object import *
from graphics.base import *
from graphics.render import *
from lib.reader.cob import COBReader

outputDir = 'output/base_3shading'


def Main_Test3Shading():
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    log.logger.info('Start base_3shading')
    camera, objList, buffer, renderList, lightList = Init()

    for angle in range(0, 360, 90):
        log.logger.info('Rendering angle={}...'.format(angle))
        RenderOneFrame(camera, objList, buffer, renderList, lightList, angle)


def Init():
    camera = Camera()

    objConstant = COBReader('res/water_constant.cob').LoadObject(EVertexAdjustFlag.SwapYZ)
    objConstant.SetTransform(scale=15, worldPos=Vector4(-50, 0, 100))
    objFlat = COBReader('res/water_flat.cob').LoadObject(EVertexAdjustFlag.SwapYZ)
    objFlat.SetTransform(scale=15, worldPos=Vector4(0, 0, 100))
    objGouraud = COBReader('res/water_gouraud.cob').LoadObject(EVertexAdjustFlag.SwapYZ)
    objGouraud.SetTransform(scale=15, worldPos=Vector4(50, 0, 100))

    buffer = RenderBuffer(color=ColorDefine.Black)
    lightList = [
        AmbientLight(ColorDefine.Gray),
        DirectionalLight(ColorDefine.Gray, direction=Vector4(-1, 0, -1)),
        PointLight(ColorDefine.Magenta, pos=Vector4(0, 4000, 0), params=(0, 0.001, 0)),
        PointLight(ColorDefine.Yellow, pos=Vector4(0, -4000, 0), params=(0, 0.001, 0))
    ]

    renderList = RenderList(Rasterizer(buffer), camera)
    return camera, [objConstant, objFlat, objGouraud], buffer, renderList, lightList


def RenderOneFrame(camera, objList, buffer, renderList, lightList, angle):
    buffer.Clear(color=ColorDefine.Black)
    TransformObject(objList, renderList, angle)
    renderList.PreRender(camera, lightList)
    renderList.RenderSolid()
    Output(buffer, angle)


def TransformObject(objList, renderList, angle):
    renderList.Reset()
    for obj in objList:
        obj.Reset()
        obj.SetEulerRotation(angle, angle, 0)
        renderList.AddObject(obj)


def Output(buffer, angle):
    filename = '{}/{}.png'.format(outputDir, angle)
    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
