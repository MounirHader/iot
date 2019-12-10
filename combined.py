from ruuvitag_sensor.ruuvitag import RuuviTag
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from azure.iot.device import IoTHubDeviceClient, Message
import time
import sys
import os
import subprocess
import traceback
import logging
import threading

# Bluetooth devices to read data from
macs = ["DC:07:6C:EF:50:AF", "CF:EF:4C:B9:98:7B", "F0:D1:20:03:81:29"]
locations = ["office", "ff", "hr"]

# Device-specific shared access signature tokens for azure iot hub
sas_tokens = [
    "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-1;SharedAccessKey=05GB4CxnEYIje8sPI6HQsVcR3m0XFTvNIMBFzXwj5X4="
]

# IoT hub message format
MSG_TXT = '{{"timestamp": {timestamp}, "device_id": {device_id}, "temperature": {temperature}, \
          "humidity": {humidity}, "location": {location}}}'

# configure log settings
log = logging.getLogger("ruuvitag_sensor")
log.setLevel(logging.INFO)
logging.basicConfig(
    filename="ruuvisensor.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def iothub_client_init(device):
    client = IoTHubDeviceClient.create_from_connection_string(device)
    client.connect()
    return client


def iothub_client_run():
    # IoT hub device clients
    client = iothub_client_init(sas_tokens[0])
    sensorConnection = RuuviTagSensor()

    # Initialize sensor states
    states = {x: {"temperature": None, "humidity": None} for x in macs}
    # Sensor read loop
    starttime = time.time()
    counter = 0
    while True:
        counter += 1
        # scan for devices
        data = sensorConnection.get_data_for_sensors(macs=macs, search_duratio_sec=4)
        found_macs = data.keys()
        pulltime = time.strftime("%Y-%m-%d %H:%M:%S")
        # update states
        for i in range(len(found_macs)):
            states[found_macs[i]]["temperature"] = data[found_macs[i]]["temperature"]
            states[found_macs[i]]["humidity"] = data[found_macs[i]]["humidity"]

        # generate messages
        for i in range(len(macs)):
            msg_txt_formatted = MSG_TXT.format(
                device_id=i + 1,
                temperature=states[macs[i]]["temperature"],
                humidity=states[macs[i]]["humidity"],
                location=locations[i]
                timestamp=pulltime
            )
            # send messages to IoT hub
            client.send_message(Message(msg_txt_formatted))

        if counter % 100 == True:
            client.disconnect()
            client.connect()

        time.sleep(5.0 - ((time.time() - starttime) % 5))


if __name__ == "__main__":
    print("Future Facts IoT Hub - Ruuvitags")
    print("Press Ctrl-C to exit")
    iothub_client_run()
