#!/usr/bin/env python3

import test

if __name__ == '__main__':
    test.RunTest()
    # renderer = ImageRenderer('output/test.png')
    # buffer = RenderBuffer()
    # for i in range(buffer.width):
    #     for j in range(buffer.height):
    #         r = random.randint(0, 255)
    #         g = random.randint(0, 255)
    #         b = random.randint(0, 255)
    #         a = 255
    #         buffer.Set((i, j), (r, g, b, a))
    #
    # renderer.Render(buffer)
    # from lib.reader.plg import PLGReader
    # reader = PLGReader('res/cube.plg')
    # data = reader.Load()
    # obj = reader.Deserialize(data)
