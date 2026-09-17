import json
import queue
import re
import sys
import threading
import time
from pathlib import Path

import paho.mqtt.client as mqtt
import serial
from serial.tools import list_ports

APP_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
CONFIG_PATH = APP_DIR / "bridge-config.json"
with CONFIG_PATH.open("r", encoding="utf-8-sig") as handle:
    CONFIG = json.load(handle)

GROUP_ID = str(CONFIG["group_id"]).upper()
MQTT_HOST = str(CONFIG.get("mqtt_host", "192.168.50.10"))
MQTT_PORT = int(CONFIG.get("mqtt_port", 1883))
SERIAL_BAUD = int(CONFIG.get("serial_baud", 115200))

if not re.fullmatch(r"GROUP\d{2}", GROUP_ID):
    raise SystemExit("bridge-config.json must contain a group_id such as GROUP01")

def find_microbit_port():
    requested = str(CONFIG.get("serial_port", "auto"))
    if requested.lower() != "auto":
        return requested

    matches = []
    seen = []
    for port in list_ports.comports():
        seen.append(port.device)
        details = " ".join(
            str(value or "")
            for value in (port.description, port.manufacturer, port.product, port.hwid)
        ).lower()
        if port.vid == 0x0D28 or any(
            marker in details for marker in ("micro:bit", "microbit", "mbed", "daplink")
        ):
            matches.append(port.device)
    if not matches:
        ports = ", ".join(seen) if seen else "none"
        raise SystemExit(f"No micro:bit found. Detected ports: {ports}")
    print(f"Serial auto-detected: {matches[0]}")
    return matches[0]

SERIAL_PORT = find_microbit_port()
commands = queue.Queue(maxsize=20)

serial_link = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.5, write_timeout=2, rtscts=False, dsrdtr=False)
serial_link.dtr = False
serial_link.rts = False
time.sleep(2)
serial_link.reset_input_buffer()
print(f"Group: {GROUP_ID}")
print(f"Serial ready: {SERIAL_PORT} at {SERIAL_BAUD}")

def encode_command(command, request_id):
    if not re.fullmatch(r"[0-9a-f]{1,32}", request_id):
        raise ValueError("request_id must be 1-32 lowercase hexadecimal characters")
    codes = {"read_light": "L", "read_temperature": "T", "read_acceleration": "A", "read_buttons": "B", "show_icon": "I", "clear_display": "C", "play_tone": "N", "ping": "P"}
    action = command["action"]
    fields = [request_id, codes[action]]
    if action == "show_icon":
        icon = command["icon"]
        if icon not in ("HAPPY", "SAD", "YES", "NO", "HEART", "SURPRISED", "ASLEEP"):
            raise ValueError("Unsupported icon")
        fields.append(icon)
    if action == "play_tone":
        frequency, duration = command["frequency"], command["duration_ms"]
        if type(frequency) is not int or type(duration) is not int:
            raise ValueError("Tone arguments must be integers")
        if not 100 <= frequency <= 2000 or not 50 <= duration <= 2000:
            raise ValueError("Tone outside bounds")
        fields.extend([str(frequency), str(duration)])
    line = "|".join(fields).encode("ascii")
    if len(line) > 60:
        raise ValueError("Serial command too long")
    return b"~\n" + line + b"\n"

def decode_reply(line, command, request_id):
    clean_line = line.decode("ascii", errors="ignore").replace("\r", "").replace("\n", "").strip()
    fields = clean_line.split("|")
    
    if len(fields) < 3 or fields[0] != request_id:
        return None
    reply = {"request_id": request_id, "status": "ok"}
    if fields[1] == "ERR":
        return {**reply, "status": "error", "error": "micro:bit: " + fields[2]}
        
    if fields[1] != "OK":
        raise ValueError("Invalid serial status")
        
    values = fields[2:]
    action = command["action"]
    count = 3 if action == "read_acceleration" else 2 if action in ("read_buttons", "play_tone", "ping") else 1
    if len(values) != count:
        raise ValueError("Invalid serial field count")
        
    if action in ("read_light", "read_temperature"):
        unit = "level_0_255" if action == "read_light" else "celsius_approx"
        result = {"value": int(values[0]), "unit": unit}
    elif action == "read_acceleration":
        result = dict(zip(("x", "y", "z"), map(int, values)))
        result["unit"] = "milli_g_approx" 
    elif action == "read_buttons":
        result = {"a": values[0] == "1", "b": values[1] == "1"}
    elif action == "show_icon":
        result = {"shown": values[0]}
    elif action == "clear_display":
        result = {"cleared": True}
    elif action == "play_tone":
        result = {"frequency": int(values[0]), "duration_ms": int(values[1])}
    else:
        if values != ["PONG", "1.2"]:
            raise ValueError("Firmware version mismatch; reflash version 1.2")
        result = {"firmware": "1.2"}
    reply["result"] = result
    return reply

def serial_request(command, request_id):
    serial_link.write(encode_command(command, request_id))
    serial_link.flush()
    deadline = time.monotonic() + 5.0
    
    while time.monotonic() < deadline:
        if serial_link.in_waiting > 0:
            raw_line = serial_link.readline()
            if raw_line:
                reply = decode_reply(raw_line, command, request_id)
                if reply is not None:
                    return reply
        time.sleep(0.01)
    raise TimeoutError("micro:bit timeout; check firmware 1.2 and USB")

serial_link.write(b"\n~\n~\n")
serial_link.flush()
time.sleep(0.5)
serial_link.reset_input_buffer()

try:
    probe = serial_request({"action": "ping"}, "0")
    print("Firmware ready: 1.2 (text serial protocol)")
except TimeoutError:
    print("[Skip Warning] Hardware handshake probe timed out; forcibly starting the MQTT listening layer...")

def publish_status(state):
    mqtt_client.publish(
        f"ktp/{GROUP_ID}/status",
        json.dumps({"state": state, "time": int(time.time())}),
        qos=1,
        retain=True,
    )

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe(f"ktp/{GROUP_ID}/cmd", qos=1)
        publish_status("online")
        print(f"MQTT connected; subscribed to ktp/{GROUP_ID}/cmd")
    else:
        print(f"MQTT connection failed; {reason_code}")

def on_disconnect(client, userdata, flags, reason_code, properties):
    print("MQTT disconnected; retrying while this window remains open")

def on_message(client, userdata, message):
    try:
        command = json.loads(message.payload.decode("utf-8"))
        commands.put_nowait(command)
    except queue.Full:
        print("Command queue full; request dropped")
    except Exception as exc:
        print(f"Invalid MQTT command: {exc}")

def status_worker():
    while True:
        if mqtt_client.is_connected():
            publish_status("online")
        time.sleep(30)

def device_worker():
    while True:
        command = commands.get()
        request_id = command.get("request_id", "unknown")
        reply_topic = f"ktp/{GROUP_ID}/resp/{request_id}"
        try:
            response = serial_request(command, request_id)
        except Exception as exc:
            response = {"request_id": request_id, "status": "error", "error": str(exc)[:160]}
        mqtt_client.publish(reply_topic, json.dumps(response), qos=1)
        commands.task_done()

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"bridge-{GROUP_ID}")
mqtt_client.will_set(
    f"ktp/{GROUP_ID}/status",
    json.dumps({"state": "offline"}),
    qos=1,
    retain=True,
)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message

mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)

threading.Thread(target=device_worker, daemon=True).start()
threading.Thread(target=status_worker, daemon=True).start()
mqtt_client.connect_async(MQTT_HOST, MQTT_PORT, keepalive=30)

try:
    mqtt_client.loop_forever(retry_first_connection=True)
finally:
    try:
        publish_status("offline")
        mqtt_client.disconnect()
    finally:
        serial_link.close()
