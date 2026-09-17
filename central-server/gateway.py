import asyncio
import json
import os
import re
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Literal
 
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
 
load_dotenv()
 
MQTT_HOST = os.environ["MQTT_HOST"]
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
ALLOWED_GROUPS = {x.strip() for x in os.environ["ALLOWED_GROUPS"].split(",")}
TIMEOUT = float(os.getenv("COMMAND_TIMEOUT_SECONDS", "8"))
 
app = FastAPI(title="AI Workshop Device Gateway", version="1.1.0")
connected = threading.Event()
pending_lock = threading.Lock()
pending = {}
device_status = {}
 
 
@dataclass
class PendingRequest:
    event: threading.Event
    response: dict | None = None
 
 
class Command(BaseModel):
    action: Literal[
        "read_light", "read_temperature", "read_acceleration", "read_buttons",
        "show_icon", "clear_display", "play_tone"
    ]
    icon: Literal["HAPPY", "SAD", "YES", "NO", "HEART", "SURPRISED", "ASLEEP"] | None = None
    frequency: int | None = Field(default=None, ge=100, le=2000)
    duration_ms: int | None = Field(default=None, ge=50, le=2000)
 
 
def validate_command(command: Command):
    if command.action == "show_icon" and command.icon is None:
        raise HTTPException(422, "show_icon requires icon")
    if command.action == "play_tone":
        if command.frequency is None or command.duration_ms is None:
            raise HTTPException(422, "play_tone requires frequency and duration_ms")
 
 
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        connected.set()
        client.subscribe("ktp/+/resp/#", qos=1)
        client.subscribe("ktp/+/status", qos=1)
    else:
        connected.clear()
 
 
def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    connected.clear()
 
 
def on_message(client, userdata, message):
    parts = message.topic.split("/")
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except Exception:
        return
    if len(parts) == 3 and parts[2] == "status":
        device_status[parts[1]] = {**payload, "received_at": time.time()}
        return
    if len(parts) == 4 and parts[2] == "resp":
        request_id = parts[3]
        with pending_lock:
            item = pending.get(request_id)
            if item:
                item.response = payload
                item.event.set()
 
 
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="device-gateway")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect_async(MQTT_HOST, MQTT_PORT, keepalive=30)
client.loop_start()
 
 
@app.get("/health")
def health():
    online = sorted(
        group for group, status in device_status.items()
        if status.get("state") == "online" and time.time() - status.get("received_at", 0) < 90
    )
    return {"status": "ok", "mqtt_connected": connected.is_set(), "online_devices": online}
 
 
@app.get("/v1/devices/{group_id}/status")
def get_status(group_id: str):
    if group_id not in ALLOWED_GROUPS:
        raise HTTPException(404, "Unknown group")
    return device_status.get(group_id, {"state": "unknown"})
 
 
@app.post("/v1/devices/{group_id}/command")
async def issue_command(group_id: str, command: Command):
    if group_id not in ALLOWED_GROUPS or not re.fullmatch(r"GROUP\d{2}", group_id):
        raise HTTPException(404, "Unknown group")
    if not connected.is_set():
        raise HTTPException(503, "MQTT broker unavailable")
    validate_command(command)
 
    request_id = uuid.uuid4().hex
    item = PendingRequest(event=threading.Event())
    with pending_lock:
        pending[request_id] = item
 
    payload = {"request_id": request_id, **command.model_dump(exclude_none=True)}
    info = client.publish(f"ktp/{group_id}/cmd", json.dumps(payload), qos=1)
    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        with pending_lock:
            pending.pop(request_id, None)
        raise HTTPException(503, "Could not publish command")
 
    completed = await asyncio.to_thread(item.event.wait, TIMEOUT)
    with pending_lock:
        pending.pop(request_id, None)
    if not completed or item.response is None:
        raise HTTPException(504, f"Device {group_id} did not respond")
 
    response = item.response
    if response.get("status") != "ok":
        raise HTTPException(502, response.get("error", "Device command failed"))
    return {"group_id": group_id, "action": command.action, **response}
