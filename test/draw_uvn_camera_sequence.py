#!/usr/bin/env python3

import os
import math

from lib.math3d import Color, ColorDefine
from graphics.object import *
from graphics.render import Rasterizer, ImageRenderer
from lib.reader.plg import PLGReader

outputDir = 'output/uvn_camera_result'
numObjects = 8
objectSpacing = 500


def Main_TestUVNCameraSequence():
    # 创建输出目录
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    camera, objModel, buffer, renderList = Init()

    for angle in range(0, 360, 10):
        log.logger.info('Rendering angle={}...'.format(angle))
        RenderOneFrame(camera, objModel, buffer, renderList, angle)


def Init():
    """初始化一些固定物体并返回"""
    camera = Camera(cameraType=ECameraType.UVN, nearClipZ=50, farClipZ=8000)
    objModel = PLGReader('res/tank.plg').LoadObject()
    objModel.material.color = ColorDefine.Black
    buffer = RenderBuffer(color=ColorDefine.White)
    renderList = RenderList(Rasterizer(buffer))
    return camera, objModel, buffer, renderList


def RenderOneFrame(camera, objModel, buffer, renderList, angle):
    buffer.Clear(color=ColorDefine.White)
    SetCameraParams(camera, angle)
    AddObjectBatch(objModel, renderList, camera)
    TransformRenderList(renderList, camera)
    renderList.RenderWire()
    Output(buffer, angle)


def SetCameraParams(camera, angle):
    """设置相机参数"""
    cameraDistance = 1000
    radian = math.radians(angle)
    camera.pos = Vector4(cameraDistance * math.cos(radian),
                         cameraDistance * math.sin(radian),
                         2 * cameraDistance * math.sin(radian))
    camera.lookAt = Vector4()


def AddObjectBatch(objModel, renderList, camera):
    """根据原模型批量添加到渲染列表中，并根据相机参数剔除物体"""
    renderList.Reset()
    for x in range(-numObjects // 2, numObjects // 2):
        for z in range(-numObjects // 2, numObjects // 2):
            pos = Vector4(x * objectSpacing + objectSpacing // 2, 0, z * objectSpacing + objectSpacing // 2)
            objModel.Reset()
            objModel.SetWorldPosition(pos)
            # 剔除物体
            if not camera.CullObject(objModel):
                renderList.AddObject(objModel, useObjectMaterial=True)


def TransformRenderList(renderList, camera):
    renderList.TransformWorldToCamera(camera)
    renderList.TransformCameraToPerspective(camera)
    renderList.TransformPerspectiveToScreen(camera)


def Output(buffer, angle):
    filename = '{}/{}.png'.format(outputDir, angle)
    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
