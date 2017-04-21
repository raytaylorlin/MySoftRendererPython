#!/usr/bin/env python3


import parse
import json
from utils import log
from graphics.object import GameObject
from graphics.base import *
from lib.math3d import *


class COBReader(object):
    def __init__(self, filename):
        self.filename = filename

    def Load(self):
        data = {}

        f = open(self.filename)

        # 名字
        while True:
            line = self.__GetLine(f)
            r = parse.parse('Name {}', line)
            if r and len(r.fixed) > 0:
                data['name'] = r[0]
                break

        # center和三轴偏移
        while True:
            line = self.__GetLine(f)
            r = parse.parse('center {:g} {:g} {:g}', line)
            if r and len(r.fixed) == 3:
                data['center'] = [r[0], r[1], r[2]]

                r = parse.parse('x axis {:g} {:g} {:g}', self.__GetLine(f))
                data['xAxis'] = [r[0], r[1], r[2]]
                r = parse.parse('y axis {:g} {:g} {:g}', self.__GetLine(f))
                data['yAxis'] = [r[0], r[1], r[2]]
                r = parse.parse('z axis {:g} {:g} {:g}', self.__GetLine(f))
                data['zAxis'] = [r[0], r[1], r[2]]
                break

        # 4x4变换矩阵
        while True:
            line = self.__GetLine(f)
            if line.strip() == 'Transform':
                transform = []
                for i in range(4):
                    r = parse.parse('{:g} {:g} {:g} {:g}', self.__GetLine(f))
                    transform.append([r[0], r[1], r[2], r[3]])
                data['transform'] = transform
                break

        # 顶点列表
        while True:
            line = self.__GetLine(f)
            r = parse.parse('World Vertices {:d}', line)
            if len(r.fixed) == 1:
                data['numVertices'] = r[0]
                data['vertices'] = []
                for i in range(data['numVertices']):
                    r = parse.parse('{:g} {:g} {:g}', self.__GetLine(f))
                    data['vertices'].append([r[0], r[1], r[2]])
                break

        # 纹理顶点列表
        while True:
            line = self.__GetLine(f)
            r = parse.parse('Texture Vertices {:d}', line)
            if r and len(r.fixed) == 1:
                data['numTextureVertices'] = r[0]
                data['textureVertices'] = []
                for i in range(data['numTextureVertices']):
                    r = parse.parse('{:g} {:g}', self.__GetLine(f))
                    data['textureVertices'].append([r[0], r[1]])
                break

        # 多边形列表
        materialIndex = set()
        while True:
            line = self.__GetLine(f)
            r = parse.parse('Faces {:d}', line)
            if r and len(r.fixed) == 1:
                data['numPolys'] = r[0]
                data['polys'] = []
                for i in range(data['numPolys']):
                    poly = {}
                    poly['numVertices'], poly['flags'], poly['mat'] = parse.parse('Face verts {:d} flags {:d} mat {:d}',
                                                                                  self.__GetLine(f))
                    materialIndex.add(poly['mat'])
                    # 024为顶点索引，135为纹理索引
                    r = parse.parse('<{:d},{:d}> <{:d},{:d}> <{:d},{:d}>', self.__GetLine(f))
                    poly['vertexIndex'] = [r[0], r[2], r[4]]
                    poly['textureIndex'] = [r[1], r[3], r[5]]
                    data['polys'].append(poly)
                data['numMaterials'] = len(materialIndex)
                break

        # 材质
        data['materials'] = []
        for i in range(data['numMaterials']):
            material = {}
            material['shaders'] = []
            while True:
                line = self.__GetLine(f)
                r = parse.parse('mat# {:d}', line)
                # 材质头部信息
                if r and len(r.fixed) == 1:
                    material['index'] = r[0]
                    material['shader'], material['facet'] = parse.parse('shader: {}  facet: {}', self.__GetLine(f))
                    r = parse.parse('rgb {:g},{:g},{:g}', self.__GetLine(f))
                    material['rgb'] = [r[0], r[1], r[2]]
                    material['alpha'], material['ka'], material['ks'], material['exp'], material['ior'] = \
                        parse.parse('alpha {:g}  ka {:g}  ks {:g}  exp {:g}  ior {:g}', self.__GetLine(f))
                    # 跳过一行
                    line = self.__GetLine(f)
                    break

            while True:
                line = self.__GetLine(f)
                if line.startswith('Mat1') or line.startswith('END'):
                    break

                # 材质shader信息
                shader = {}
                shader['class'] = parse.parse('Shader class: {}', line)[0]
                shader['name'] = parse.parse('Shader name: "{}" ({})', self.__GetLine(f))[0]
                shader['numParams'] = parse.parse('Number of parameters: {:d}', self.__GetLine(f))[0]
                shader['params'] = []
                for j in range(shader['numParams']):
                    paramKey, paramType, paramValue = parse.parse('{}: {} {}', self.__GetLine(f))
                    shader['params'].append({'key': paramKey, 'type': paramType, 'value': paramValue})
                shader['flags'] = parse.parse('Flags: {:d}', self.__GetLine(f))[0]
                material['shaders'].append(shader)

            data['materials'].append(material)

        log.logger.debug(json.dumps(data, indent=2))
        f.close()

        return data

    def Deserialize(self, data, adjustFlag):
        obj = GameObject()
        obj.name = data['name']
        for v in data['vertices']:
            newVertex = Vertex()
            newVertex.SetPosition(v)
            newVertex.Adjust(adjustFlag)
            obj.AddVertex(newVertex)

        materialList = []
        materialShaderDict = {
            'constant': EMaterialShadeMode.Constant,
            'matte': EMaterialShadeMode.Flat,
            'phong': EMaterialShadeMode.Phong,
            'plastic': EMaterialShadeMode.Gouraud
        }
        for m in data['materials']:
            material = Material()
            map(lambda x: int(x * 256), m['rgb'])
            material.color = Color(int(m['rgb'][0] * 255), int(m['rgb'][1] * 255), int(m['rgb'][2] * 255),
                                   int(m['alpha'] * 255))
            print(material.color)
            # kd暂且设为1
            material.ka, material.kd, material.ks = m['ka'], 1, m['ks']
            for s in m['shaders']:
                if s['class'] == 'reflectance':
                    material.mode = materialShaderDict[s['name']]
            materialList.append(material)

        for p in data['polys']:
            newPoly = Poly()
            newPoly.material = materialList[p['mat']]
            for i in p['vertexIndex']:
                newPoly.AddVertex(i, obj.vListLocal[i])
            obj.AddPoly(newPoly)

        return obj

    def LoadObject(self, adjustFlag=EVertexAdjustFlag.Null):
        data = self.Load()
        return self.Deserialize(data, adjustFlag)

    def __GetLine(self, f):
        while True:
            line = f.readline()
            if not line:
                return None
            stripLine = line.strip()
            if stripLine == '' or stripLine.startswith('#'):
                continue
            return stripLine
