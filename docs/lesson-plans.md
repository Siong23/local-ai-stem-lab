# AI Agent Workshop - Comprehensive Course Outline & Run Sheets

This document serves as the master instructional blueprint and delivery run-sheet for the 3-session hands-on program: *Building AI Agents That Sense and Act*. 

---

## Session 1: From Chatbot to Agent (120 Mins)
**Big Idea:** An LLM predicts text; an agent pursues a goal with instructions and tools.
**Evidence of Learning:** Students can identify goal, instruction, model, tool, observation, and action.

### Session 1 Timeline

| Time | Min | Activity | Instructor Evidence / Focus |
| :--- | :--- | :--- | :--- |
| **00:00-00:05** | 5 | Welcome, teams, roles, norms | Every student has a role and a `GROUPxx` card assigned. |
| **00:05-00:15** | 10 | Hook: Chatbot vs Agent Demonstration | Students visually pinpoint the tool request step in the trace logs. |
| **00:15-00:27** | 12 | Mini-Lesson: 6-Part Mental Model | Vocabulary check: Goal, Instruction, Model, Tool, Observation, Action. |
| **00:27-00:37** | 10 | Safety, Privacy & System Reliability | Groups successfully declare one prohibited action and data item. |
| **00:37-00:52** | 15 | Prompt Lab: Fixing Ambiguity | Each group rewrites a weak prompt into a structured instruction. |
| **00:52-01:02** | 10 | Build: Model Endpoint Connection | Verify a short response is pulled from the local LM Studio instance. |
| **01:02-01:07** | 5 | *Movement Break* | Instructor runs an overarching system resource check. |
| **01:07-01:27** | 20 | Build: Add Calculator Tool to Agent | Execution of a live mathematical calculation through tool tracing. |
| **01:27-01:45** | 18 | Test Matrix: Edge Cases & Refusals | Four distinct scenarios are executed and manually recorded. |
| **01:45-01:55** | 10 | Pair Explain: Tracing the Agent Loop | Peers retell the core loop mechanics without reading notes. |
| **01:55-02:00** | 5 | Checkpoint & Exit Ticket | Flow saved as `GROUPxx-S1` and reflection submitted. |

### Critical Checkpoints & Safety Boundaries
* **The Emergency Stop:** Prior to any building, students must demonstrate they know the emergency cutoff: **Close the terminal Bridge window or physically pull the micro:bit USB cable.**
* **System Prompt Template Boundary:** Students rewrite unconstrained prompts into a structured format containing explicit `ROLE`, `GOAL`, `EVIDENCE`, `BOUNDARIES`, and `RESPONSE` guidelines.
* **Session 1 Recovery:** If the model acts but completely bypasses the calculator tool, inspect the Agent node parameters, enforce an explicit query strategy, or adjust prompt weights.

---

## Session 2: Give the Agent Senses (120 Mins)
**Big Idea:** A tool lets the agent obtain fresh evidence from the physical world.
**Evidence of Learning:** Students trace one request through Flowise, Gateway, MQTT, Bridge, USB, and back.

### Session 2 Timeline

| Time | Min | Activity | Instructor Evidence / Focus |
| :--- | :--- | :--- | :--- |
| **00:00-00:08** | 8 | Session 1 Recap & Infrastructure Check | Quick mental model validation (the 6 core vocabulary steps). |
| **00:08-00:20** | 12 | Architecture Relay Challenge | Correct layout of the 7-hop device network communication path. |
| **00:20-00:35** | 15 | Connect hardware & Fire up Device Bridge | All group bridges transition to an "Online" network status. |
| **00:35-00:52** | 17 | Direct Hardware Sensor Lab | Capture and document direct light and temperature payloads. |
| **00:52-01:00** | 8 | Controlled Variable Experiment | Light variables reflect a direct delta under covered conditions. |
| **01:00-01:05** | 5 | *Movement Break* | Instructor scans the central MQTT logs for unexpected anomalies. |
| **01:05-01:25** | 20 | Integrate `read_device_sensor` Tool | The Flowise visual agent successfully executes a sensor call. |
| **01:25-01:43** | 18 | Design a Dark-Room Evidence Rule | Three distinct physical room threshold matrices are verified. |
| **01:43-01:54** | 11 | Failure Drill & Timeout Emulation | Students distinguish an explicit error payload from a numeric `0`. |
| **01:54-02:00** | 6 | Checkpoint & Save State | Flow saved as `GROUPxx-S2` along with trace screenshots. |

### Critical Checkpoints & Safety Boundaries
* **Architecture Rules:** Students must verify that the local LLM *does not* touch the hardware directly. It requests an approved tool; software layers validate it.
* **Controlled Threshold Logic:** The sensor reading is relative (0-255). Teams must calculate their own custom `DARK_THRESHOLD` derived from physical environment observations instead of copying arbitrary templates.
* **Session 2 Recovery:** In the event of an "Access Denied" or busy port error, verify that competing Python editors or secondary background bridge scripts are fully shut down.

---

## Session 3: Let the Agent Act Safely (120 Mins)
**Big Idea:** An agent can select a bounded action and use feedback to confirm the result.
**Evidence of Learning:** Students demonstrate observe-decide-act-explain loops and discuss governance.

### Session 3 Timeline

| Time | Min | Activity | Instructor Evidence / Focus |
| :--- | :--- | :--- | :--- |
| **00:00-00:08** | 8 | Reconnect & Sensor Baseline Check | Every team confirms an active pipeline via a clean light request. |
| **00:08-00:20** | 12 | Actuation Safety Mapping | Categorization of safe built-in actions vs high-risk hardware. |
| **00:20-00:38** | 18 | Integrate `control_device` Tool | Validation of bounded screen icon changes and micro-tones. |
| **00:38-00:55** | 17 | Build Observe-Decide-Act-Explain Loop | The agent uses physical environment evidence to trigger reactions. |
| **00:55-01:00** | 5 | *Movement Break* | Global device clear and deployment workspace reset. |
| **01:00-01:07** | 7 | Final Project Challenge Brief | Core optimization rules, group mission selection, and rubric review. |
| **01:07-01:37** | 30 | Team Build, Test, & Iterate Sprint | Minimum of three test scenarios fully logged in the sheet. |
| **01:37-01:42** | 5 | Demo Preparation & Code Freeze | Flow configurations locked; execution prompt ready for review. |
| **01:42-01:58** | 16 | 10 Lightning Student Demonstrations | Strict 90-second lightning run per group following the script. |
| **01:58-02:00** | 2 | Infrastructure Teardown & Closeout | Bridge terminals terminated; hardware unplugged and inventoried. |

### Critical Checkpoints & Safety Boundaries
* **Actuation Safeguards:** Built-in display icons and short tones are allowlisted. High-voltage arrays, locks, and external motors are strictly prohibited in this environment.
* **Closed-Loop Rule:** If a diagnostic tool or structural connection drops, the agent **must not** proceed with secondary actuation choices. It must abort and report an availability error.
* **Session 3 Mastery Sign-Off:** A team successfully completes the program when their visual agent processes raw environment variables, handles dropouts cleanly, and the student team can accurately articulate the structural loop topology without claiming the LLM runs the physical hardware directly.
