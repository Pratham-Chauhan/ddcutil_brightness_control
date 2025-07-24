import subprocess
import re
import sys
import time
import os
import signal
from multiprocessing import Process
from pathlib import Path

PID_FILE = Path("/tmp/ddc_brightness_setter.pid")
COUNTER_FILE = Path("/tmp/ddc_brightness_counter")
# COUNTER_FILE.touch(exist_ok=True)

def get_current_brightness():
    for _ in range(4):
        try:
            output = subprocess.check_output(['ddcutil', 'getvcp', '10'], text=True)
            match = re.search(r'current value\s*=\s*(\d+)', output)
            if match:
                return int(match.group(1))
        except subprocess.CalledProcessError as e:
            print("Failed to get current brightness. Retrying.")
            # print(output)

    return None



def set_counter(flag):
    if flag == 'increment':
        try:
            with COUNTER_FILE.open("r") as f:
                current_value = int(f.read())

            with COUNTER_FILE.open("w") as f:
                new_value = current_value + 1
                f.write(str(new_value))

        except FileNotFoundError:
            with COUNTER_FILE.open("w") as f:
                f.write("1")
                
    elif flag == 'set':
        with COUNTER_FILE.open("w") as f:
            f.write("0")


def set_brightness(value):
    for _ in range(4):
        try:
            subprocess.run(['ddcutil', 'setvcp', '10', str(value)], check=True)
            set_counter('set')
            break
        except subprocess.CalledProcessError as e:
            print("Failed to set brightness. Retrying.")
            # print(e)

    subprocess.run(['kdialog', '--title', 'Brightness', '--passivepopup', f'{value}%', '1'])

def brightness_worker(value):
    print("Starting brightness worker")
    time.sleep(.2)

    with COUNTER_FILE.open("r") as f:
        c = int(f.read())

    current = get_current_brightness()
    if current is not None:
        new = min(current + (value*c), 100)
        set_brightness(new)

def kill_previous():
    if PID_FILE.exists():
        try:
            with PID_FILE.open("r") as f:
                pid = int(f.read())
            os.kill(pid, signal.SIGTERM)
            print('Process killed:', pid)
        except Exception:
            pass
        PID_FILE.unlink(missing_ok=True)

def main(value):
    # Kill the previous process
    kill_previous()
    set_counter('increment')
    # Start a new process
    p = Process(target=brightness_worker, args=(value,))
    p.start()

    # Write the current process ID to a file
    with PID_FILE.open("w") as f:
        print('Process ID:', p.pid)
        f.write(str(p.pid))

if __name__ == "__main__":
    try:
        value = int(sys.argv[1])
        print("offset value:", value)
    except (IndexError, ValueError):
        print("Usage: python3 increase_brightness_code.py <value>")
        exit(1)
    
    main(value)

