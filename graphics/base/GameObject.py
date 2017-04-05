#!/usr/bin/env python3

from enum import IntFlag


class GameObjectState(IntFlag):
    Null = 0
    Active = 1
    Visible = 2
    Culled = 4


class GameObjectAttribute(IntFlag):
    Null = 0
    SingleFrame = 1
    MultiFrame = 2
    Textures = 4


class GameObject(object):
    def __init__(self):
        self.state = GameObjectState.Active | GameObjectState.Visible
        self.attr = GameObjectAttribute.Null
        self.name = ''
        self.vListLocal = []
        self.vListTrans = []
        self.polyList = []

    def AddVertex(self, v):
        self.vListLocal.append(v)
        self.vListTrans.append(v)

    def AddPoly(self, p):
        self.polyList.append(p)