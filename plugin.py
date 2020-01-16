#           VictronGX modbus over TCP/IP Python Plugin for Domoticz
#

# Below is what will be displayed in Domoticz GUI under HW
#
"""
<plugin key="VictronGXModBus" name="VictronGX Modbus over TCP/IP" author="pawcio" version="1.0.0" wikilink="no" >
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="192.168.1.73"/>
        <param field="Port" label="Port" width="40px" required="true" default="502"/>
        <param field="Mode3" label="GX Device Unit-id" width="250px" default="100"/> 
        <param field="Mode4" label="Multiplus Device Unit-id" width="250px" default="228"/> 
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="False" />
            </options>
        </param>
    </params>
</plugin>
"""
#
# Main Import
import Domoticz

class BasePlugin:

    conn = None
    config = None
    id = 0
    #228 - multiplus, 100 - gx
    registers = [] 
    idx = 0;

    # Domoticz call back functions
    #
            
    # Executed once at HW creation/ update. Can create up to 255 devices.
    def onStart(self):
        self.registers = [ int(Parameters["Mode4"]).to_bytes(1, byteorder='big') + b'\x03\x00\x03\x00\x3d', 
            int(Parameters["Mode3"]).to_bytes(1, byteorder='big') + b'\x03\x03\x26\x00\x15', 
            int(Parameters["Mode3"]).to_bytes(1, byteorder='big') + b'\x03\x03\x48\x00\x06'] 
            
        Domoticz.Log(str(self.registers))
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()

        # Do not change below UNIT constants!

        self.UNIT_ACINVL1 = 1
        self.UNIT_ACINAL1 = 2
        self.UNIT_ACINWL1 = 3
        self.UNIT_ACOUTVL1 = 4
        self.UNIT_ACOUTAL1 = 5
        self.UNIT_ACOUTWL1 = 6
        self.UNIT_BATTV = 7
        self.UNIT_BATTA = 8
        self.UNIT_BATTSOC = 9
        self.UNIT_BATTSTATE = 10
        self.UNIT_BATTTEMP = 11
        self.UNIT_BATTW = 12

        if (len(Devices) == 0):
            
            Domoticz.Device(Name="acInVL1", Unit=self.UNIT_ACINVL1, TypeName="Voltage").Create()
            Domoticz.Device(Name="acInAL1", Unit=self.UNIT_ACINAL1, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="acInWL1", Unit=self.UNIT_ACINWL1, Type=248, Subtype=1).Create()
            Domoticz.Device(Name="acOutVL1", Unit=self.UNIT_ACOUTVL1, TypeName="Voltage").Create()
            Domoticz.Device(Name="acOutAL1", Unit=self.UNIT_ACOUTAL1, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="acOutWL1", Unit=self.UNIT_ACOUTWL1, Type=248, Subtype=1).Create()
            Domoticz.Device(Name="battV", Unit=self.UNIT_BATTV, TypeName="Voltage").Create()
            Domoticz.Device(Name="battA", Unit=self.UNIT_BATTA, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="battSOC", Unit=self.UNIT_BATTSOC, TypeName="Percentage").Create()
            Domoticz.Device(Name="battState", Unit=self.UNIT_BATTSTATE, TypeName="Alert").Create()
            Domoticz.Device(Name="battTemp", Unit=self.UNIT_BATTTEMP, TypeName="Temperature").Create()
            Domoticz.Device(Name="battW", Unit=self.UNIT_BATTW, Type=248, Subtype=1).Create()
 
            Domoticz.Log("Devices created.")
        else:
            #self.acInVL1 = Devices[self.UNIT_ACINVL1].sValue 
            pass

        Domoticz.Heartbeat(60)

        self.config = {
            "description": "Domoticz",
            "host": Parameters["Address"],
            "port": Parameters["Port"],
        }

        Domoticz.Log("VictronGX onStart: " + Parameters["Address"] + ":" + Parameters["Port"])

        return True
            
    def onConnect(self, Connection, Status, Description):
        success = False

        if (Connection == self.conn):
            if (Status == 0):
                if Parameters["Mode6"] == "Debug":
                    Domoticz.Log("VictronGX plugin -> Connected successfully to: "+Connection.Address)
                success = True
                #todo if needed...

        if False == success:
            Domoticz.Log("VictronGX plugin -> Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+" with error: "+Description)
            self.conn = None
            self.SyncDevices(1)

    def sendPriv(self):
            #registry 800 - 866, unit id - 246
            #0x00 0x00 - fixed for the tcp modbus (protocol identifier)
            #0x00 0x06 - remaining bytes
            
            #0xf6 - unit identifier
            #0x03 - command code
            #0x0320 - first register address (big endian)
            #0x0042 - number of registers requested
            b = b'\x00\x00\x00\x06'
            self.conn.Send(self.id.to_bytes(2, byteorder='big') + b + self.registers[self.idx]) 
            self.id += 1 # transaction id  
            self.idx += 1

    def refreshData(self):
        
        if self.conn:
            self.idx = 0
            self.sendPriv()

        else:
            if self.conn == None:
                self.handleConnect()
        
    def onHeartbeat(self):
        #Domoticz.Log("onHeartbeat called")

        #Disabled temporary
        self.refreshData()

        return True

    def onMessage(self, Connection, Data):
        
        #Domoticz.Log("onMessage called: " + str(Data) + " , Connection: " + str(Connection) + " , idx: " + str(self.idx))
            
        if 1 == self.idx:
        
            self.acInVL1 = int.from_bytes(Data[9:11], byteorder='big', signed=False) / 10
            self.acInAL1 = int.from_bytes(Data[15:17], byteorder='big', signed=True) / 10
            self.acInFL1 = int.from_bytes(Data[21:23], byteorder='big', signed=True) / 100
            self.acInWL1 = int.from_bytes(Data[27:29], byteorder='big', signed=True) * 10
            
            self.acOutVL1 = int.from_bytes(Data[33:35], byteorder='big', signed=False) / 10
            self.acOutAL1 = int.from_bytes(Data[39:41], byteorder='big', signed=True) / 10
            self.acOutFL1 = int.from_bytes(Data[45:47], byteorder='big', signed=True) / 100
            self.acOutWL1 = int.from_bytes(Data[49:51], byteorder='big', signed=True) * 10
            
            self.battV = int.from_bytes(Data[55:57], byteorder='big', signed=False) / 100
            self.battA = int.from_bytes(Data[57:59], byteorder='big', signed=True) / 10
            self.battSOC = int.from_bytes(Data[63:65], byteorder='big', signed=False) / 10
            self.battState = int.from_bytes(Data[65:67], byteorder='big', signed=False)
            self.battTemp = int.from_bytes(Data[125:127], byteorder='big', signed=True) / 10
            
            if Parameters["Mode6"] == "Debug":
                Domoticz.Log("acInVL1: " + str(self.acInVL1))
                Domoticz.Log("acInAL1: " + str(self.acInAL1))
                Domoticz.Log("acInFL1: " + str(self.acInFL1))
                Domoticz.Log("acInWL1: " + str(self.acInWL1))
                Domoticz.Log("acOutVL1: " + str(self.acOutVL1))
                Domoticz.Log("acOutAL1: " + str(self.acOutAL1))
                Domoticz.Log("acOutFL1: " + str(self.acOutFL1))
                Domoticz.Log("acOutWL1: " + str(self.acOutWL1))
                Domoticz.Log("battV: " + str(self.battV))
                Domoticz.Log("battA: " + str(self.battA))
                Domoticz.Log("battSOC: " + str(self.battSOC))
                Domoticz.Log("battState: " + str(self.battState))
                Domoticz.Log("battTemp: " + str(self.battTemp))
            
        elif 2 == self.idx:
            self.acConsumptionWL1 = int.from_bytes(Data[31:33], byteorder='big', signed=False) / 1
            self.gridWL1 = int.from_bytes(Data[37:39], byteorder='big', signed=True) / 1

            if Parameters["Mode6"] == "Debug":            
                Domoticz.Log("acConsumptionWL1: " + str(self.acConsumptionWL1))            
                Domoticz.Log("gridWL1: " + str(self.gridWL1))            
            
        elif 3 == self.idx:
            self.battW = int.from_bytes(Data[13:15], byteorder='big', signed=True) / 1
            self.battConsumedAh = int.from_bytes(Data[19:21], byteorder='big', signed=False) / -10
            self.battTimeToGo = int.from_bytes(Data[21:23], byteorder='big', signed=False) * 100
            
            if Parameters["Mode6"] == "Debug":
                Domoticz.Log("battW: " + str(self.battW))            
                Domoticz.Log("battConsumedAh: " + str(self.battConsumedAh))            
                Domoticz.Log("battTimeToGo: " + str(self.battTimeToGo))            

        if self.idx < len(self.registers):
            self.sendPriv()
        else:
            self.SyncDevices(0)

        return

    # def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
    #     Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
    #         Priority) + "," + Sound + "," + ImageFile)
    #     return

    def onDisconnect(self, Connection):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Log("Device has disconnected")
        self.conn = None
        return

    def onStop(self):
        Domoticz.Log("onStop called")
        return True

    def handleConnect(self):
        self.id = 0
        self.conn = Domoticz.Connection(Name="VictronGX", Transport="TCP/IP", Protocol="None", Address=self.config["host"], Port=self.config["port"])

        self.conn.Connect()

    def state(self, argument):
        switcher = {
            0: "Off",
            1: "Low Power",
            2: "Fault",
            3: "Bulk",
            4: "Absorption",
            5: "Float",
            6: "Storage",
            7: "Equalize",
            8: "Passthru",
            9: "Inverting",
            10: "Power assist",
            11: "Power supply",
            252: "Bulk protection"
        }
        
        return switcher.get(argument, "Invalid value")
       
    def SyncDevices(self, TimedOut):
    
        UpdateDevice(self.UNIT_ACINVL1, self.acInVL1, str(self.acInVL1), TimedOut)
        UpdateDevice(self.UNIT_ACINAL1, self.acInAL1, str(self.acInAL1), TimedOut)
        UpdateDevice(self.UNIT_ACINWL1, self.acInWL1, str(self.acInWL1), TimedOut)
        UpdateDevice(self.UNIT_ACOUTVL1, self.acOutVL1, str(self.acOutVL1), TimedOut)
        UpdateDevice(self.UNIT_ACOUTAL1, self.acOutAL1, str(self.acOutAL1), TimedOut)
        UpdateDevice(self.UNIT_ACOUTWL1, self.acOutWL1, str(self.acOutWL1), TimedOut)
        UpdateDevice(self.UNIT_BATTV, self.battV, str(self.battV), TimedOut)
        UpdateDevice(self.UNIT_BATTA, self.battA, str(self.battA), TimedOut)
        UpdateDevice(self.UNIT_BATTSOC, self.battSOC, str(self.battSOC), TimedOut)
        UpdateDevice(self.UNIT_BATTSTATE, self.battState, self.state(self.battState), TimedOut)
        UpdateDevice(self.UNIT_BATTTEMP, self.battTemp, str(self.battTemp), TimedOut)
        UpdateDevice(self.UNIT_BATTW, self.battW, str(self.battW), TimedOut)
        
        return

#    def onCommand(self, Unit, Command, Level, Hue):
#       Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
#       
#       if 99 == Level:
#           self.refreshData()

    def onDeviceModified(self, Unit):
        
        Device = Devices[Unit]
        Domoticz.Log("onDeviceModified called for Unit " + str(Unit) + " " + str(Device))
        if 99 == Device.nValue:
            #Domoticz.Log("Refresh data")
            self.refreshData()
            
            
            
################ base on example ######################
global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


#def onCommand(Unit, Command, Level, Hue):
#   global _plugin
#   _plugin.onCommand(Unit, Command, Level, Hue)

def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)

# def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
#     global _plugin
#     _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    #Domoticz.Debug("Settings count: " + str(len(Settings)))
    # for x in Settings:
    #     Domoticz.Debug("'" + x + "':'" + str(Settings[x]) + "'")
    Domoticz.Debug("Image count: " + str(len(Images)))
    for x in Images:
        Domoticz.Debug("'" + x + "':'" + str(Images[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device Image:     " + str(Devices[x].Image))
    return


def UpdateDevice(Unit, nValue, sValue, TimedOut):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=int(nValue), sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Log("Update " + str(nValue) + ":'" + str(sValue) + "' (" + Devices[Unit].Name + ")")
    return
    