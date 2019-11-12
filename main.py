from ruuvitag_sensor.ruuvitag import RuuviTag
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
DEVICE_ID = int(sys.argv[1]) - 1
CONNECTION_STRING = sas_tokens[DEVICE_ID]
MSG_TXT = (
    '{{"device_id": {device_id}, "temperature": {temperature},"humidity": {humidity}}}'
)

# configure log settings
logging.basicConfig(
    filename="rasppi.log", filemode="a", format="%(asctime)s \n %(message)s"
)


def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client


def iothub_client_telemetry_sample_run():
    client = iothub_client_init()
    print("IoT Hub device sending periodic messages, press Ctrl-C to exit")
    starttime = time.time()
    while True:
        state = None
        while state is None:
            try:
                sensor = RuuviTag(macs[DEVICE_ID])
                state = sensor.update()
            except Exception as e:
                print(e)
                os.system("sudo reboot")

        #                 print("Connection error, restarting bluetooth drivers...")
        #                 subprocess.call("sudo hciconfig hci0 down".split())
        #                 subprocess.call("sudo hciconfig hci0 up".split())

        temperature = state["temperature"]
        humidity = state["humidity"]
        msg_txt_formatted = MSG_TXT.format(
            device_id=DEVICE_ID + 1, temperature=temperature, humidity=humidity
        )
        message = Message(msg_txt_formatted)

        print(time.ctime())
        print("Sending message: {}".format(message))
        client.send_message(message)
        print("Message successfully sent")
        time.sleep(2.0 - ((time.time() - starttime) % 2))


if __name__ == "__main__":
    print("Future Facts IoT Hub - Ruuvitag {}".format(DEVICE_ID + 1))
    print("Press Ctrl-C to exit")
    iothub_client_telemetry_sample_run()
