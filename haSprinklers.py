from ha.HAClasses import *
from ha.GPIOInterface import *
from ha.I2CInterface import *
from ha.TC74Interface import *
from ha.MCP9803Interface import *
from ha.tempInterface import *
from ha.restServer import *

if __name__ == "__main__":
    # Resources
    resources = HACollection("resources")
    schedule = HASchedule("schedule")

    # Interfaces
    stateChangeEvent = threading.Event()
    i2c1 = I2CInterface("I2C1", bus=1, event=stateChangeEvent)
    gpioInterface = GPIOInterface("GPIO", i2c1)
    tc74 = TC74Interface("TC74", i2c1)
    mcp9803 = MCP9803Interface("MCP9803", i2c1)
    tc74Temp = TempInterface("tc74Temp", tc74)
    mcp9803Temp = TempInterface("mcp9803Temp", mcp9803)
    
    # Doors
#    resources.addRes(HASensor("frontDoor", gpioInterface, 2, type="door", group="Doors", label="Front"))
#    resources.addRes(HASensor("familyRoomDoor", gpioInterface, 1, type="door", group="Doors", label="Family room"))
#    resources.addRes(HASensor("masterBedDoor", gpioInterface, 0, type="door", group="Doors", label="Master bedroom"))
#    resources.addRes(HASensor("garageBackDoor", gpioInterface, 3, type="door", group="Doors", label="Garage back"))
#    resources.addRes(HADoorSensor("Garage door", gpioInterface, 5, type="door", group="Doors"))
#    resources.addRes(HADoorSensor("Garage door house", gpioInterface, 4, type="door", group="Doors"))

    # Sprinklers
    resources.addRes(HAControl("frontLawn", gpioInterface, 3, group="Water", label="Front lawn")) # yellow
    resources.addRes(HAControl("garden", gpioInterface, 4, group="Water", label="Garden")) # red
    resources.addRes(HAControl("backLawn", gpioInterface, 2, group="Water", label="Back lawn")) # green
    resources.addRes(HAControl("backBeds", gpioInterface, 1, group="Water", label="Back beds")) # blue
    resources.addRes(HAControl("sideBeds", gpioInterface, 0, group="Water", label="Side beds")) # red

    # Sequences
    resources.addRes(HASequence("frontLawnSequence", [HACycle(resources["frontLawn"], 900)], group="Water", label="Front lawn 15 min"))
    resources.addRes(HASequence("gardenSequence", [HACycle(resources["garden"], 300)], group="Water", label="Garden 5 min"))
    resources.addRes(HASequence("backLawnSequence", [HACycle(resources["backLawn"], 900)], group="Water", label="Back lawn 15 min"))
    resources.addRes(HASequence("sideBedSequence", [HACycle(resources["sideBeds"], 600)], group="Water", label="Side beds 10 min"))
    resources.addRes(HASequence("backBedSequence", [HACycle(resources["backBeds"], 600)], group="Water", label="Back beds 10 min"))

    # Schedules
    resources.addRes(schedule)
    schedule.addTask(HATask("frontLawnTask", HASchedTime(hour=[21], minute=[00], weekday=[Mon, Wed, Fri], month=[May, Jun, Jul, Aug, Sep, Oct]), resources["frontLawnSequence"], 1, enabled=True))
    schedule.addTask(HATask("gardenTask", HASchedTime(hour=[21], minute=[15], month=[May, Jun, Jul, Aug, Sep, Oct]), resources["gardenSequence"], 1, enabled=True))
    schedule.addTask(HATask("backLawnTask", HASchedTime(hour=[21], minute=[20], weekday=[Mon, Wed, Fri], month=[May, Jun, Jul, Aug, Sep, Oct]), resources["backLawnSequence"], 1, enabled=True))
    schedule.addTask(HATask("sideBedTask", HASchedTime(hour=[21], minute=[35], weekday=[Fri], month=[May, Jun, Jul, Aug, Sep, Oct]), resources["sideBedSequence"], 1, enabled=True))
    schedule.addTask(HATask("backBedTask", HASchedTime(hour=[21], minute=[45], weekday=[Fri], month=[May, Jun, Jul, Aug, Sep, Oct]), resources["backBedSequence"], 1, enabled=True))

    # Temperature
#    resources.addRes(HASensor("bedroomTemp", mcp9803Temp, 0x48, group="Temperature", label="Bedroom temp", type="tempF"))
#    resources.addRes(HASensor("kitchenTemp", tc74Temp, 0x4e, group="Temperature", label="Kitchen temp", type="tempF"))
#    resources.addRes(HASensor("atticTemp", tc74Temp, 0x4f, group="Temperature", label="Attic temp", type="tempF"))
    
    # Start interfaces
    gpioInterface.start()
    tc74Temp.start()
    mcp9803Temp.start()
    schedule.start()
    restServer = RestServer(resources, event=stateChangeEvent, label="Sprinklers")
    restServer.start()

