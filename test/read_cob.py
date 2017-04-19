#!/usr/bin/env python3


from graphics.object import *
from graphics.base import *
from graphics.render import *
from lib.reader.cob import COBReader


def Main_TestReadCOB():
    camera = Camera(direction=Vector4(0, 0, 0), pos=Vector4(0, 0, 0))

    obj = COBReader('res/hammer.cob').LoadObject(EVertexAdjustFlag.SwapYZ)
    obj.SetTransform(scale=10, eulerRotation=(0, 135, 0), worldPos=Vector4(0, 0, 50))
    # obj.material.color = ColorDefine.Black

    buffer = RenderBuffer(color=ColorDefine.Black)
    renderList = RenderList(Rasterizer(buffer))
    renderList.AddObject(obj)

    renderList.CheckBackFace(camera)
    renderList.TransformWorldToCamera(camera)
    renderList.TransformCameraToPerspective(camera)
    renderList.TransformPerspectiveToScreen(camera)
    renderList.RenderWire()

    renderer = ImageRenderer('output/read_cob.png')
    renderer.Render(buffer)
