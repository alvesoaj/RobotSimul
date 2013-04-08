# -*- coding: UTF-8 -*-
'''
    @author: zerokol
'''
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import *
from FollowCam import FollowCam
from panda3d.core import Vec3

class Application(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.setupCD()
        self.addWalls()
        
        self.panda = Actor("panda", {"walk": "panda-walk"})
        self.panda.setPos(0, 0, 0)
        self.panda.reparentTo(render)

        self.crate = loader.loadModel("../models/crate")
        self.crate.setPos(0, 0, 0)
        self.crate.setScale(10)
        # self.crate.reparentTo(render)
        
        self.robot = loader.loadModel("../models/robot")
        self.robot.setPos(0, 0, 0)
        self.robot.setScale(5)
        self.robot.reparentTo(render)
        
        self.addCam()
        
        base.disableMouse()
        props = WindowProperties.getDefault()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.resetMouse()
        # don't use -repeat because of slight delay after keydown
        self.pandaWalk = False
        self.pandaReverse = False
        self.pandaLeft = False
        self.pandaRight = False
        self.accept("escape", exit)
        self.accept("w", self.beginWalk)
        self.accept("w-up", self.endWalk)
        self.accept("s", self.beginReverse)
        self.accept("s-up", self.endReverse)
        self.accept("a", self.beginTurnLeft)
        self.accept("a-up", self.endTurnLeft)
        self.accept("d", self.beginTurnRight)
        self.accept("d-up", self.endTurnRight)
        taskMgr.add(self.updatePanda, "update panda")
        
    def setupCD(self):
        base.cTrav = CollisionTraverser()
        # base.cTrav.showCollisions(render)
        self.notifier = CollisionHandlerEvent()
        
        self.notifier.addInPattern("%fn-in-%in")
        self.notifier.addOutPattern("%fn-out-%in")
        
        self.accept("cam-in-house_front", self.onHouseFrontCollision)
        self.accept("cam-out-house_front", self.onHouseFrontUncollision)
        
        self.accept("cam-in-house_back", self.onHouseBackCollision)
        self.accept("cam-out-house_back", self.onHouseBackUncollision)
        
        self.accept("cam-in-house_right_side", self.onHouseRightSideCollision)
        self.accept("cam-out-house_right_side", self.onHouseRightSideUncollision)
        
        self.accept("cam-in-house_left_side", self.onHouseLeftSideCollision)
        self.accept("cam-out-house_left_side", self.onHouseLeftSideUncollision)
        
    def addWalls(self):
        self.house_front = loader.loadModel("../models/house-front")
        self.house_front.setScale(8)
        self.house_front.setPos(0, -28, 8)
        self.house_front.setHpr(180, 0, 0)
        self.house_front.reparentTo(render)
        
        colHF = self.house_front.attachNewNode(CollisionNode("house_front"))
        colHF.node().addSolid(CollisionBox(Point3(-3, -1, -1), Point3(3, 3, 1)))
        # colHF.show()
        
        self.house_back = loader.loadModel("../models/house-back")
        self.house_back.setScale(8)
        self.house_back.setPos(0, 28, 8)
        self.house_back.setHpr(0, 0, 0)
        self.house_back.reparentTo(render)
        
        colHB = self.house_back.attachNewNode(CollisionNode("house_back"))
        colHB.node().addSolid(CollisionBox(Point3(-3, -1, -1), Point3(3, 3, 1)))
        # colHB.show()
        
        self.house_right_side = loader.loadModel("../models/house-side")
        self.house_right_side.setScale(8)
        self.house_right_side.setPos(14, 0, 8)
        self.house_right_side.setHpr(90, 0, 0)
        self.house_right_side.reparentTo(render)
        
        colHRS = self.house_right_side.attachNewNode(CollisionNode("house_right_side"))
        colHRS.node().addSolid(CollisionBox(Point3(-4, -3, -1), Point3(4, 1, 1)))
        # colHRS.show()
        
        self.house_left_side = loader.loadModel("../models/house-side")
        self.house_left_side.setScale(8)
        self.house_left_side.setPos(-14, 0, 8)
        self.house_left_side.setHpr(-90, 0, 0)
        self.house_left_side.reparentTo(render)
        
        colHLS = self.house_left_side.attachNewNode(CollisionNode("house_left_side"))
        colHLS.node().addSolid(CollisionBox(Point3(-4, -3, -1), Point3(4, 1, 1)))
        # colHLS.show()
        
    def addCam(self):
        self.cam.setPos(0, -20, 6)

        self.followCam = FollowCam(self.cam, self.panda)
        
        col = self.cam.attachNewNode(CollisionNode("cam"))
        col.node().addSolid(CollisionSphere(0, 10, 6, 4))
        col.show()
        
        base.cTrav.addCollider(col, self.notifier)
        
    def onHouseFrontCollision(self, entry):
        self.house_front.hide()
        
    def onHouseFrontUncollision(self, entry):
        self.house_front.show()
        
    def onHouseBackCollision(self, entry):
        self.house_back.hide()
        
    def onHouseBackUncollision(self, entry):
        self.house_back.show()
        
    def onHouseRightSideCollision(self, entry):
        self.house_right_side.hide()
    
    def onHouseRightSideUncollision(self, entry):
        self.house_right_side.show()
        
    def onHouseLeftSideCollision(self, entry):
        self.house_left_side.hide()
    
    def onHouseLeftSideUncollision(self, entry):
        self.house_left_side.show()
        
    def resetMouse(self):
        cx = base.win.getProperties().getXSize() / 2
        cy = base.win.getProperties().getYSize() / 2
        base.win.movePointer(0, cx, cy)

    def beginWalk(self):
        self.panda.setPlayRate(1.0, "walk")
        self.panda.loop("walk")
        self.pandaWalk = True
    
    def endWalk(self):
        self.panda.stop()
        self.pandaWalk = False
    
    def beginReverse(self):
        self.panda.setPlayRate(-1.0, "walk")
        self.panda.loop("walk")
        self.pandaReverse = True
        
    def endReverse(self):
        self.panda.stop()
        self.pandaReverse = False
        
    def beginTurnLeft(self):
        self.pandaLeft = True
        
    def endTurnLeft(self):
        self.pandaLeft = False
        
    def beginTurnRight(self):
        self.pandaRight = True
        
    def endTurnRight(self):
        self.pandaRight = False

    def updatePanda(self, task):
        if base.mouseWatcherNode.hasMouse():
            self.panda.setH(self.panda, -base.mouseWatcherNode.getMouseX() * 10)
        self.resetMouse()
        
        if self.pandaWalk:
            self.panda.setY(self.panda, -0.4)
        elif self.pandaReverse:
            self.panda.setY(self.panda, 0.4)
            
        if self.pandaLeft:
            self.panda.setH(self.panda, 1.6)
        elif self.pandaRight:
            self.panda.setH(self.panda, -1.6)
            
        return task.cont

