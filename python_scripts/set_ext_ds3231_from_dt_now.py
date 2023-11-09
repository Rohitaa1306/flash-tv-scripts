from datetime import datetime as dt
from smbus2 import SMBus
import traceback
import sys

# Constants
RTC_ADDRESS = 104  # Replace with the actual RTC address if different
I2C_BUS_NUMBER = 1  # Replace with the actual bus number if different

def stderr_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_bcd(value):
    # Converts an integer to BCD format
    return (value // 10) << 4 | (value % 10)

def get_current_time_bcd():
    now = dt.now()
    return [
        get_bcd(now.second),
        get_bcd(now.minute),
        get_bcd(now.hour),
        get_bcd(now.weekday() + 1),  # Adjust weekday to RTC format (1-7)
        get_bcd(now.day),
        get_bcd(now.month),
        get_bcd(now.year % 100)  # Get last two digits of the year
    ]

def set_external_rtc_time():
    try:
        bus = SMBus(I2C_BUS_NUMBER)
        bus.write_i2c_block_data(RTC_ADDRESS, 0, get_current_time_bcd())
        bus.close()
        print(f"Time for external RTC was set to: {get_current_time_bcd()}")
    except:
        stderr_print(traceback.format_exc())
        stderr_print("Failed to properly set time for external RTC. Please retry before continuing.")
        sys.exit(1)

def save_current_date_to_file(file_path):
    current_date = dt.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, "w") as file:
        file.write(current_date)

if __name__ == "__main__":
    famid = sys.argv[1]
    set_external_rtc_time()
    save_current_date_to_file(f"{famid}_start_date.txt")

