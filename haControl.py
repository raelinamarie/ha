restIgnore = []

import time
from ha.HAClasses import *
from ha.restInterface import *
from ha.restServer import *
from ha.restProxy import *
from ha.timeInterface import *
from haWeb import *

stateChangeEvent = threading.Event()
resourceLock = threading.Lock()

if __name__ == "__main__":
    # resources
    try:
        with open(rootDir+"aliases") as aliasFile:
            aliases = json.load(aliasFile)
    except:
        aliases = {}
    resources = HACollection("resources", aliases=aliases)

    # time resources
    timeInterface = TimeInterface("time")
    resources.addRes(HASensor("theDayOfWeek", timeInterface, "%A", type="date", group="Time", label="Day of week"))
    resources.addRes(HASensor("theDate", timeInterface, "%B %d %Y", type="date", group="Time", label="Date"))
    resources.addRes(HASensor("theTimeAmPm", timeInterface, "%I:%M %p", type="time", group="Time", label="Time"))
    resources.addRes(HASensor("sunrise", timeInterface, "sunrise", type="time", group="Time", label="Sunrise"))
    resources.addRes(HASensor("sunset", timeInterface, "sunset", type="time", group="Time", label="Sunset"))
    resources.addRes(HASensor("theDay", timeInterface, "%a %b %d %Y", type="date", label="Day"))
    resources.addRes(HASensor("theTime", timeInterface, "%I:%M", type="time", label="Time"))
    resources.addRes(HASensor("theAmPm", timeInterface, "%p", type="ampm", label="AmPm"))

    # start the cache to listen for services on other servers
    restIgnore.append(socket.gethostname()+":"+str(webRestPort))
    restCache = RestProxy("restProxy", resources, restIgnore, stateChangeEvent, resourceLock)
    restCache.start()
    
    # scenes and groups
    resources.addRes(SensorGroup("houseDoors", ["frontDoor", "familyRoomDoor", "masterBedroomDoor"], resources=resources, type="door", group="Doors", label="House doors"))
    resources.addRes(SensorGroup("garageDoors", ["garageDoor", "garageBackDoor", "garageHouseDoor"], resources=resources, type="door", group="Doors", label="Garage doors"))
    resources.addRes(HAScene("porchLights", ["frontLights",
                                               "backLights",
                                               "garageBackDoorLight"],
                                               resources=resources, 
                                               group="Lights", label="Porch lights"))
    resources.addRes(HAScene("xmasLights", ["xmasTree",
                                            "xmasCowTree",
                                            "xmasFrontLights",
                                            "xmasBackLights"],
                                               resources=resources, 
                                               group="Lights", label="Xmas lights"))
    resources.addRes(HAScene("outsideLights", ["porchLights",
                                               "bbqLights",
                                               "backYardLights",
                                               "deckLights",
                                               "trashLights",
                                               "xmasFrontLights",
                                               "xmasBackLights"],
                                               resources=resources, 
                                               group="Lights", label="Outside lights"))
    resources.addRes(HAScene("bedroomLights", ["bedroomLight", 
                                               "bathroomLight"],
                                               resources=resources, 
                                               stateList=[[0, 100, 0], [0, 100, 10]], 
                                               type="nightLight", group="Lights", label="Night lights"))

    # Tasks
    resources.addRes(HATask("bedroomLightsOnSunset", HASchedTime(event="sunset"), "bedroomLights", 1, resources=resources))
    resources.addRes(HATask("bedroomLightsOffSunrise", HASchedTime(event="sunrise"), "bedroomLights", 0, resources=resources))
    resources.addRes(HATask("porchLightsOnSunset", HASchedTime(event="sunset"), "porchLights", 1, resources=resources))
    resources.addRes(HATask("outsideLightsOffMidnight", HASchedTime(hour=[23,0], minute=[00]), "outsideLights", 0, resources=resources))
    resources.addRes(HATask("outsideLightsOffSunrise", HASchedTime(event="sunrise"), "outsideLights", 0, resources=resources))
    resources.addRes(HATask("xmasLightsOnSunset", HASchedTime(event="sunset"), "xmasLights", 1, resources=resources))
    resources.addRes(HATask("xmasLightsOffMidnight", HASchedTime(hour=[23,0], minute=[00]), "xmasLights", 0, resources=resources))
    resources.addRes(HATask("xmasLightsOffSunrise", HASchedTime(event="sunrise"), "xmasLights", 0, resources=resources))
    resources.addRes(HATask("hotWaterRecircOn", HASchedTime(hour=[05], minute=[0]), "recircPump", 1, resources=resources))
    resources.addRes(HATask("hotWaterRecircOff", HASchedTime(hour=[23], minute=[0]), "recircPump", 0, resources=resources))
    
    # Schedule
    schedule = HASchedule("schedule")
    schedule.addTask(resources["bedroomLightsOnSunset"])
    schedule.addTask(resources["bedroomLightsOffSunrise"])
    schedule.addTask(resources["porchLightsOnSunset"])
    schedule.addTask(resources["outsideLightsOffMidnight"])
    schedule.addTask(resources["outsideLightsOffSunrise"])
    schedule.addTask(resources["xmasLightsOnSunset"])
    schedule.addTask(resources["xmasLightsOffMidnight"])
    schedule.addTask(resources["xmasLightsOffSunrise"])
    schedule.addTask(resources["hotWaterRecircOn"])
    schedule.addTask(resources["hotWaterRecircOff"])
    schedule.start()

    # set up the web server
    webInit(resources, restCache, stateChangeEvent, resourceLock)
    
    # start the REST server for this service
    restServer = RestServer(resources, port=webRestPort, event=stateChangeEvent)
    # restServer.start()
    while True:
        time.sleep(1)

