# Central Server: Flowise AI Setup & Configuration

This guide covers the step-by-step setup, configuration, and model credential injection for the Flowise instance on the central workshop server (`192.168.50.10`).

---

## Prerequisites & System Environment
Ensure you have **Node.js 20 LTS** installed on your Ubuntu 24.04 server before executing the initialization suite.

```bash
# Verify base environment packages
node --version     # Expected output: v20.x.x
npm --version      # Expected output: a structural version number
```

---

## Step 1: Global Installation & Workspace Creation
Execute the following instructions to spin up the server environment directories and securely bound the application instance.

```bash
# Create local application and data persistent directory paths
sudo mkdir -p /opt/ai-workshop/flowise/data
sudo chown -R "$USER":"$USER" /opt/ai-workshop/flowise
cd /opt/ai-workshop/flowise

# Install Flowise globally via npm node packager
npm install -g flowise
```

---

## Step 2: Environmental Sandboxing (`.env` Setup)
Create a `.env` configuration file inside `/opt/ai-workshop/flowise/.env` to configure network policies, block unauthorized external dependencies, and set security credentials:

```ini
PORT=3000
FLOWISE_USERNAME=instructor
FLOWISE_PASSWORD=<YOUR_SECURE_CLASSROOM_PASSWORD>
DATABASE_TYPE=sqlite
DATABASE_PATH=/opt/ai-workshop/flowise/data
SECRETKEY_PATH=/opt/ai-workshop/flowise/data
LOG_PATH=/opt/ai-workshop/flowise/data/logs

# CORS policy limits: Update with your exact server IP address
CORS_ORIGINS=http://192.168.50.10:3000
IFRAME_ORIGINS=http://192.168.50.10:3000

# Security setting: Block unreviewed dynamic community plugins
SHOW_COMMUNITY_NODES=false
```

---

## Step 3: Booting Up the Pipeline
To activate the server pipeline and initialize variables using the variables file, run the following workspace tasks:

```bash
cd /opt/ai-workshop/flowise
set -a
source .env
set +a

# Fire up Flowise framework
flowise start
```
*Once running, navigate your terminal browser to `http://192.168.50.10:3000` to access the visual workspace dashboard.*

---

## Step 4: Connecting the Local LLM Endpoint (LM Studio)
To let Flowise talk to the local hardware model without hitting cloud services, register the following parameters inside the UI framework:

1. **Create Credentials:** Navigate to **Credentials** ➡️ **Create New** ➡️ Select **OpenAI-Compatible Chat Model**.
   * **Name:** `LM-STUDIO-LOCAL`
   * **API Key:** `lm-studio` (Non-secret fallback placeholder required by the interface node).
2. **Configure ChatOpenAI Node:** Drag a custom OpenAI chat wrapper onto your graph and update its connection string configuration parameters:
   * **Base URL:** `http://100.117.90.5:1234/v1` *(Points directly to the host container loopback layer)*.
   * **Model Name:** qwen/qwen3.8-27b .
   * **Temperature:** `0.1` (Forces rigorous, predictable decision rules instead of creative hallucination).
   * **Max Output Tokens:** `160` (Caps runtime context for fast local edge iteration processing).

---

## Step 5: Global Flowise Variables Mapping
To automate group routing dynamically without duplicating massive logic forks, create the following core parameters inside Flowise **Variables Dashboard**:

| Variable Key | Assigned Reference Value | Operational Vision Bound |
| :--- | :--- | :--- |
| `gateway_url` | `http://127.0.0.1:8000` | Gateway physical endpoint destination loopback path. |
| `group_id` | `GROUP01` | Group tag identification mapping (Update manually per dynamic graph duplicate fork). |

---
⚠️ **Docker Container Deployment Warning:** If you subsequently package this pipeline workspace into isolated Docker instances, loopback strings like `127.0.0.1` will look inside the container itself instead of the root machine. Adjust backend target paths to `host.docker.internal` or active docker host bridge gateways as necessary.
