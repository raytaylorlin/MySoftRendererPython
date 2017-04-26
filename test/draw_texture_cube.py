#!/usr/bin/env python3

from graphics.object import *
from graphics.base import *
from graphics.render import *
from lib.reader.cob import COBReader


def Main_TestDrawTextureCube():
    DrawCube('output/draw_textured_cube.png', removeBackFace=False)
    # DrawCube('output/draw_cube_removebackface.png', removeBackFace=True)


def DrawCube(filename, removeBackFace):
    camera = Camera()

    obj = COBReader('res/cube_flat_textured.cob').LoadObject(
        adjustFlag=EVertexAdjustFlag.SwapXY, textureFilterMode=ETextureFilterMode.Bilinear)
    obj.SetTransform(scale=25, eulerRotation=(-45, 45, 0), worldPos=Vector4(0, 0, 100))
    obj.material.color = ColorDefine.Black

    buffer = RenderBuffer(color=ColorDefine.Black)
    lightList = [
        AmbientLight(ColorDefine.Gray),
        DirectionalLight(ColorDefine.White, direction=Vector4(-1, 0.5, -1))
    ]
    renderList = RenderList(Rasterizer(buffer), camera)
    renderList.AddObject(obj)
    renderList.PreRender(camera, lightList)
    renderList.RenderSolid()

    renderer = ImageRenderer(filename)
    renderer.Render(buffer)
