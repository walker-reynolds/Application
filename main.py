import time
import socket
import struct
import platform
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import tkinter as tk
import threading

# Define MQTT broker details
broker_address = "45.76.236.64"
broker_port = 1883

# Set up MQTT client
client = mqtt.Client()

# Define callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code " + str(rc))

def on_publish(client, userdata, mid):
    global topic, payload_json
    print("Message published with message id " + str(mid))
    print("Topic: " + topic)
    print("Payload: " + payload_json)
    update_topics(topic, payload_json)

# Set up MQTT client callbacks
client.on_connect = on_connect
client.on_publish = on_publish

# Define function to stop the MQTT client
def stop_client():
    client.disconnect()
    client.loop_stop()
    root.destroy()

# Define function to publish a message to the MQTT broker
def publish_message():
    global topic, payload_json
    # Get host information
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    local_time = int(time.time())
    os_info = platform.platform()
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Define Sparkplug B message payload using JSON
    payload = {
        "timestamp": local_time,
        "datetime": dt_string,
        "data": {
            "temp": 23.5,
            "pressure": 1001.2,
            "humidity": 45.0
        },
        "device": {
            "type": "app",
            "name": hostname,
            "ip": ip_address,
            "os": os_info
        }
    }

    # Serialize payload to JSON format
    payload_json = json.dumps(payload)

    # Publish Sparkplug B message with EON ID 'app'
    topic = "spBv1.0/app/" + hostname + "/data"
    mid = client.publish(topic, payload_json, qos=1, retain=True)

    # Wait for message to be published
    mid.wait_for_publish()

# Define function to update the topic list on the GUI window
def update_topics(topic, payload):
    data = json.loads(payload)
    timestamp = data['timestamp']
    dt_string = data['datetime']
    temp = data['data']['temp']
    pressure = data['data']['pressure']
    humidity = data['data']['humidity']
    device_name = data['device']['name']
    device_ip = data['device']['ip']
    device_os = data['device']['os']

# Create GUI window
root = tk.Tk()
root.title("MQTT Client")
root.geometry("400x300")
# Create listbox to display published topics and payloads
topics_listbox = tk.Listbox(root, width=50)
topics_listbox.pack(padx=10, pady=10)

# Create 'Publish' button to publish message to MQTT broker
publish_button = tk.Button(root, text="Publish", command=publish_message)
publish_button.pack(padx=10, pady=10)

# Create 'Stop' button to stop MQTT client and close window
stop_button = tk.Button(root, text="Stop", command=stop_client)
stop_button.pack(padx=10, pady=10)

# Set up MQTT client connection to broker
client.connect(broker_address, broker_port)

# Start network loop in a separate thread
client.loop_start()

# Define function to update the topic list on the GUI window
def update_topics(topic, payload):
    data = json.loads(payload)
    timestamp = data['timestamp']
    dt_string = data['datetime']
    temp = data['data']['temp']
    pressure = data['data']['pressure']
    humidity = data['data']['humidity']
    device_name = data['device']['name']
    device_ip = data['device']['ip']
    device_os = data['device']['os']

    # Create string to display in listbox
    topic_string = f"Topic: {topic}\n"
    payload_string = f"Timestamp: {timestamp}\n"
    payload_string += f"Date/time: {dt_string}\n"
    payload_string += f"Temperature: {temp}\n"
    payload_string += f"Pressure: {pressure}\n"
    payload_string += f"Humidity: {humidity}\n"
    payload_string += f"Device name: {device_name}\n"
    payload_string += f"Device IP: {device_ip}\n"
    payload_string += f"Device OS: {device_os}\n"

    # Insert topic and payload string into listbox
    topics_listbox.insert(tk.END, topic_string)
    topics_listbox.insert(tk.END, payload_string)
    topics_listbox.see(tk.END)

    # Remove oldest items from listbox if necessary
    if topics_listbox.size() > 50:
        topics_listbox.delete(0, 1)

# Define function to update the payload every 5 seconds
def update_payload():
    while True:
        publish_message()
        time.sleep(5)

# Create a separate thread to update the payload
payload_thread = threading.Thread(target=update_payload)
payload_thread.start()

# Subscribe to all nodes in the Sparkplug namespace
client.subscribe("spBv1.0/#")

# Define callback function for when a message is received
def on_message(client, userdata, msg):
    # Parse Sparkplug B message payload
    data = json.loads(msg.payload)

    # Get topic and message data from the received message
    topic = msg.topic
    timestamp = data['timestamp']
    dt_string = data['datetime']
    temp = data['data']['temp']
    pressure = data['data']['pressure']
    humidity = data['data']['humidity']
    device_name = data['device']['name']
    device_ip = data['device']['ip']
    device_os = data['device']['os']

    # Insert topic and payload string into listbox
    topic_string = f"Topic: {topic}\n"
    payload_string = f"Timestamp: {timestamp}\n"
    payload_string += f"Date/time: {dt_string}\n"
    payload_string += f"Temperature: {temp}\n"
    payload_string += f"Pressure: {pressure}\n"
    payload_string += f"Humidity: {humidity}\n"
    payload_string += f"Device name: {device_name}\n"
    payload_string += f"Device IP: {device_ip}\n"
    payload_string += f"Device OS: {device_os}\n"

    topics_listbox.insert(tk.END, topic_string)
    topics_listbox.insert(tk.END, payload_string)
    topics_listbox.see(tk.END)

    # Remove oldest items from listbox if necessary
    if topics_listbox.size() > 50:
        topics_listbox.delete(0, 1)

# Set up MQTT client callback for message reception
client.on_message = on_message

# Run GUI loop
root.mainloop()
