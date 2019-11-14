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

# Device-specific shared access signature tokens for azure iot hub
sas_tokens = [
    "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-1;SharedAccessKey=05GB4CxnEYIje8sPI6HQsVcR3m0XFTvNIMBFzXwj5X4=",
    "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-2;SharedAccessKey=MWP1riNi4+ZSD8K28FzdQn9vD1PCYovk8hNsw1ff8nA=",
    "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-3;SharedAccessKey=TDpfGpLLFpzyxiMFG940HJ1D/GaK9qno5QuMuJcsxpU=",
]

# IoT hub message format
MSG_TXT = '{{"timestamp": {timestamp}, "device_id": {device_id}, "temperature": {temperature},"humidity": {humidity}}}'

# configure log settings
log = logging.getLogger("ruuvitag_sensor")
log.setLevel(logging.INFO)
logging.basicConfig(
    filename="ruuvisensor.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def iothub_client_init(device):
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(device)
    return client


def iothub_client_run():
    log.info("Starting script")
    # IoT hub device clients
    clients = [iothub_client_init(x) for x in sas_tokens]
    sensorConnection = RuuviTagSensor()
    log.info("Devices successfully connected to IoT hub")

    print("Devices now start sending messages to IoT hub, press Ctrl-C to exit")
    # Initialize sensor states
    states = {x: {"temperature": None, "humidity": None} for x in macs}
    # Sensor read loop
    starttime = time.time()
    while True:
        # scan for devices
        data = sensorConnection.get_data_for_sensors(macs=macs, search_duratio_sec=4)
        found_macs = data.keys()
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
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            # send messages to IoT hub
            clients[i].send_message(Message(msg_txt_formatted))

        time.sleep(5.0 - ((time.time() - starttime) % 5))


if __name__ == "__main__":
    print("Future Facts IoT Hub - Ruuvitags")
    print("Press Ctrl-C to exit")
    iothub_client_run()
