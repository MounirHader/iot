from ruuvitag_sensor.ruuvitag import RuuviTag
import ruuvitag_sensor.log
from azure.iot.device import IoTHubDeviceClient, Message
import time
import sys
import os
import subprocess
import traceback
import logging
import threading

# bluetooth device to read
macs = ["DC:07:6C:EF:50:AF", "CF:EF:4C:B9:98:7B", "F0:D1:20:03:81:29"]

# device-specific shared access signature tokens for azure iot hub
sas_tokens = [
    "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-1;SharedAccessKey=05GB4CxnEYIje8sPI6HQsVcR3m0XFTvNIMBFzXwj5X4=",
    "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-2;SharedAccessKey=MWP1riNi4+ZSD8K28FzdQn9vD1PCYovk8hNsw1ff8nA=",
    "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-3;SharedAccessKey=TDpfGpLLFpzyxiMFG940HJ1D/GaK9qno5QuMuJcsxpU=",
]

# device to use (-1 added for indexing 0th list element for device 1)
MSG_TXT = (
    '{{"device_id": {device_id}, "temperature": {temperature},"humidity": {humidity}}}'
)

# configure log settings
logging.basicConfig(
    filename="rasppi.log", filemode="a", format="%(asctime)s \n %(message)s"
)


def iothub_client_init(device):
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(device)
    return client


def generate_message(sensors, device_index):
    state = None
    while state is None:
        try:
            sensor = sensors[device_index]
            state = sensor.update()
        except Exception as e:
            print(e)

    temperature = state["temperature"]
    humidity = state["humidity"]
    msg_txt_formatted = MSG_TXT.format(
        device_id=device_index + 1, temperature=temperature, humidity=humidity
    )
    message = Message(msg_txt_formatted)
    return message


def iothub_client_telemetry_sample_run():
    # IoT hub device clients
    client1 = iothub_client_init(sas_tokens[0])
    client2 = iothub_client_init(sas_tokens[1])
    client3 = iothub_client_init(sas_tokens[2])

    # RuuviTag sensors
    sensors = [RuuviTag(macs[0]), RuuviTag(macs[1]), RuuviTag(macs[2])]

    print("IoT Hub device sending periodic messages, press Ctrl-C to exit")
    starttime = time.time()
    while True:
        message1 = generate_message(sensors, 0)
        message2 = generate_message(sensors, 1)
        message3 = generate_message(sensors, 2)

        client1.send_message(message1)
        client2.send_message(message2)
        client3.send_message(message3)
        time.sleep(5.0 - ((time.time() - starttime) % 5))


if __name__ == "__main__":
    print("Future Facts IoT Hub - Ruuvitags")
    print("Press Ctrl-C to exit")
    iothub_client_telemetry_sample_run()
