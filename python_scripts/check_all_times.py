from datetime import datetime as dt
from smbus2 import SMBus
import subprocess
import traceback
import time
import sys

RTC_ADDRESS = 104
I2C_BUS_NUMBER = 1  # Replace with the actual bus number if different

def stderr_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def read_rtc_data(bus):
    return bus.read_i2c_block_data(RTC_ADDRESS, 0, 8)

def hex_rtc_data(bus):
    return [hex(x) for x in read_rtc_data(bus)]

def dec_rtc_data(hex_data):
    return [int(x.replace("0x", ""), 16) for x in hex_data]

def convert_rtc_format_to_timedatectl_format(bus):
    rtc_data = dec_rtc_data(hex_rtc_data(bus))
    return f"20{rtc_data[6]:02}-{rtc_data[5]:02}-{rtc_data[4]:02} {rtc_data[2]:02}:{rtc_data[1]:02}:{rtc_data[0]:02}"

def run_command(command, error_message, success_message=None):
    try:
        result = subprocess.check_output(command)
        if success_message:
            print(success_message)
        return result.decode('utf-8')
    except Exception as e:
        stderr_print(f"{error_message}: {str(e)}")
        return None

def check_and_print(command, success_message, error_message):
    result = run_command(command, error_message, success_message)
    if result:
        print(result)

def check_times():
    bus = SMBus(I2C_BUS_NUMBER)
    
    check_and_print(["timedatectl"], None, "Unable to run timedatectl for system time info")
    check_and_print(['sudo', 'hwclock', '-r'], "Time from internal RTC rtc0 (PSEQ_RTC, being used) is: {result}", "Unable to obtain time from internal RTC rtc0 (PSEQ_RTC, being used) for validation")
    check_and_print(['timedatectl'], "Time from external RTC (DS3231) is: {result}", "Unable to obtain time from external RTC for validation")
    check_and_print(['sudo', 'hwclock', '--rtc', '/dev/rtc1'], "Time from internal RTC rtc1 (tegra-RTC, not being used) is: {result}", "Unable to obtain time from internal RTC rtc1 (tegra-RTC, not being used)")
    
    if bus:
        bus.close()

if __name__ == "__main":
    check_times()
