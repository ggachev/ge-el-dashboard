from pyModbusTCP.client import ModbusClient
import pyModbusTCP.utils
import time
import pandas as pd

#Global constants
GRID_EMULATOR_IP = "192.168.55.215"
GRID_EMULATOR_PORT = 502
ELECTRONIC_LOAD_IP = "192.168.55.216"
ELECTRONIC_LOAD_PORT = 502

# Define the list for the Current_Output_U_RMS ,Current_Output_V_RMS and Current_Output_W_RMS
calibration_list = [0, 0, 0]

data_dict = {'Timestamp': [],
            'Analog_Output_1_U': [],
            'Analog_Output_2_U': [],
            'Analog_Output_1_V': [],
            'Analog_Output_2_V': [],
            'Analog_Output_1_W': [],
            'Analog_Output_2_W': [],
            'Voltage_Realtime_Output_U': [],
            'Voltage_Realtime_Output_V': [],
            'Voltage_Realtime_Output_W': [],
            'Voltage_Realtime_Slave': [],
            'Current_Realtime_OUT_U': [],
            'Current_Realtime_OUT_V': [],
            'Current_Realtime_OUT_W': [],
            'Voltage_Output_UV_RMS': [],
            'Voltage_Output_VW_RMS': [],
            'Voltage_Output_WU_RMS': [],
            'Voltage_Output_Intern_U': [],
            'Voltage_Output_Intern_V': [],
            'Voltage_Output_Intern_W': [],
            'Voltage_Output_U_RMS': [],
            'Voltage_Output_V_RMS': [],
            'Voltage_Output_W_RMS': [],
            'Current_Output_U_RMS': [],
            'Current_Output_V_RMS': [],
            'Current_Output_W_RMS': [],
            'Current_Output_Global': [],
            'Current_Output_Capacitor_U_RMS': [],
            'Current_Output_Capacitor_V_RMS': [],
            'Current_Output_Capacitor_W_RMS': [],
            'Power_Active_Output_U': [],
            'Power_Active_Output_V': [],
            'Power_Active_Output_W': [],
            'Power_Active_Output_Total': [],
            'Power_Reactive_Output_U': [],
            'Power_Reactive_Output_V': [],
            'Power_Reactive_Output_W': [],
            'Power_Reactive_Output_Total': [],
            'Power_Apparent_Output_U': [],
            'Power_Apparent_Output_V': [],
            'Power_Apparent_Output_W': [],
            'Power_Apparent_Output_Total': [],
            'Frequency_Output_U': [],
            'Frequency_Output_V': [],
            'Frequency_Output_W': [],
            'Phase_Angle_Output_U': [],
            'Phase_Angle_Output_V': [],
            'Phase_Angle_Output_W': [],
            'UV_desf_angle': [],
            'VW_desf_angle': [],
            'Analog_Input_Realtime_1': [],
            'Analog_Input_Realtime_2': [],
            'Analog_Input_Realtime_3': [],
            'Analog_Input_Realtime_4': [],
            'Analog_Input_Realtime_5': [],
            'Analog_Input_Realtime_6': [],
            'Vbus_menys': [],
            'Vbus_mes': [],
            'Vbus_Total': []}

#Modbus Client for the grid emulator
gridEmulator = ModbusClient(host=GRID_EMULATOR_IP, port=GRID_EMULATOR_PORT, unit_id=1, auto_open=True, timeout=10)

#Modbus Client for the electronic load
electronicLoad = ModbusClient(host=ELECTRONIC_LOAD_IP, port=ELECTRONIC_LOAD_PORT, unit_id=1, auto_open=True, timeout=10)

#Function taking a number (long or int) and returning it in a IEEE Big Endian
def int_to_register(a):
    """Function taking a number (long or int) and returning it in a IEEE Big Endian)

    :param a: number to be transfered
    :type a: int or long
    """
    a = pyModbusTCP.utils.encode_ieee(a, double=False)
    list_a = [a]
    list_a = pyModbusTCP.utils.long_list_to_word(list_a, big_endian=True, long_long=False)
    return list_a

#Function taking a number (long or int) and returning it in a IEEE Big Endian
def register_to_int(val_list):
    """Function taking a register output and writing it in a list of ints

    :param a: data from register
    """
    list_of_ints = []
    new_list = pyModbusTCP.utils.word_list_to_long(val_list, big_endian=True, long_long=False)
    for i in range(0, len(new_list)):
        list_of_ints.append(pyModbusTCP.utils.decode_ieee(new_list[i], double=False))
    return list_of_ints

def start_grid_emulator():
    """Function starting the grid emulator according to Section 3.1 and 3.2 table 3.2.1 from the user manual

    """
    #Check connection with grid emulator
    boolean = gridEmulator.read_holding_registers(17002, 2)
    if gridEmulator.last_error:
        print(gridEmulator.last_error_as_txt)
        raise Exception("Connecting to the grid emulator timeout")

    #Strt the GridEmulator -> from Standy to Run Grid Emulator Mode Section 3.1 and 3.2 table 3.2.1
    #Step 1 CW_EnableDisable -> should be 1
    gridEmulator.write_multiple_registers(17000, int_to_register(1))
    boolean = gridEmulator.read_holding_registers(17000, 2)
    while not boolean[1]:
        print("Waiting for enable state")
        gridEmulator.write_multiple_registers(17000, int_to_register(1))
        time.sleep(1)
        boolean = gridEmulator.read_holding_registers(17000, 2)

    for i in range(0, 10):
        print("Starting GE machine...")
        time.sleep(1)

    #Step 2 CW_RunReady -> should be 1
    gridEmulator.write_multiple_registers(17002, int_to_register(1))

    #Step 3 Wait for CW_RunReady to be 1
    boolean = gridEmulator.read_holding_registers(17002, 2)
    while not boolean[1]:
        print("Waiting for run state")
        gridEmulator.write_multiple_registers(17002, int_to_register(1))
        time.sleep(1)
        boolean = gridEmulator.read_holding_registers(17002, 2)

    #Step 4 Read SW_GE_EL_Selector -> should be 1
    boolean = gridEmulator.read_holding_registers(16012, 2)
    if not boolean[1]:
        raise Exception("SW_GE_EL_Selector not 1")

    #Step 5 Read SW_AC_DC_Selector_U -> should be 1
    boolean = gridEmulator.read_holding_registers(16006, 2)
    if not boolean[1]:
        raise Exception("SW_AC_DC_Selector_U not 1")

    #Step 6 Read SW_AC_DC_Selector_V -> should be 1
    boolean = gridEmulator.read_holding_registers(16008, 2)
    if not boolean[1]:
        raise Exception("SW_AC_DC_Selector_V not 1")

    #Step 7 Read SW_AC_DC_Selector_W -> should be 1
    boolean = gridEmulator.read_holding_registers(16010, 2)
    if not boolean[1]:
        raise Exception("SW_AC_DC_Selector_W not 1")

    #Step 8 Read SW_OutputConnection -> should be 0 for 3 channel output
    boolean = gridEmulator.read_holding_registers(16014, 2)
    if boolean[1]:
        raise Exception("SW_OutputConnection not 0 (for 3 channel output)")

    #Step 9 Activate voltage Mode for all 3 phases and check if so (CW_ControlOperationU, CW_ControlOperationV, CW_ControlOperationW) all 3 should be 0
    gridEmulator.write_multiple_registers(17004, int_to_register(0))
    gridEmulator.write_multiple_registers(17006, int_to_register(0))
    gridEmulator.write_multiple_registers(17008, int_to_register(0))
    val_list = gridEmulator.read_holding_registers(16022, 6)
    for i in val_list:
        if i:
            raise Exception("Control operating mode not set to voltage source")


def start_electronic_load():
    """Function starting the electronic load according to Section 4.1 and 4.2 table 4.2.1 from the user manual

    """
    #Check connection with electronic load
    boolean = electronicLoad.read_holding_registers(17002, 2)
    if electronicLoad.last_error:
        print(electronicLoad.last_error_as_txt)
        raise Exception("Connecting to the electronic load timeout")

    #Start the electronic load -> from Standy to Run electronic load Mode Section 4.1 and 4.2 table 4.2.1
    #Step 1 CW_EnableDisable -> should be 1
    electronicLoad.write_multiple_registers(17000, int_to_register(1))
    boolean = electronicLoad.read_holding_registers(17000, 2)
    while not boolean[1]:
        print("Waiting for enable state")
        electronicLoad.write_multiple_registers(17000, int_to_register(1))
        time.sleep(1)
        boolean = electronicLoad.read_holding_registers(17000, 2)

    for i in range(0, 10):
        print("Starting EL machine...")
        time.sleep(1)

    #Step 2 CW_RunReady -> should be 1
    electronicLoad.write_multiple_registers(17002, int_to_register(1))

    #Step 3 Wait for CW_RunReady to be 1
    boolean = electronicLoad.read_holding_registers(17002, 2)
    while not boolean[1]:
        print("Waiting for run state")
        electronicLoad.write_multiple_registers(17002, int_to_register(1))
        time.sleep(1)
        boolean = electronicLoad.read_holding_registers(17002, 2)

    #Step 4 Read SW_GE_EL_Selector -> should be 0
    boolean = electronicLoad.read_holding_registers(16012, 2)
    if not boolean[1]:
        raise Exception("SW_GE_EL_Selector not 0")

    #Step 5 Read SW_AC_DC_Selector_U -> should be 1
    boolean = electronicLoad.read_holding_registers(16006, 2)
    if not boolean[1]:
        raise Exception("SW_AC_DC_Selector_U not 1")

    #Step 6 Read SW_AC_DC_Selector_V -> should be 1
    boolean = electronicLoad.read_holding_registers(16008, 2)
    if not boolean[1]:
        raise Exception("SW_AC_DC_Selector_V not 1")

    #Step 7 Read SW_AC_DC_Selector_W -> should be 1
    boolean = electronicLoad.read_holding_registers(16010, 2)
    if not boolean[1]:
        raise Exception("SW_AC_DC_Selector_W not 1")

    #Step 9 Activate current Mode for all 3 phases and check if so (CW_ControlOperationU, CW_ControlOperationV, CW_ControlOperationW) all 3 should be 1
    electronicLoad.write_multiple_registers(17004, int_to_register(1))
    electronicLoad.write_multiple_registers(17006, int_to_register(1))
    electronicLoad.write_multiple_registers(17008, int_to_register(1))
    val_list = electronicLoad.read_holding_registers(16022, 6)
    for num in range(0, 5 + 1):
        if num % 2 != 0:
            if not val_list[num]:
                raise Exception("Control operating mode not set to current source")

def set_current(current_list_u, current_list_v, current_list_w):
    """Function taking lists with the currents for the three phases and sending them to the electronic load

    :param current_list_u: List of the current specification for phase u according to example 4.2.1 from the Cinergia Modbus data table
    :type current_list_u: List of values
    :param current_list_v: List of the current specification for phase v according to example 4.2.1 from the Cinergia Modbus data table
    :type current_list_v: List of values
    :param current_list_w: List of the current specification for phase w according to example 4.2.1 from the Cinergia Modbus data table
    :type current_list_w: List of values
    """
    #PHASE U
    electronicLoad.write_multiple_registers(27066, int_to_register(current_list_u[0]))
    electronicLoad.write_multiple_registers(27068, int_to_register(current_list_u[1]))
    electronicLoad.write_multiple_registers(27070, int_to_register(current_list_u[2]))
    electronicLoad.write_multiple_registers(27072, int_to_register(current_list_u[3]))

    #PHASE V
    electronicLoad.write_multiple_registers(27074, int_to_register(current_list_v[0]))
    electronicLoad.write_multiple_registers(27076, int_to_register(current_list_v[1]))
    electronicLoad.write_multiple_registers(27078, int_to_register(current_list_v[2]))
    electronicLoad.write_multiple_registers(27080, int_to_register(current_list_v[3]))

    #PHASE W
    electronicLoad.write_multiple_registers(27082, int_to_register(current_list_w[0]))
    electronicLoad.write_multiple_registers(27084, int_to_register(current_list_w[1]))
    electronicLoad.write_multiple_registers(27086, int_to_register(current_list_w[2]))
    electronicLoad.write_multiple_registers(27088, int_to_register(current_list_w[3]))

def set_voltage(EU, voltages_list_u, voltages_list_v, voltages_list_w):
    """Function taking a boolean if the EU voltage standard should be used and lists with the voltages for the three phases if not so

    :param EU: if the standard EU voltage should be used
    :type EU: 0 or 1
    :param voltages_list_u: List of the voltage specification for phase u according to example 3.2.1 from the Cinergia Modbus data table
    :type voltages_list_u: List of values
    :param voltages_list_v: List of the voltage specification for phase v according to example 3.2.1 from the Cinergia Modbus data table
    :type voltages_list_u: List of values
    :param voltages_list_w: List of the voltage specification for phase w according to example 3.2.1 from the Cinergia Modbus data table
    :type voltages_list_u: List of values
    """
    if EU == 1:
        #PHASE U with 230V EU
        gridEmulator.write_multiple_registers(27010, int_to_register(1))
        gridEmulator.write_multiple_registers(27012, int_to_register(50))
        gridEmulator.write_multiple_registers(27014, int_to_register(0))
        gridEmulator.write_multiple_registers(27016, int_to_register(100))
        gridEmulator.write_multiple_registers(27018, int_to_register(10))
        gridEmulator.write_multiple_registers(27020, int_to_register(0))
        gridEmulator.write_multiple_registers(27022, int_to_register(230))

        #PHASE V with 230V EU
        gridEmulator.write_multiple_registers(27024, int_to_register(1))
        gridEmulator.write_multiple_registers(27026, int_to_register(50))
        gridEmulator.write_multiple_registers(27028, int_to_register(0))
        gridEmulator.write_multiple_registers(27030, int_to_register(100))
        gridEmulator.write_multiple_registers(27032, int_to_register(10))
        gridEmulator.write_multiple_registers(27034, int_to_register(-120))
        gridEmulator.write_multiple_registers(27036, int_to_register(230))

        #PHASE W with 230V EU
        gridEmulator.write_multiple_registers(27038, int_to_register(1))
        gridEmulator.write_multiple_registers(27040, int_to_register(50))
        gridEmulator.write_multiple_registers(27042, int_to_register(0))
        gridEmulator.write_multiple_registers(27044, int_to_register(100))
        gridEmulator.write_multiple_registers(27046, int_to_register(10))
        gridEmulator.write_multiple_registers(27048, int_to_register(-240))
        gridEmulator.write_multiple_registers(27050, int_to_register(230))
    else:
        #PHASE U voltage from voltages_list_u
        gridEmulator.write_multiple_registers(27010, int_to_register(voltages_list_u[0]))
        gridEmulator.write_multiple_registers(27012, int_to_register(voltages_list_u[1]))
        gridEmulator.write_multiple_registers(27014, int_to_register(voltages_list_u[2]))
        gridEmulator.write_multiple_registers(27016, int_to_register(voltages_list_u[3]))
        gridEmulator.write_multiple_registers(27018, int_to_register(voltages_list_u[4]))
        gridEmulator.write_multiple_registers(27020, int_to_register(voltages_list_u[5]))
        gridEmulator.write_multiple_registers(27022, int_to_register(voltages_list_u[6]))

        #PHASE V with voltage from voltages_list_v
        gridEmulator.write_multiple_registers(27024, int_to_register(voltages_list_v[0]))
        gridEmulator.write_multiple_registers(27026, int_to_register(voltages_list_v[1]))
        gridEmulator.write_multiple_registers(27028, int_to_register(voltages_list_v[2]))
        gridEmulator.write_multiple_registers(27030, int_to_register(voltages_list_v[3]))
        gridEmulator.write_multiple_registers(27032, int_to_register(voltages_list_v[4]))
        gridEmulator.write_multiple_registers(27034, int_to_register(voltages_list_v[5]))
        gridEmulator.write_multiple_registers(27036, int_to_register(voltages_list_v[6]))

        #PHASE W with voltage from voltages_list_w
        gridEmulator.write_multiple_registers(27038, int_to_register(voltages_list_w[0]))
        gridEmulator.write_multiple_registers(27040, int_to_register(voltages_list_w[1]))
        gridEmulator.write_multiple_registers(27042, int_to_register(voltages_list_w[2]))
        gridEmulator.write_multiple_registers(27044, int_to_register(voltages_list_w[3]))
        gridEmulator.write_multiple_registers(27046, int_to_register(voltages_list_w[4]))
        gridEmulator.write_multiple_registers(27048, int_to_register(voltages_list_w[5]))
        gridEmulator.write_multiple_registers(27050, int_to_register(voltages_list_w[6]))

def grid_emulator_activate_config():
    #Activate config
    gridEmulator.write_multiple_registers(17020, int_to_register(1))
    # Sleep to wait to populate the values
    time.sleep(1)

def grid_emulator_calibrate():
    global calibration_list

    #Take the values that are read to have the calibration offset
    val_list = gridEmulator.read_holding_registers(26100, 6)
    calibration_list = register_to_int(val_list)
    print("Calibration offset: " + str(calibration_list))
    return calibration_list

def electronic_load_activate_config():
    #Activate config
    electronicLoad.write_multiple_registers(17020, int_to_register(1))

def read_RMS_Voltage(number_steps):
#Read RMS Voltage for UVW (the 3 phases)
    for _ in range(0, number_steps):
        zahl = []
        val_list = gridEmulator.read_holding_registers(26094, 6)
        new_list = pyModbusTCP.utils.word_list_to_long(val_list, big_endian=True, long_long=False)
        for i in range(0, len(new_list)):
            zahl.append(pyModbusTCP.utils.decode_ieee(new_list[i], double=False))
        print("RMS Voltage U V W", zahl)
        time.sleep(1)

def read_specific_register():
    val_list = gridEmulator.read_holding_registers(22168, 6)
    list_of_values = register_to_int(val_list)

    val_list = gridEmulator.read_holding_registers(22180, 6)
    list_of_values.extend(register_to_int(val_list))
    return list_of_values

def write_specific_register():
    boolean = gridEmulator.write_multiple_registers(22182, int_to_register(1))
    print(boolean)
    boolean = gridEmulator.write_multiple_registers(22168, int_to_register(0.14))
    print(boolean)
    boolean = gridEmulator.write_multiple_registers(22170, int_to_register(0.14))
    print(boolean)
    boolean = gridEmulator.write_multiple_registers(22172, int_to_register(0.14))
    print(boolean)
    boolean = gridEmulator.write_multiple_registers(22182, int_to_register(0))
    print(boolean)

def read_all_outputs(u_active, v_active, w_active):
    global data_dict
    global calibration_list

    list_of_all_values = []
    temp_list = []

    #Print time stamp before reading the registers
    timestamp = pd.Timestamp.today().strftime('%d.%m.%Y %H:%M:%S.%f')
    print("Start reading @", timestamp)

    #Read the first 13 registers (from 26042 to 26066)
    val_list = gridEmulator.read_holding_registers(26042, 26)
    list_of_all_values = register_to_int(val_list)

    #Read the next 36 registers (from 26082 to 26152)
    val_list = gridEmulator.read_holding_registers(26082, 72)
    temp_list = register_to_int(val_list)

    # Substract the calibration offset, if not set it will substract 0
    # If phase not selected ignore the resault that was read
    # Substract U, V and W
    if u_active:
        temp_list[9] = temp_list[9] - calibration_list[0]
    else:
        temp_list[9] = 0
    if v_active:
        temp_list[10] = temp_list[10] - calibration_list[1]
    else:
        temp_list[10] = 0
    if w_active:
        temp_list[11] = temp_list[11] - calibration_list[2]
    else:
        temp_list[11] = 0

    #Add the values to the main list
    list_of_all_values.extend(temp_list)
    
    #Read the last 9 registers (from 26172 to 26188)
    val_list = gridEmulator.read_holding_registers(26172, 18)
    list_of_all_values.extend(register_to_int(val_list))

    #Print time stamp after reading the registers
    print("End reading @", pd.Timestamp.today().strftime('%d.%m.%Y %H:%M:%S.%f'))

    #Add the data to the dictionary with a timestamp at the beginning
    j = 0
    for keys in data_dict:
        if j == 0:
            data_dict[keys].append(timestamp)
        else:
            data_dict[keys].append(list_of_all_values[j-1])
        j += 1

def read_grid_emulator_temp():
    """Function returning the intake temperature of the grid emulator

    :returns: int of the temperature
    """
    temperature = gridEmulator.read_holding_registers(16104, 2)
    temperature_int = register_to_int(temperature)
    temperature_int = int(temperature_int[0])
    return temperature_int

def save_dataframe_to_csv(filepath):
    global data_dict

    #Create a dataframe for pandas
    df = pd.DataFrame.from_dict(data_dict)

    #Print out to the CSV at FILEPATH
    df.to_csv(filepath)

    #Clear dictionary
    data_dict = {'Timestamp': [],
            'Analog_Output_1_U': [],
            'Analog_Output_2_U': [],
            'Analog_Output_1_V': [],
            'Analog_Output_2_V': [],
            'Analog_Output_1_W': [],
            'Analog_Output_2_W': [],
            'Voltage_Realtime_Output_U': [],
            'Voltage_Realtime_Output_V': [],
            'Voltage_Realtime_Output_W': [],
            'Voltage_Realtime_Slave': [],
            'Current_Realtime_OUT_U': [],
            'Current_Realtime_OUT_V': [],
            'Current_Realtime_OUT_W': [],
            'Voltage_Output_UV_RMS': [],
            'Voltage_Output_VW_RMS': [],
            'Voltage_Output_WU_RMS': [],
            'Voltage_Output_Intern_U': [],
            'Voltage_Output_Intern_V': [],
            'Voltage_Output_Intern_W': [],
            'Voltage_Output_U_RMS': [],
            'Voltage_Output_V_RMS': [],
            'Voltage_Output_W_RMS': [],
            'Current_Output_U_RMS': [],
            'Current_Output_V_RMS': [],
            'Current_Output_W_RMS': [],
            'Current_Output_Global': [],
            'Current_Output_Capacitor_U_RMS': [],
            'Current_Output_Capacitor_V_RMS': [],
            'Current_Output_Capacitor_W_RMS': [],
            'Power_Active_Output_U': [],
            'Power_Active_Output_V': [],
            'Power_Active_Output_W': [],
            'Power_Active_Output_Total': [],
            'Power_Reactive_Output_U': [],
            'Power_Reactive_Output_V': [],
            'Power_Reactive_Output_W': [],
            'Power_Reactive_Output_Total': [],
            'Power_Apparent_Output_U': [],
            'Power_Apparent_Output_V': [],
            'Power_Apparent_Output_W': [],
            'Power_Apparent_Output_Total': [],
            'Frequency_Output_U': [],
            'Frequency_Output_V': [],
            'Frequency_Output_W': [],
            'Phase_Angle_Output_U': [],
            'Phase_Angle_Output_V': [],
            'Phase_Angle_Output_W': [],
            'UV_desf_angle': [],
            'VW_desf_angle': [],
            'Analog_Input_Realtime_1': [],
            'Analog_Input_Realtime_2': [],
            'Analog_Input_Realtime_3': [],
            'Analog_Input_Realtime_4': [],
            'Analog_Input_Realtime_5': [],
            'Analog_Input_Realtime_6': [],
            'Vbus_menys': [],
            'Vbus_mes': [],
            'Vbus_Total': []}

def stop_grid_emulator():
    #CW_EnableDisable -> should be 0 to TURN OFF
    print("Shutting down GE...")
    gridEmulator.write_multiple_registers(17000, int_to_register(0))
    boolean = gridEmulator.read_holding_registers(17000, 2)
    if boolean[1]:
        raise Exception("CW_EnableDisable at EL not 0")
    print("GE Device Standby")
    gridEmulator.close()

def stop_electronic_load():
    #CW_EnableDisable -> should be 0 to TURN OFF
    print("Shutting down EL...")
    electronicLoad.write_multiple_registers(17000, int_to_register(0))
    boolean = electronicLoad.read_holding_registers(17000, 2)
    if boolean[1]:
        raise Exception("CW_EnableDisable at EL not 0")
    print("EL device Standby")
    gridEmulator.close()

def test_func(uvalue, vvalue, wvalue):
    print(uvalue, vvalue, wvalue)