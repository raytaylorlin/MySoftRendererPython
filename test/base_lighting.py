#!/usr/bin/env python3

import os
import math

from graphics.base import Color, ColorDefine
from graphics.lighting import *
from graphics.object import *
from graphics.render import Rasterizer, ImageRenderer
from lib.reader.plg import PLGReader

outputDir = 'output/base_lighting'
numObjects = 4
objectSpacing = 100


def Main_TestBaseLighting():
    # 创建输出目录
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    camera, objModel, buffer, renderList = Init()
    lightList = []

    log.logger.info('Rendering with ambient light...')
    name = 'lighting_a'
    lightList.append(AmbientLight(Color(72, 61, 139)))
    RenderOneFrame(camera, objModel, buffer, renderList, lightList, name)

    log.logger.info('Rendering with ambient light and directional light...')
    name = 'lighting_a_d'
    lightList.append(DirectionalLight(Color(108, 166, 205), direction=Vector4(-1, 1, -0.5)))
    RenderOneFrame(camera, objModel, buffer, renderList, lightList, name)

    log.logger.info('Rendering with ambient light and 2 directional light...')
    name = 'lighting_a_d_d'
    lightList.append(DirectionalLight(Color(200, 200, 200), direction=Vector4(1, 1, 0.5)))
    RenderOneFrame(camera, objModel, buffer, renderList, lightList, name)

    log.logger.info('Rendering with ambient light, point light and 2 directional light...')
    name = 'lighting_a_d_d_p'
    lightList.append(PointLight(Color(205, 79, 57), pos=Vector4(0, 500, 0), params=(1, 0.0005, 0)))
    RenderOneFrame(camera, objModel, buffer, renderList, lightList, name)


def Init():
    """初始化一些固定物体并返回"""
    camera = Camera(cameraType=ECameraType.UVN, pos=Vector4(0, 200, -150), nearClipZ=50, farClipZ=8000)
    objModel = PLGReader('res/cube.plg').LoadObject()
    objModel.SetTransform(scale=5)
    objModel.material.color = ColorDefine.White
    buffer = RenderBuffer(color=ColorDefine.Black)

    # 相机空间排序（可以设置为ESortPolyMethod.Null看看不正常的效果）
    sortPolyMethod = ESortPolyMethod.AverageZ
    renderList = RenderList(Rasterizer(buffer), sortPolyMethod)
    return camera, objModel, buffer, renderList


def RenderOneFrame(camera, objModel, buffer, renderList, lightList, filename):
    buffer.Clear(color=ColorDefine.Black)
    AddObjectBatch(objModel, renderList, camera)
    TransformRenderList(renderList, camera, lightList)

    renderList.RenderSolid()
    # renderList.RenderWire()
    Output(buffer, filename)


def AddObjectBatch(objModel, renderList, camera):
    """根据原模型批量添加到渲染列表中，并根据相机参数剔除物体"""
    renderList.Reset()
    for x in range(-numObjects // 2, numObjects // 2):
        for z in range(-numObjects // 2, numObjects // 2):
            pos = Vector4(x * objectSpacing + objectSpacing // 2, 0, z * objectSpacing + objectSpacing // 2)
            objModel.Reset()
            objModel.SetWorldPosition(pos)
            log.logger.debug('obj world pos = {}'.format(pos))
            # 剔除物体
            if not camera.CullObject(objModel):
                renderList.AddObject(objModel)


def TransformRenderList(renderList, camera, lightList):
    renderList.CheckBackFace(camera)
    renderList.TransformWorldToCamera(camera)
    renderList.Sort()
    renderList.TransformCameraToPerspective(camera)
    renderList.TransformPerspectiveToScreen(camera)
    renderList.CalculateLighting(lightList)


def Output(buffer, filename):
    filename = '{}/{}.png'.format(outputDir, filename)
    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
