#!/usr/bin/env python3

from PIL import Image


class RenderInterface(object):
    def Render(self, buffer):
        pass


class ImageRenderer(RenderInterface):
    def __init__(self, filename):
        self.filename = filename

    def Render(self, buffer):
        image = Image.new('RGBA', (buffer.width, buffer.height))
        pixels = image.load()
        for i in range(image.size[0]):
            for j in range(image.size[1]):
                pixels[i, j] = buffer.data[i][j]

        image.save(self.filename)


class OpenGLRenderer(RenderInterface):
    pass
