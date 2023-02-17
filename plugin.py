#           VictronGX modbus over TCP/IP Python Plugin for Domoticz
#

# Below is what will be displayed in Domoticz GUI under HW
#
"""
<plugin key="VictronGXModBus" name="VictronGX Modbus over TCP/IP" author="pawcio" version="2.0.0" wikilink="no" >
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="192.168.1.73"/>
        <param field="Port" label="Port" width="40px" required="true" default="502"/>
        <param field="Mode3" label="GX Device Unit-id" width="250px" default="100"/> 
        <param field="Mode4" label="Multiplus Device Unit-id" width="250px" default="228"/> 
        <param field="Mode5" label="First Solar Charger Unit-id" width="250px" default=""/>  #229
        <param field="Mode1" label="Second Solar Charger Unit-id" width="250px" default=""/> #238
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
    #228 - multiplus, 100 - gx, 229 - solar charger
    registers = [] 
    idx = 0;
    
    firstSolarCharger = False
    secondSolarCharger = False
    
    power = "0;0"

    # Domoticz call back functions
    #
            
    # Executed once at HW creation/ update. Can create up to 255 devices.
    def onStart(self):
        self.firstSolarCharger = len(Parameters["Mode5"])!=0
        self.secondSolarCharger = len(Parameters["Mode1"])!=0
        
        self.registers = [ int(Parameters["Mode4"]).to_bytes(1, byteorder='big') + b'\x03\x00\x03\x00\x3d', 
            int(Parameters["Mode3"]).to_bytes(1, byteorder='big') + b'\x03\x03\x26\x00\x15', 
            int(Parameters["Mode3"]).to_bytes(1, byteorder='big') + b'\x03\x03\x48\x00\x06']
            
        if True == self.firstSolarCharger:
            self.registers.append(int(Parameters["Mode5"]).to_bytes(1, byteorder='big') + b'\x03\x03\x03\x00\x15')
            
        if True == self.secondSolarCharger:
            self.registers.append(int(Parameters["Mode1"]).to_bytes(1, byteorder='big') + b'\x03\x03\x03\x00\x15')

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
        if True == self.firstSolarCharger:
            self.UNIT_PVW = 13
            self.UNIT_PVALLPOW = 14
            self.UNIT_PVV = 15
            self.UNIT_PVA = 16
        if True == self.secondSolarCharger:
            self.UNIT_PVW_250 = 17
            self.UNIT_PVALLPOW_250 = 18
            self.UNIT_PVV_250 = 19
            self.UNIT_PVA_250 = 20
        self.UNIT_ACINVL2 = 21
        self.UNIT_ACINAL2 = 22
        self.UNIT_ACINWL2 = 23
        self.UNIT_ACOUTVL2 = 24
        self.UNIT_ACOUTAL2 = 25
        self.UNIT_ACOUTWL2 = 26
        self.UNIT_ACINVL3 = 27
        self.UNIT_ACINAL3 = 28
        self.UNIT_ACINWL3 = 29
        self.UNIT_ACOUTVL3 = 30
        self.UNIT_ACOUTAL3 = 31
        self.UNIT_ACOUTWL3 = 32        
        
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
            if True == self.firstSolarCharger:
                Domoticz.Device(Name="PVW", Unit=self.UNIT_PVW, Type=248, Subtype=1).Create()
                Domoticz.Device(Name="PVV", Unit=self.UNIT_PVV, TypeName="Voltage").Create()
                Domoticz.Device(Name="PVA", Unit=self.UNIT_PVA, Type=243, Subtype=23).Create()
            if True == self.secondSolarCharger:
                Domoticz.Device(Name="PVW_250", Unit=self.UNIT_PVW_250, Type=248, Subtype=1).Create()
                Domoticz.Device(Name="PVV_250", Unit=self.UNIT_PVV_250, TypeName="Voltage").Create()
                Domoticz.Device(Name="PVA_250", Unit=self.UNIT_PVA_250, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="acInVL2", Unit=self.UNIT_ACINVL2, TypeName="Voltage").Create()
            Domoticz.Device(Name="acInAL2", Unit=self.UNIT_ACINAL2, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="acInWL2", Unit=self.UNIT_ACINWL2, Type=248, Subtype=1).Create()
            Domoticz.Device(Name="acOutVL2", Unit=self.UNIT_ACOUTVL2, TypeName="Voltage").Create()
            Domoticz.Device(Name="acOutAL2", Unit=self.UNIT_ACOUTAL2, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="acOutWL2", Unit=self.UNIT_ACOUTWL2, Type=248, Subtype=1).Create()
            Domoticz.Device(Name="acInVL3", Unit=self.UNIT_ACINVL3, TypeName="Voltage").Create()
            Domoticz.Device(Name="acInAL3", Unit=self.UNIT_ACINAL3, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="acInWL3", Unit=self.UNIT_ACINWL3, Type=248, Subtype=1).Create()
            Domoticz.Device(Name="acOutVL3", Unit=self.UNIT_ACOUTVL3, TypeName="Voltage").Create()
            Domoticz.Device(Name="acOutAL3", Unit=self.UNIT_ACOUTAL3, Type=243, Subtype=23).Create()
            Domoticz.Device(Name="acOutWL3", Unit=self.UNIT_ACOUTWL3, Type=248, Subtype=1).Create()            
            
            Domoticz.Log("Devices created.")
        else:
            if True == self.firstSolarCharger:
                if not self.UNIT_PVW in Devices:
                    Domoticz.Device(Name="PVW", Unit=self.UNIT_PVW, Type=248, Subtype=1).Create()
                else:
                    self.solPVPower = Devices[self.UNIT_PVW].sValue

                if not self.UNIT_PVALLPOW in Devices:
                    Domoticz.Device(Name="PVPower", Unit=self.UNIT_PVALLPOW, TypeName="kWh").Create()
                else:
                    self.power = Devices[self.UNIT_PVALLPOW].sValue 

                if not self.UNIT_PVV in Devices:
                    Domoticz.Device(Name="PVV", Unit=self.UNIT_PVV, TypeName="Voltage").Create()
                else:
                    self.solPVV = Devices[self.UNIT_PVV].sValue
                    
                if not self.UNIT_PVA in Devices:
                    Domoticz.Device(Name="PVA", Unit=self.UNIT_PVA, Type=243, Subtype=23).Create()
                else:
                    self.solPVA = Devices[self.UNIT_PVA].sValue
                

            if True == self.secondSolarCharger:
                if not self.UNIT_PVW_250 in Devices:
                    Domoticz.Device(Name="PVW_250", Unit=self.UNIT_PVW_250, Type=248, Subtype=1).Create()
                else:
                    self.solPVPower_250 = Devices[self.UNIT_PVW_250].sValue

                if not self.UNIT_PVALLPOW_250 in Devices:
                    Domoticz.Device(Name="PVPower_250", Unit=self.UNIT_PVALLPOW_250, TypeName="kWh").Create()
                else:
                    self.power_250 = Devices[self.UNIT_PVALLPOW_250].sValue 

                if not self.UNIT_PVV_250 in Devices:
                    Domoticz.Device(Name="PVV_250", Unit=self.UNIT_PVV_250, TypeName="Voltage").Create()
                else:
                    self.solPVV_250 = Devices[self.UNIT_PVV_250].sValue
                    
                if not self.UNIT_PVA_250 in Devices:
                    Domoticz.Device(Name="PVA_250", Unit=self.UNIT_PVA_250, Type=243, Subtype=23).Create()
                else:
                    self.solPVA_250 = Devices[self.UNIT_PVA_250].sValue
                
                
            # L2  
            if not self.UNIT_ACINVL2 in Devices:
                Domoticz.Device(Name="acInVL2", Unit=self.UNIT_ACINVL2, TypeName="Voltage").Create()
            else:
                self.acInVL2 = Devices[self.UNIT_ACINVL2].sValue
                
            if not self.UNIT_ACINAL2 in Devices:
                Domoticz.Device(Name="acInAL2", Unit=self.UNIT_ACINAL2, Type=243, Subtype=23).Create()
            else:
                self.acInAL2 = Devices[self.UNIT_ACINAL2].sValue
            
            if not self.UNIT_ACINWL2 in Devices:            
                Domoticz.Device(Name="acInWL2", Unit=self.UNIT_ACINWL2, Type=248, Subtype=1).Create()
            else:
                self.acInWL2 = Devices[self.UNIT_ACINWL2].sValue
            
            if not self.UNIT_ACOUTVL2 in Devices:
                Domoticz.Device(Name="acOutVL2", Unit=self.UNIT_ACOUTVL2, TypeName="Voltage").Create()
            else:
                self.acOutVL2 = Devices[self.UNIT_ACOUTVL2].sValue
            
            if not self.UNIT_ACOUTAL2 in Devices:
                Domoticz.Device(Name="acOutAL2", Unit=self.UNIT_ACOUTAL2, Type=243, Subtype=23).Create()
            else:
                self.acOutAL2 = Devices[self.UNIT_ACOUTAL2].sValue

            if not self.UNIT_ACOUTWL2 in Devices:
                Domoticz.Device(Name="acOutWL2", Unit=self.UNIT_ACOUTWL2, Type=248, Subtype=1).Create()
            else:
                self.acOutWL2 = Devices[self.UNIT_ACOUTWL2].sValue                

            # L3
            if not self.UNIT_ACINVL3 in Devices:
                Domoticz.Device(Name="acInVL3", Unit=self.UNIT_ACINVL3, TypeName="Voltage").Create()
            else:
                self.acInVL3 = Devices[self.UNIT_ACINVL3].sValue
                
            if not self.UNIT_ACINAL3 in Devices:
                Domoticz.Device(Name="acInAL3", Unit=self.UNIT_ACINAL3, Type=243, Subtype=23).Create()
            else:
                self.acInAL3 = Devices[self.UNIT_ACINAL3].sValue
            
            if not self.UNIT_ACINWL3 in Devices:            
                Domoticz.Device(Name="acInWL3", Unit=self.UNIT_ACINWL3, Type=248, Subtype=1).Create()
            else:
                self.acInWL3 = Devices[self.UNIT_ACINWL3].sValue
            
            if not self.UNIT_ACOUTVL3 in Devices:
                Domoticz.Device(Name="acOutVL3", Unit=self.UNIT_ACOUTVL3, TypeName="Voltage").Create()
            else:
                self.acOutVL3 = Devices[self.UNIT_ACOUTVL3].sValue
            
            if not self.UNIT_ACOUTAL3 in Devices:
                Domoticz.Device(Name="acOutAL3", Unit=self.UNIT_ACOUTAL3, Type=243, Subtype=23).Create()
            else:
                self.acOutAL3 = Devices[self.UNIT_ACOUTAL3].sValue

            if not self.UNIT_ACOUTWL3 in Devices:
                Domoticz.Device(Name="acOutWL3", Unit=self.UNIT_ACOUTWL3, Type=248, Subtype=1).Create()
            else:
                self.acOutWL3 = Devices[self.UNIT_ACOUTWL3].sValue 

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
            
            #0xf6 - unit id
            #0x03 - command code
            #0x0320 - first register address (big endian)
            #0x0042 - number of registers requested
            b = b'\x00\x00\x00\x06'
            self.conn.Send(self.id.to_bytes(2, byteorder='big') + b + self.registers[self.idx]) 
            self.id += 1 # transaction id  
            if 65536 == self.id:
                self.id = 0
                
            self.idx += 1

    def refreshData(self):
        
        if self.conn:
            if 0 != self.idx:   #transaction in progress
                return
                
            self.idx = 0
            self.sendPriv()

        else:
            if self.conn == None:
                self.handleConnect()
        
    def onHeartbeat(self):
        #Domoticz.Log("onHeartbeat called")

        self.refreshData()

        return True

    def onMessage(self, Connection, Data):
        
        # Domoticz.Log("onMessage called: " + str(Data) + " , Connection: " + str(Connection) + " , idx: " + str(self.idx))
            
        if 1 == self.idx:
        
            self.acInVL1 = int.from_bytes(Data[9:11], byteorder='big', signed=False) / 10
            self.acInVL2 = int.from_bytes(Data[11:13], byteorder='big', signed=False) / 10
            self.acInVL3 = int.from_bytes(Data[13:15], byteorder='big', signed=False) / 10
            self.acInAL1 = int.from_bytes(Data[15:17], byteorder='big', signed=True) / 10
            self.acInAL2 = int.from_bytes(Data[17:19], byteorder='big', signed=True) / 10
            self.acInAL3 = int.from_bytes(Data[19:21], byteorder='big', signed=True) / 10
            self.acInFL1 = int.from_bytes(Data[21:23], byteorder='big', signed=True) / 100
            self.acInFL2 = int.from_bytes(Data[23:25], byteorder='big', signed=True) / 100
            self.acInFL3 = int.from_bytes(Data[25:27], byteorder='big', signed=True) / 100
            self.acInWL1 = int.from_bytes(Data[27:29], byteorder='big', signed=True) * 10
            self.acInWL2 = int.from_bytes(Data[29:31], byteorder='big', signed=True) * 10
            self.acInWL3 = int.from_bytes(Data[31:33], byteorder='big', signed=True) * 10
            
            self.acOutVL1 = int.from_bytes(Data[33:35], byteorder='big', signed=False) / 10
            self.acOutVL2 = int.from_bytes(Data[35:37], byteorder='big', signed=False) / 10
            self.acOutVL3 = int.from_bytes(Data[37:39], byteorder='big', signed=False) / 10
            self.acOutAL1 = int.from_bytes(Data[39:41], byteorder='big', signed=True) / 10
            self.acOutAL2 = int.from_bytes(Data[41:43], byteorder='big', signed=True) / 10
            self.acOutAL3 = int.from_bytes(Data[43:45], byteorder='big', signed=True) / 10
            self.acOutFL1 = int.from_bytes(Data[45:47], byteorder='big', signed=True) / 100 # there is only one freq register!
            self.acOutWL1 = int.from_bytes(Data[49:51], byteorder='big', signed=True) * 10
            self.acOutWL2 = int.from_bytes(Data[51:53], byteorder='big', signed=True) * 10
            self.acOutWL3 = int.from_bytes(Data[53:55], byteorder='big', signed=True) * 10
            
            # multiplus ii bat reading
            # self.battV = int.from_bytes(Data[55:57], byteorder='big', signed=False) / 100
            # self.battA = int.from_bytes(Data[57:59], byteorder='big', signed=True) / 10
            # self.battSOC = int.from_bytes(Data[63:65], byteorder='big', signed=False) / 10
            # self.battState = int.from_bytes(Data[65:67], byteorder='big', signed=False)
            self.battTemp = int.from_bytes(Data[125:127], byteorder='big', signed=True) / 10
            
            if Parameters["Mode6"] == "Debug":
                Domoticz.Log("acInVL1: " + str(self.acInVL1) + ", acInVL2: " + str(self.acInVL2) + ", acInVL3: " + str(self.acInVL3) + 
                        ", acInAL1: " + str(self.acInAL1) + ", acInAL2: " + str(self.acInAL2) + ", acInAL3: " + str(self.acInAL3) + 
                        ", acOutWL1: " + str(self.acOutWL1) + ", acOutWL2: " + str(self.acOutWL2) + ", acOutWL3: " + str(self.acOutWL3))
             
            if Parameters["Mode6"] == "Debug":
                Domoticz.Log("acInVL1: " + str(self.acInVL1))
                Domoticz.Log("acInVL2: " + str(self.acInVL2))
                Domoticz.Log("acInVL3: " + str(self.acInVL3))
                Domoticz.Log("acInAL1: " + str(self.acInAL1))
                Domoticz.Log("acInAL2: " + str(self.acInAL2))
                Domoticz.Log("acInAL3: " + str(self.acInAL3))
                Domoticz.Log("acInFL1: " + str(self.acInFL1))
                Domoticz.Log("acInFL2: " + str(self.acInFL2))
                Domoticz.Log("acInFL3: " + str(self.acInFL3))
                Domoticz.Log("acInWL1: " + str(self.acInWL1))
                Domoticz.Log("acInWL2: " + str(self.acInWL2))
                Domoticz.Log("acInWL3: " + str(self.acInWL3))
                Domoticz.Log("acOutVL1: " + str(self.acOutVL1))
                Domoticz.Log("acOutVL2: " + str(self.acOutVL2))
                Domoticz.Log("acOutVL3: " + str(self.acOutVL3))
                Domoticz.Log("acOutAL1: " + str(self.acOutAL1))
                Domoticz.Log("acOutAL2: " + str(self.acOutAL2))
                Domoticz.Log("acOutAL3: " + str(self.acOutAL3))
                Domoticz.Log("acOutFL1: " + str(self.acOutFL1))
                Domoticz.Log("acOutWL1: " + str(self.acOutWL1))
                Domoticz.Log("acOutWL2: " + str(self.acOutWL2))
                Domoticz.Log("acOutWL3: " + str(self.acOutWL3))
                Domoticz.Log("battV: " + str(self.battV))
                Domoticz.Log("battA: " + str(self.battA))
                Domoticz.Log("battSOC: " + str(self.battSOC))
                Domoticz.Log("battState: " + str(self.battState))
                Domoticz.Log("battTemp: " + str(self.battTemp))
            
        elif 2 == self.idx:
            self.acConsumptionWL1 = int.from_bytes(Data[31:33], byteorder='big', signed=False) / 1
            self.acConsumptionWL2 = int.from_bytes(Data[33:35], byteorder='big', signed=False) / 1
            self.acConsumptionWL3 = int.from_bytes(Data[35:37], byteorder='big', signed=False) / 1
            
            self.gridWL1 = int.from_bytes(Data[37:39], byteorder='big', signed=True) / 1
            self.gridWL2 = int.from_bytes(Data[39:41], byteorder='big', signed=True) / 1
            self.gridWL3 = int.from_bytes(Data[41:43], byteorder='big', signed=True) / 1

            if Parameters["Mode6"] == "Debug":            
                Domoticz.Log("acConsumptionWL1: " + str(self.acConsumptionWL1))            
                Domoticz.Log("acConsumptionWL2: " + str(self.acConsumptionWL2))            
                Domoticz.Log("acConsumptionWL3: " + str(self.acConsumptionWL3))            
                Domoticz.Log("gridWL1: " + str(self.gridWL1))            
                Domoticz.Log("gridWL2: " + str(self.gridWL2))            
                Domoticz.Log("gridWL3: " + str(self.gridWL3))            
            
        elif 3 == self.idx:
            # com.victornenergy.system
            self.battV = int.from_bytes(Data[9:11], byteorder='big', signed=False) / 10
            self.battA = int.from_bytes(Data[11:13], byteorder='big', signed=True) / 10
            self.battW = int.from_bytes(Data[13:15], byteorder='big', signed=True) / 1
            self.battSOC = int.from_bytes(Data[15:17], byteorder='big', signed=False) / 1
            self.battState = int.from_bytes(Data[17:19], byteorder='big', signed=False)
            self.battConsumedAh = int.from_bytes(Data[19:21], byteorder='big', signed=False) / -10
            self.battTimeToGo = int.from_bytes(Data[21:23], byteorder='big', signed=False) * 100
            
            if Parameters["Mode6"] == "Debug":
                Domoticz.Log("battW: " + str(self.battW))            
                Domoticz.Log("battConsumedAh: " + str(self.battConsumedAh))            
                Domoticz.Log("battTimeToGo: " + str(self.battTimeToGo))            

        elif 4 == self.idx:
            #Domoticz.Log("onMessage called for solar charger: " + str(Data))
            self.solBatV = int.from_bytes(Data[9:11], byteorder='big', signed=False) / 100
            self.solBatA = int.from_bytes(Data[11:13], byteorder='big', signed=True) / 10
            self.solBatTemp = int.from_bytes(Data[13:15], byteorder='big', signed=True) / 10
            self.solOnOff = int.from_bytes(Data[15:17], byteorder='big', signed=False)
            self.solState = int.from_bytes(Data[17:19], byteorder='big', signed=False)
            self.solPVV = int.from_bytes(Data[19:21], byteorder='big', signed=False) / 100
            self.solPVA = int.from_bytes(Data[21:23], byteorder='big', signed=True) / 10
            self.solEqPending = int.from_bytes(Data[23:25], byteorder='big', signed=False)
            self.solEqTimeRemaining = int.from_bytes(Data[25:27], byteorder='big', signed=False) / 10
            self.solRelay = int.from_bytes(Data[27:29], byteorder='big', signed=False)
            #self.solNA
            self.solLowBattAlarm = int.from_bytes(Data[31:33], byteorder='big', signed=False)
            self.solHighBattAlarm = int.from_bytes(Data[33:35], byteorder='big', signed=False)
            self.solYieldToday = int.from_bytes(Data[35:37], byteorder='big', signed=False) / 10
            self.solMaxPowToday = int.from_bytes(Data[37:39], byteorder='big', signed=False)
            self.solYieldYesterday = int.from_bytes(Data[39:41], byteorder='big', signed=False) / 10
            self.solMaxPowYesterday = int.from_bytes(Data[41:43], byteorder='big', signed=False)
            self.solErrorCode = int.from_bytes(Data[43:45], byteorder='big', signed=False)
            self.solPVPower = int.from_bytes(Data[45:47], byteorder='big', signed=False) / 10
            self.solUserYield = int.from_bytes(Data[47:49], byteorder='big', signed=False) / 10
            self.solOpMode = int.from_bytes(Data[49:51], byteorder='big', signed=False)
            
            self.power = str(self.solPVPower) + ";" + str(self.solUserYield * 1000)
            
            if Parameters["Mode6"] == "Debug":
                Domoticz.Log("self.solPVV: " + str(self.solPVV) + ", self.solPVA: " + str(self.solPVA) + ", self.solYieldToday: " + 
                    str(self.solYieldToday) + ", self.solMaxPowToday: " + str(self.solMaxPowToday) + ", self.solPVPower: " + str(self.solPVPower) +
                    ", self.solBatV: " + str(self.solBatV) +
                    ", self.solUserYield: " + str(self.solUserYield) +
                    ", self.power: " + str(self.power))
            
        elif 5 == self.idx:
            #Domoticz.Log("onMessage called for solar charger: " + str(Data))
            self.solBatV_250 = int.from_bytes(Data[9:11], byteorder='big', signed=False) / 100
            self.solBatA_250 = int.from_bytes(Data[11:13], byteorder='big', signed=True) / 10
            self.solBatTemp_250 = int.from_bytes(Data[13:15], byteorder='big', signed=True) / 10
            self.solOnOff_250 = int.from_bytes(Data[15:17], byteorder='big', signed=False)
            self.solState_250 = int.from_bytes(Data[17:19], byteorder='big', signed=False)
            self.solPVV_250 = int.from_bytes(Data[19:21], byteorder='big', signed=False) / 100
            self.solPVA_250 = int.from_bytes(Data[21:23], byteorder='big', signed=True) / 10
            self.solEqPending_250 = int.from_bytes(Data[23:25], byteorder='big', signed=False)
            self.solEqTimeRemaining_250 = int.from_bytes(Data[25:27], byteorder='big', signed=False) / 10
            self.solRelay_250 = int.from_bytes(Data[27:29], byteorder='big', signed=False)
            #self.solNA_250
            self.solLowBattAlarm_250 = int.from_bytes(Data[31:33], byteorder='big', signed=False)
            self.solHighBattAlarm_250 = int.from_bytes(Data[33:35], byteorder='big', signed=False)
            self.solYieldToday_250 = int.from_bytes(Data[35:37], byteorder='big', signed=False) / 10
            self.solMaxPowToday_250 = int.from_bytes(Data[37:39], byteorder='big', signed=False)
            self.solYieldYesterday_250 = int.from_bytes(Data[39:41], byteorder='big', signed=False) / 10
            self.solMaxPowYesterday_250 = int.from_bytes(Data[41:43], byteorder='big', signed=False)
            self.solErrorCode_250 = int.from_bytes(Data[43:45], byteorder='big', signed=False)
            self.solPVPower_250 = int.from_bytes(Data[45:47], byteorder='big', signed=False) / 10
            self.solUserYield_250 = int.from_bytes(Data[47:49], byteorder='big', signed=False) / 10
            self.solOpMode_250 = int.from_bytes(Data[49:51], byteorder='big', signed=False)
            
            self.power_250 = str(self.solPVPower_250) + ";" + str(self.solUserYield_250 * 1000)
            
            if Parameters["Mode6"] == "Debug":
                Domoticz.Log("self.solPVV_250: " + str(self.solPVV_250) + ", self.solPVA_250: " + str(self.solPVA_250) + ", self.solYieldToday_250: " + 
                    str(self.solYieldToday_250) + ", self.solMaxPowToday_250: " + str(self.solMaxPowToday_250) + ", self.solPVPower_250: " + str(self.solPVPower_250) +
                    ", self.solBatV_250: " + str(self.solBatV_250) +
                    ", self.solUserYield_250: " + str(self.solUserYield_250) +
                    ", self.power_250: " + str(self.power_250))
                
            
        if self.idx < len(self.registers):
            self.sendPriv()
        else:
            self.SyncDevices(0)
            self.idx = 0

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
        self.idx = 0
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
    
        try:
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
            
            if True == self.firstSolarCharger:
                UpdateDevice(self.UNIT_PVW, self.solPVPower, str(self.solPVPower), TimedOut)
                UpdateDevice(self.UNIT_PVALLPOW, 0, str(self.power), TimedOut) # 0 - it isn't a int
                UpdateDevice(self.UNIT_PVV, 0, str(self.solPVV), TimedOut)
                UpdateDevice(self.UNIT_PVA, 0, str(self.solPVA), TimedOut)
         
            UpdateDevice(self.UNIT_ACINVL2, self.acInVL2, str(self.acInVL2), TimedOut)
            UpdateDevice(self.UNIT_ACINAL2, self.acInAL2, str(self.acInAL2), TimedOut)
            UpdateDevice(self.UNIT_ACINWL2, self.acInWL2, str(self.acInWL2), TimedOut)
            UpdateDevice(self.UNIT_ACOUTVL2, self.acOutVL2, str(self.acOutVL2), TimedOut)
            UpdateDevice(self.UNIT_ACOUTAL2, self.acOutAL2, str(self.acOutAL2), TimedOut)
            UpdateDevice(self.UNIT_ACOUTWL2, self.acOutWL2, str(self.acOutWL2), TimedOut)
            
            UpdateDevice(self.UNIT_ACINVL3, self.acInVL3, str(self.acInVL3), TimedOut)
            UpdateDevice(self.UNIT_ACINAL3, self.acInAL3, str(self.acInAL3), TimedOut)
            UpdateDevice(self.UNIT_ACINWL3, self.acInWL3, str(self.acInWL3), TimedOut)
            UpdateDevice(self.UNIT_ACOUTVL3, self.acOutVL3, str(self.acOutVL3), TimedOut)
            UpdateDevice(self.UNIT_ACOUTAL3, self.acOutAL3, str(self.acOutAL3), TimedOut)
            UpdateDevice(self.UNIT_ACOUTWL3, self.acOutWL3, str(self.acOutWL3), TimedOut)        

            if True == self.secondSolarCharger:            
                if ( 0 != int(self.solPVPower_250 )):
                    UpdateDevice(self.UNIT_PVW_250, self.solPVPower_250, str(self.solPVPower_250), TimedOut)
                #self.power_2505.8;1975000.0
                if ( 0 != int(float(self.power_250.split(";")[1])//1 )):
                    UpdateDevice(self.UNIT_PVALLPOW_250, 0, str(self.power_250), TimedOut)
                UpdateDevice(self.UNIT_PVV_250, self.solPVV_250, str(self.solPVV_250), TimedOut)
                UpdateDevice(self.UNIT_PVA_250, self.solPVA_250, str(self.solPVA_250), TimedOut)   
        except Exception as e:
            Domoticz.Log("except: " + str(e))
            
        return

#    def onCommand(self, Unit, Command, Level, Hue):
#       Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
#       
#       if 99 == Level:
#           self.refreshData()

    def onDeviceModified(self, Unit):
        
        Device = Devices[Unit]
        Domoticz.Log("onDeviceModified called for Unit " + str(Unit) + " " + str(Device))
        #if 99 == Device.nValue:
        Domoticz.Log("Refresh data")
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
    else:
    	Domoticz.Log("Not found during update " + str(nValue) + ":'" + str(sValue) + "' (" + Devices[Unit].Name + ")")
    return
    