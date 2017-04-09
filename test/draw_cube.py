#!/usr/bin/env python3

from graphics.base.Camera import Camera
from graphics.base.Color import Color
from graphics.base.RenderList import RenderList
from graphics.core.Rasterizer import Rasterizer
from graphics.core.RenderBuffer import RenderBuffer
from graphics.core.RenderInterface import ImageRenderer
from lib.math.Vector4 import Vector4
from lib.reader.plg import PLGReader
from lib.math.Point import Point


def TestDrawCube():
    DrawCube('output/draw_cube.png', removeBackFace=False)
    DrawCube('output/draw_cube_removebackface.png', removeBackFace=True)


def DrawCube(filename, removeBackFace):
    camera = Camera()

    obj = PLGReader('res/cube.plg').LoadObject()
    obj.SetTransform(scale=5, eulerRotation=(0, 45, 0), worldPos=Vector4(0, 0, 100))

    buffer = RenderBuffer(color=Color(255, 255, 255))
    renderList = RenderList(Rasterizer(buffer))
    renderList.AddObject(obj, insertLocal=False)
    if removeBackFace:
        renderList.CheckBackFace(camera)
    renderList.TransformWorldToCamera(camera)
    renderList.TransformCameraToPerspective(camera)
    renderList.TransformPerspectiveToScreen(camera)
    renderList.RenderWire()

    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
