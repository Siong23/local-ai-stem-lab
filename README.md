# Building AI Agents That Sense and Act 
> A 3-session knowledge-transfer program for senior secondary students to build low-voltage physical AI agents.

This repository contains the complete production-grade infrastructure code, local edge AI gateway, device bridges, and micro:bit firmware version 1.2 for the AI Agent Classroom Program.

## Program Architecture Overview
The system enables a visual LLM orchestration layer (Flowise) to sense the physical environment and take safe, bounded actions via an isolated deployment framework.

```text
[Flowise Agent UI] 
       │ (HTTP tool call)
       ▼
[FastAPI Device Gateway] (Port 8000)
       │ (Local MQTT Broker: Port 1883)
       ▼
[Windows Device Bridge] (Group Laptops)
       │ (USB Serial / Pipe text protocol)
       ▼
[BBC micro:bit V2 Firmware v1.2]
```

## Repository Structure & Components
* `central-server/`: Local FastAPI gateway, environment variable configs, and Flowise custom JS tools (light/temp sensors & actuators).
* `group-laptop/`: Lightweight standalone PyInstaller-ready python bridge for Windows client laptops.
* `hardware-firmware/`: Tailored MicroPython runtime for micro:bit V2 handling ASCII stream frames.
* `docs/`: Automated environment verification suites (`verify_stack.py`) and standard lesson run-sheets.

## Networking Prerequisite (IP Configuration)
Before deploying the classroom stack, you **must substitute the reference IP address (`192.168.50.10` / `192.168.0.x`) with your own central server's actual local IP address** across the following initialization files:
1. **Gateway Environment:** Update `MQTT_HOST` in `central-server/gateway/.env`
2. **Flowise JavaScript Tools:** Update `gateway_url` inside the script logic for both sensor and control nodes.
3. **Group Configurations:** Update `mqtt_host` in each group's local client `bridge-config.json` before distributing the client application bundle to the student laptops.

## Rapid Classroom Deployment (v1.2 Protocol)
1. **Host Verification:** Run `python docs/verify_stack.py` to ensure local MQTT and FastAPI gates are fully accessible.
2. **Client Startup:** Connect the assigned micro:bit board, navigate to `group-laptop/device-bridge/` and execute `Start Bridge.bat`.
3. **Safety Control:** Close the bridge window or disconnect the USB interface to trigger an instant emergency hardware lock.

---
*Maintained under isolated workshop specifications. Internet connectivity is not required during delivery.*
