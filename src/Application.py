# -*- coding: UTF-8 -*-
'''
    @author: zerokol
'''
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import *
from FollowCam import FollowCam
from panda3d.core import Vec3
from direct.gui.OnscreenImage import OnscreenImage

from PIL import Image, ImageDraw
from pylab import *
import os

lineNum = 31
columnNum = 59
matrix = [[127 for i in xrange(columnNum)] for i in xrange(lineNum)]

class Application(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
            
        self.setupCD()
        
        self.addWalls()
        
        self.floor = loader.loadModel("../models/floor")
        self.floor.setPos(0, 0, -1)
        self.floor.setScale(6)
        self.floor.reparentTo(render)

        self.addActor()
        
        self.addObstacles()
        
        self.addCam()
        
        base.disableMouse()

        self.drawChart()
        
        props = WindowProperties.getDefault()
        props.setCursorHidden(True)
        props.setTitle("AJ's Robot Simuluator - Robotic Class")
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
        
        self.accept("p", self.getActorPoint)

        taskMgr.add(self.updatePanda, "update panda")
        # taskMgr.doMethodLater(1, self.checkRobotray, "check robotray")
        
    def setupCD(self):
        base.cTrav = CollisionTraverser()
        # base.cTrav.showCollisions(render)

        self.pusher = CollisionHandlerPusher()
        
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

        self.accept("robotray-in-house_front", self.onRayCollision)
        self.accept("robotray-in-house_back", self.onRayCollision)
        self.accept("robotray-in-house_right_side", self.onRayCollision)
        self.accept("robotray-in-house_left_side", self.onRayCollision)
        self.accept("robotray-in-crate", self.onRayCollision)
        self.accept("robotray-in-tri", self.onRayCollision)
        
    def addWalls(self):
        self.house_front = loader.loadModel("../models/house-front")
        self.house_front.setScale(8)
        self.house_front.setPos(0, -28, 8)
        self.house_front.setHpr(180, 0, 0)
        self.house_front.reparentTo(render)
        
        colHF = self.house_front.attachNewNode(CollisionNode("house_front"))
        colHF.node().addSolid(CollisionBox(Point3(-4, 0, -1), Point3(4, 4, 1)))
        # colHF.show()
        
        self.house_back = loader.loadModel("../models/house-back")
        self.house_back.setScale(8)
        self.house_back.setPos(0, 28, 8)
        self.house_back.setHpr(0, 0, 0)
        self.house_back.reparentTo(render)
        
        colHB = self.house_back.attachNewNode(CollisionNode("house_back"))
        colHB.node().addSolid(CollisionBox(Point3(-4, 0, -1), Point3(4, 4, 1)))
        # colHB.show()
        
        self.house_right_side = loader.loadModel("../models/house-side")
        self.house_right_side.setScale(8)
        self.house_right_side.setPos(14, 0, 8)
        self.house_right_side.setHpr(90, 0, 0)
        self.house_right_side.reparentTo(render)
        
        colHRS = self.house_right_side.attachNewNode(CollisionNode("house_right_side"))
        colHRS.node().addSolid(CollisionBox(Point3(-5, -4, -1), Point3(5, 0, 1)))
        # colHRS.show()
        
        self.house_left_side = loader.loadModel("../models/house-side")
        self.house_left_side.setScale(8)
        self.house_left_side.setPos(-14, 0, 8)
        self.house_left_side.setHpr(-90, 0, 0)
        self.house_left_side.reparentTo(render)
        
        colHLS = self.house_left_side.attachNewNode(CollisionNode("house_left_side"))
        colHLS.node().addSolid(CollisionBox(Point3(-5, -4, -1), Point3(5, 0, 1)))
        # colHLS.show()
        
    def addActor(self):
        """
        self.panda = Actor("panda", {"walk": "panda-walk"})
        self.panda.setPos(0, 0, 0)
        self.panda.reparentTo(render)
        """
        
        self.robot = loader.loadModel("../models/robot")
        self.robot.setPos(0, 0, 1)
        # self.robot.setScale(5)
        self.robot.reparentTo(render)
        
        colRobot = self.robot.attachNewNode(CollisionNode("robot"))
        colRobot.node().addSolid(CollisionSphere(0, 0, 0, 1.9))
        # colRobot.show()
        
        colRobotRay = self.robot.attachNewNode(CollisionNode("robotray"))
        colRobotRay.node().addSolid(CollisionSegment(0, -3, 0.3, 0, -10, 0.3))
        colRobotRay.show()

        base.cTrav.addCollider(colRobotRay, self.notifier)
        
        base.cTrav.addCollider(colRobot, self.pusher)
        
        self.pusher.addCollider(colRobot, self.robot, base.drive.node())
        
    def addObstacles(self):
        self.crate = loader.loadModel("../models/crate")
        self.crate.setPos(0, -15, 1.1)
        self.crate.setScale(4)
        self.crate.reparentTo(render)
        
        colCrate = self.crate.attachNewNode(CollisionNode("crate"))
        colCrate.node().addSolid(CollisionBox(Point3(-0.6, -0.6, -0.6), Point3(0.6, 0.6, 0.6)))
        # colCrate.show()
        
        self.tri = loader.loadModel("../models/tri")
        self.tri.setPos(-10, 15, 0.8)
        # self.tri.setScale(3)
        self.tri.reparentTo(render)
        
        colTri = self.tri.attachNewNode(CollisionNode("tri"))
        colTri.node().addSolid(CollisionBox(Point3(-0.6, -0.6, -0.6), Point3(0.6, 0.6, 0.6)))
        # colTri.show()
        
    def addCam(self):
        self.cam.setPos(0, -20, 6)

        self.followCam = FollowCam(self.cam, self.robot)
        
        col = self.cam.attachNewNode(CollisionNode("cam"))
        col.node().addSolid(CollisionSphere(0, 0, 0, 8))
        # col.show()
        
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
        # self.panda.setPlayRate(1.0, "walk")
        # self.panda.loop("walk")
        self.pandaWalk = True
    
    def endWalk(self):
        # self.panda.stop()
        self.pandaWalk = False
    
    def beginReverse(self):
        # self.panda.setPlayRate(-1.0, "walk")
        # self.panda.loop("walk")
        self.pandaReverse = True
        
    def endReverse(self):
        # self.panda.stop()
        self.pandaReverse = False
        
    def beginTurnLeft(self):
        self.pandaLeft = True
        
    def endTurnLeft(self):
        self.pandaLeft = False
        
    def beginTurnRight(self):
        self.pandaRight = True
        
    def endTurnRight(self):
        self.pandaRight = False

    def getActorPoint(self):
        print("x: "+str(self.robot.getX())+" y: "+str(self.robot.getY())+" z: "+str(self.robot.getZ()))

    def updatePanda(self, task):
        if base.mouseWatcherNode.hasMouse():
            self.robot.setH(self.robot, -base.mouseWatcherNode.getMouseX() * 10)
        self.resetMouse()
        
        if self.pandaWalk:
            self.robot.setY(self.robot, -0.2)
        elif self.pandaReverse:
            self.robot.setY(self.robot, 0.2)
            
        if self.pandaLeft:
            self.robot.setH(self.robot, 0.8)
        elif self.pandaRight:
            self.robot.setH(self.robot, -0.8)
            
        return task.cont

    def onRayCollision(self, entry):
        point = entry.getSurfacePoint(render)
        x = int(point.get_x() + 15)
        y = int(point.get_y() + 29)

        print "x: "+str(x)+", y: "+str(y)
        
        matrix[x][y] = 0
        self.map.destroy()
        self.drawChart()

    def drawChart(self):
        im = Image.new("RGB", (310, 590), (127, 127, 127))
        draw = ImageDraw.Draw(im)

        for x in range(lineNum):
            for y in range(columnNum):
                color = matrix[x][y]
                draw.rectangle([(10*x, 10*y), (10*x+10, 10*y+10)], fill=(color, color, color))

        im.save(os.getcwd()+"/textures/map.png")

        self.map = OnscreenImage("../textures/map.png",
                scale = Vec3(1, 0.5, 0.5),
                pos = Vec3(-1, 8, 1),
                parent = self.cam
            )
