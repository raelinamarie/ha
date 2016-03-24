webPort = 80
webRestPort = 7478
webUpdateInterval = 1
webPageTitle = "Home Automation"

insideTemp = "kitchenTemp"
outsideTemp = "deckTemp"
poolTemp = "waterTemp"

import cherrypy
import json
from jinja2 import Environment, FileSystemLoader
from ha.HAClasses import *
from haWebViews import *

solarDevices = {"inverters": {
"7F104A16": (868, 310),
"7F104920": (868, 380),
},
"optimizers": {
"1016AB88": (824, 514),
"100F7333": (343, 186),
"100F7195": (211, 444),
"100E3520": (420, 443),
"100F7255": (662, 520),
"100F7118": (474, 366),
"100F714E": (127, 444),
"100F74D9": (516, 366),
"1016B2BB": (824, 437),
"100E3313": (390, 366),
"100E3325": (558, 290),
"100F7220": (301, 109),
"100F71F9": (600, 366),
"100F7237": (642, 366),
"100F7408": (744, 443),
"100F72C1": (301, 186),
"100F7401": (301, 263),
"100F74DB": (385, 109),
"100F74C6": (474, 290),
"100F746B": (343, 109),
"100F74A0": (127, 367),
"100F755D": (620, 443),
"100E34EC": (662, 443),
"100F719B": (558, 366),
"100F721E": (336, 443),
"100F707C": (432, 366),
"100F71E5": (578, 520),
"100E3326": (378, 443),
"100F743D": (516, 290),
"100F7335": (385, 186),
"100E32F9": (169, 444),
"100F6FC5": (294, 443),
"100F747C": (704, 443),
"100F74B7": (578, 443),
}}

class WebRoot(object):
    def __init__(self, resources, env, cache, stateChangeEvent, resourceLock):
        self.resources = resources
        self.env = env
        self.cache = cache
        self.stateChangeEvent = stateChangeEvent
        self.resourceLock = resourceLock
    
    # Everything    
    @cherrypy.expose
    def index(self, group=None):
        debug('debugWeb', "/", "get", group)
        try:
            groups = [group.capitalize()]
            details = False
        except:
            groups = ["Time", "Temperature", "Hvac", "Services", "Pool", "Lights", "Doors", "Water", "Solar", "Power", "Cameras", "Tasks"]
            details = True
        with self.resourceLock:
            reply = self.env.get_template("default.html").render(title=webPageTitle, script="", 
                                groups=[[group, self.resources.getGroup(group)] for group in groups],
                                views=views,
                                details=details)
        return reply

    # Solar   
    @cherrypy.expose
    def solar(self, action=None, resource=None):
        debug('debugWeb', "/solar", "get", action, resource)
        with self.resourceLock:
            inverters = self.resources.getGroup("Inverters")
#            for inverter in inverters:
#                inverter.location = solarDevices["inverters"][inverter.name]
            optimizers = self.resources.getGroup("Optimizers")
#            for optimizer in optimizers:
#                optimizer.location = solarDevices["optimizers"][optimizer.name]
            latitude = str(abs(latLong[0]))+(" N" if latLong[0]>0 else " S")
            longitude = str(abs(latLong[1]))+(" E" if latLong[1]>0 else " W")
            reply = self.env.get_template("solar.html").render(script="",
                                dayOfWeek=self.resources["theDayOfWeek"],
                                date=self.resources["theDate"],
                                time=self.resources["theTime"],
                                ampm=self.resources["theAmPm"],
                                sunrise=self.resources["sunrise"],
                                sunset=self.resources["sunset"],
                                latitude=latitude, longitude=longitude,
                                airTemp=self.resources[outsideTemp],
                                inverterTemp=self.resources["inverterTemp"], 
                                roofTemp=self.resources["roofTemp"], 
                                currentPower=self.resources["currentPower"], 
                                todaysEnergy=self.resources["todaysEnergy"], 
                                lifetimeEnergy=self.resources["lifetimeEnergy"], 
                                inverters=inverters, 
                                optimizers=optimizers, 
                                views=views)
        return reply

    # iPad - 1024x768   
    @cherrypy.expose
    def ipad(self, action=None, resource=None):
        debug('debugWeb', "/ipad", "get", action, resource)
        with self.resourceLock:
            reply = self.env.get_template("ipad.html").render(script="", 
                                time=self.resources["theTime"],
                                ampm=self.resources["theAmPm"],
                                day=self.resources["theDay"],
                                pooltemp=self.resources[poolTemp],
                                intemp=self.resources[insideTemp],
                                outtemp=self.resources[outsideTemp],
                                groups=[["Pool", self.resources.getResList(["spaTemp"])], 
                                      ["Lights", self.resources.getResList(["xmasTree", "xmasCowTree", "porchLights", "xmasLights", "bbqLights", "backYardLights", "poolLight", "spaLight"])], 
                                      ["Shades", self.resources.getResList(["allShades", "shade1", "shade2", "shade3", "shade4"])], 
                                      ["Hvac", self.resources.getResList(["southHeatTempTarget", "northHeatTempTarget"])], 
                                      ["Sprinklers", self.resources.getResList(["backLawnSequence", "gardenSequence", "sideBedSequence", "frontLawnSequence"])]
                                      ],
                                views=views)
        return reply

    # iPhone 5 - 320x568    
    @cherrypy.expose
    def iphone5(self, action=None, resource=None):
        debug('debugWeb', "/iphone5", "get", action, resource)
        with self.resourceLock:
            reply = self.env.get_template("iphone5.html").render(script="", 
                                time=self.resources["theTime"],
                                ampm=self.resources["theAmPm"],
                                temp=self.resources[outsideTemp],
                                resources=self.resources.getResList(["spaTemp", "xmasTree", "xmasCowTree", "porchLights", "xmasLights", "allShades", "shade1", "shade2", "shade3", "shade4", "backLawn", "backBeds", "garden", "sideBeds", "frontLawn"]),
                                views=views)
        return reply

    # iPhone 3GS - 320x480    
    @cherrypy.expose
    def iphone3gs(self, action=None, resource=None):
        debug('debugWeb', "/iphone3gs", "get", action, resource)
        with self.resourceLock:
            reply = self.env.get_template("iphone3gs.html").render(script="", 
                                time=self.resources["theTime"],
                                ampm=self.resources["theAmPm"],
                                day=self.resources["theDay"],
                                temp=self.resources[outsideTemp],
                                resources=self.resources.getResList(["porchLights", "xmasLights", "bedroomLights", "recircPump", "garageDoors", "houseDoors"]),
                                views=views)
        return reply

    # get or set a resource state
    @cherrypy.expose
    def cmd(self, resource=None, state=None):
        debug('debugWeb', "/cmd", "get", resource, state)
        try:
            if resource == "resources":
                reply = ""
                for resource in self.resources.keys():
                    if resource != "states":
                        reply += resource+"\n"
                return reply
            else:
                if state:
                    self.resources[resource].setViewState(state, views)
                    time.sleep(1)   # hack
                return json.dumps({"state": self.resources[resource].getViewState(views)})
        except:
            return "Error"        

    # Return the value of a resource attribute
    @cherrypy.expose
    def value(self, resource=None, attr=None):
        try:
            if resource:
                if attr:
                    return self.resources[resource].__getattribute__(attr).__str__()
                else:
                    return self.resources[resource].dict().__str__()
        except:
            return "Error"        

    # Update the states of all resources
    @cherrypy.expose
    def state(self, _=None):
        debug('debugWebUpdate', "state", cherrypy.request.remote.ip)
        return self.updateStates(self.resources["states"].getState())
        
    # Update the states of resources that have changed
    @cherrypy.expose
    def stateChange(self, _=None):
        debug('debugWebUpdate', "stateChange", cherrypy.request.remote.ip)
        debug('debugInterrupt', "update", "event wait")
        self.stateChangeEvent.wait()
        debug('debugInterrupt', "update", "event clear")
        self.stateChangeEvent.clear()
        return self.updateStates(self.resources["states"].getStateChange())

    # return the json to update the states of the specified collection of sensors
    def updateStates(self, resourceStates):
        staticTypes = ["time", "ampm", "date", "W", "KW"]          # types whose class does not depend on their value
        tempTypes = ["tempF", "tempFControl", "tempC", "spaTemp"]       # temperatures
        updates = {"cacheTime": self.cache.cacheTime}
        for resource in resourceStates.keys():
            try:
                resState = self.resources[resource].getViewState(views)
                resClass = self.resources[resource].type
                if resClass in tempTypes:
                    updates[resource] = ("temp", resState, tempColor(resState))
                else:
                    if resClass not in staticTypes:
                        resClass += "_"+resState
                    updates[resource] = (resClass, resState, "")
            except:
                pass
        debug('debugWebUpdate', "states", len(updates))
        return json.dumps(updates)
        
    # Submit    
    @cherrypy.expose
    def submit(self, action=None, resource=None):
        debug('debugWeb', "/submit", "post", action, resource)
        self.resources[resource].setViewState(action, views)
        reply = ""
        return reply

def webInit(resources, restCache, stateChangeEvent, resourceLock):
    # set up the web server
    baseDir = os.path.abspath(os.path.dirname(__file__))
    globalConfig = {
        'server.socket_port': webPort,
        'server.socket_host': "0.0.0.0",
        }
    appConfig = {
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.root': os.path.join(baseDir, "static"),
            'tools.staticdir.dir': "css",
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.root': os.path.join(baseDir, "static"),
            'tools.staticdir.dir': "js",
        },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.root': os.path.join(baseDir, "static"),
            'tools.staticdir.dir': "images",
        },
        '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(baseDir, "static/favicon.ico"),
        },
    }    
    cherrypy.config.update(globalConfig)
    root = WebRoot(resources, Environment(loader=FileSystemLoader(os.path.join(baseDir, 'templates'))), restCache, stateChangeEvent, resourceLock)
    cherrypy.tree.mount(root, "/", appConfig)
    if not webLogging:
        access_log = cherrypy.log.access_log
        for handler in tuple(access_log.handlers):
            access_log.removeHandler(handler)
    cherrypy.engine.timeout_monitor.unsubscribe()
    cherrypy.engine.autoreload.unsubscribe()
    cherrypy.engine.start()

