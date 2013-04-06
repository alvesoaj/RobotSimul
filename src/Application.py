# -*- coding: UTF-8 -*-
'''
    @author: zerokol
'''
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import Vec3

class Application(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.crate = loader.loadModel("../models/crate")
        self.crate.reparentTo(render)
        self.crate.setPos(-5, 0, 0)
        self.cam.setPos(0, -30, 6)
