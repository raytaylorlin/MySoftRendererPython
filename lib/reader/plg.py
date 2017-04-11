#!/usr/bin/env python3


import parse
import json
from utils import log
from graphics.object import GameObject
from graphics.base import Vertex, Poly


class PLGReader(object):
    def __init__(self, filename):
        self.filename = filename

    def Load(self):
        data = {}

        f = open(self.filename)

        # 读取描述行
        line = self.__GetLine(f)
        data['name'], data['numVertices'], data['numPolys'] = parse.parse('{} {:d} {:d}', line)

        # 读取顶点列表
        data['vertices'] = []
        for i in range(data['numVertices']):
            line = self.__GetLine(f)
            newVertex = [0, 0, 0]
            newVertex[0], newVertex[1], newVertex[2] = parse.parse('{:d} {:d} {:d}', line)
            data['vertices'].append(newVertex)

        # 读取多边形列表
        data['polys'] = []
        for i in range(data['numPolys']):
            line = self.__GetLine(f)
            newPoly = {}
            vertex = [0, 0, 0]
            newPoly['desc'], newPoly['numVertices'], vertex[0], vertex[1], vertex[2] = \
                parse.parse('{} {:d} {:d} {:d} {:d}', line)
            newPoly['vertexIndex'] = vertex
            data['polys'].append(newPoly)

        # log.logger.debug(json.dumps(data, indent=2))
        f.close()

        return data

    def Deserialize(self, data):
        obj = GameObject()
        obj.name = data['name']
        for v in data['vertices']:
            newVertex = Vertex()
            newVertex.SetPosition(v)
            obj.AddVertex(newVertex)

        for p in data['polys']:
            newPoly = Poly()
            for i in p['vertexIndex']:
                newPoly.AddVertex(i, obj.vListLocal[i])
            obj.AddPoly(newPoly)

        return obj

    def LoadObject(self):
        data = self.Load()
        return self.Deserialize(data)

    def __GetLine(self, f):
        while True:
            line = f.readline()
            if not line:
                return None
            stripLine = line.strip()
            if stripLine == '' or stripLine.startswith('#'):
                continue
            return stripLine
