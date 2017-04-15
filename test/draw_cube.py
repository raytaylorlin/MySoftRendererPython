#!/usr/bin/env python3

from graphics.object import *
from graphics.base import *
from graphics.render import *
from lib.reader.plg import PLGReader


def TestDrawCube():
    DrawCube('output/draw_cube.png', removeBackFace=False)
    DrawCube('output/draw_cube_removebackface.png', removeBackFace=True)


def DrawCube(filename, removeBackFace):
    camera = Camera(direction=Vector4(0, 0, 0), pos=Vector4(0, 50, 0))

    obj = PLGReader('res/cube.plg').LoadObject()
    obj.SetTransform(scale=5, eulerRotation=(0, 0, 0), worldPos=Vector4(0, 0, 100))

    buffer = RenderBuffer(color=Color(255, 255, 255))
    renderList = RenderList(Rasterizer(buffer))
    renderList.AddObject(obj)
    if removeBackFace:
        renderList.CheckBackFace(camera)
    renderList.TransformWorldToCamera(camera)
    renderList.TransformCameraToPerspective(camera)
    renderList.TransformPerspectiveToScreen(camera)
    renderList.RenderWire()

    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
