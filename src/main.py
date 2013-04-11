# -*- coding: UTF-8 -*-
'''
    @author: zerokol
'''
from Application import Application
from pandac.PandaModules import WindowProperties

if __name__ == "__main__":
    gameApp = Application()
    
    props = WindowProperties( )
    props.setTitle('Robot Simul')
    base.win.requestProperties(props)
    
    gameApp.run()