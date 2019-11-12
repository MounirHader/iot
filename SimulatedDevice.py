# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import random
import time
from azure.iot.device import IoTHubDeviceClient, Message

sas_tokens = ["HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-1;SharedAccessKey=05GB4CxnEYIje8sPI6HQsVcR3m0XFTvNIMBFzXwj5X4=", "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-2;SharedAccessKey=MWP1riNi4+ZSD8K28FzdQn9vD1PCYovk8hNsw1ff8nA=", "HostName=future-facts-iothub.azure-devices.net;DeviceId=ruuvitag-3;SharedAccessKey=TDpfGpLLFpzyxiMFG940HJ1D/GaK9qno5QuMuJcsxpU="]

# Define the JSON message to send to IoT Hub.
TEMPERATURE = 20.0
HUMIDITY = 60
MSG_TXT = '{{"device_id": {device_id}, "temperature": {temperature},"humidity": {humidity}}}'

def iothub_client_init(CONNECTION_STRING):
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def create_message(device_id):
    temperature = TEMPERATURE + (random.random() * 15)
    humidity = HUMIDITY + (random.random() * 20)
    msg_txt_formatted = MSG_TXT.format(device_id=device_id,temperature=temperature, humidity=humidity)
    message = Message(msg_txt_formatted)
    return message

def iothub_client_telemetry_sample_run():

    try:
        client1 = iothub_client_init(sas_tokens[0])
        client2 = iothub_client_init(sas_tokens[1])
        client3 = iothub_client_init(sas_tokens[2])

        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

        while True:
            try:
              client1.send_message(create_message(1))
              client2.send_message(create_message(2))
              client3.send_message(create_message(3))
            except Exception as e:
              print(e)
            time.sleep(5)

    except Exception as e:
        print ( e )

if __name__ == '__main__':
    print ( "IoT Hub Quickstart #1 - Simulated device" )
    print ( "Press Ctrl-C to exit" )
    iothub_client_telemetry_sample_run()