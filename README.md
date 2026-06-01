# 📡 LTE Automatic Spectrum Scanner & Wiki Ingestion System

An automated, passive LTE cellular network monitoring and intelligence-gathering system using SDR hardware (**LimeSDR Mini 2.0** / **Ettus USRP B205-mini**) to capture and decode 3GPP Master Information Block (MIB) & System Information Blocks (SIB1-7) parameters, map cell topologies, and compile findings into an interactive, cross-linked **Obsidian Wiki Knowledge Base**.

---

## 🚀 Key Features

*   **Passive Cell Discovery**: Captures MIB, SIB1, SIB2, SIB3, SIB4, SIB5, SIB6, and SIB7 broadcasts over-the-air with zero network trace.
*   **Carrier Mapping (TR)**: Decodes PLMN codes to auto-identify Turkish network operators:
    *   `286-01` $\implies$ **Turkcell**
    *   `286-02` $\implies$ **Vodafone**
    *   `286-03` $\implies$ **Türk Telekom**
*   **Dual-SDR Dynamic Routing**: Automatically splits scanning queues based on frequency limits:
    *   **High-Band ($\ge$ 1500 MHz)**: Routed to LimeSDR LNAH port.
    *   **Low-Band ($<$ 1500 MHz)**: Routed to LimeSDR LNAW port.
*   **Real-time CLI Dashboard**: Renders beautiful, ANSI-colored tables detailing Cell Inventories, SIB5/SIB6/SIB7 inter-frequency neighbors, and reselection priorities.
*   **Obsidian Wiki Compiler**: Automatically distills raw cellular outputs into highly organized markdown pages (`cells/`, `bands/`, `references/`, `concepts/`) with cross-linked network topologies and interactive HTML network graphs.
*   **Scalable Microservice Architecture**: Fully decoupled donanım layer with the containerized **`hw-worker-sdr`** gRPC/ZMQ Python worker.

---

## 📊 System Architecture

The core scanner orchestrates hardware capabilities, parses low-level signals, and publishes them for high-fidelity database persistence and UI visualization.

```
+-------------------------------------------------------------+
|                        Tauri GUI Frontend                   |
|                   (React / TypeScript Desktop App)          |
+------------------------------+------------------------------+
                               | (IPC / WebSocket)
                               v
+-------------------------------------------------------------+
|                          Go Backend                         |
|                 (Central Orchestrator Core)                 |
+--------------+-------------------------------+--------------+
               |                               ^
               | (gRPC Control Plane)          | (ZMQ PUB/SUB Data Plane)
               | SDRWorkerService              | sdr_{serial}_scan_progress
               v                               |
+----------------------------------------------+--------------+
|                     hw-worker-sdr Instance                  |
|                 (SDR Hardware Python Worker)                |
|  +-------------------------------------------------------+  |
|  |           srsue (srsRAN direct subprocess)            |  |
|  |                   (RF Frontend & SIBs)                |  |
|  +---------------------------+---------------------------+  |
|                              | Writes results              |
|                              v                             |
|  +-------------------------------------------------------+  |
|  |             SQLite DB (/vol/output/scan_*.db)         |  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
                               |
                        Go Core imports & persists
                               v
+-------------------------------------------------------------+
|                        ClickHouse DB                        |
|                  (Historical Analytics Database)            |
+-------------------------------------------------------------+
```

---

## 📂 Project Structure

```
netmon/
├── hw-worker-sdr/            # [REPOSTORY] Containerized gRPC/ZMQ SDR Hardware Worker
├── obsidian-lte-wiki/        # The compiled Obsidian Knowledge Base Vault
│   ├── cells/                # Note-per-cell with full SIB properties & reselection links
│   ├── bands/                # LTE frequency band classifications
│   ├── references/           # 3GPP TS 36.101 reference & frequency tables
│   ├── concepts/             # Mathematical formulas, EARFCN converting pages
│   └── logs/                 # Historic campaign scan reports
├── lte-sib-parser/           # Low-level srsRAN parser & SQLite dbparsers scripts
├── scan.py                   # High-fidelity CLI automatic scan orchestrator
├── hw-worker-sdr-handoff.md  # Comprehensive developer specification spec sheet
└── README.md                 # This file
```

---

## 🛠️ Getting Started & CLI Scanning

### Prerequisites
Make sure your LimeSDR Mini 2.0 or USRP B205 is connected to the USB 3.0 port and the UDEV rules are successfully loaded.

### 1. Launching a Direct CLI Passive Scan
Run the main orchestrator script with your target EARFCN queue:
```bash
# Scan Turkcell Band 1 (100) and Band 20 (6400)
python3 scan.py "100 6400"
```

During execution, the scanner provides real-time progress of MIB/SIB acquisition:
```
[1/2] EARFCN 100 taraniyor... ✅ MIB ✅ SIB1 ✅ SIB5 (5 komşu bulundu)
[2/2] EARFCN 6400 taraniyor... ✅ MIB ✅ SIB1 ✅ SIB5 (3 komşu bulundu)
```

At campaign completion, the script generates ANSI-colored tables on the CLI and exports raw data to SQLite and Obsidian.

---

## 📖 Opening the Obsidian LTE Wiki

To navigate the cross-linked network topologies and visual cell relationships:
1. Open the **Obsidian** app.
2. Select **"Open folder as vault"**.
3. Choose the directory: `/home/mobsec/Desktop/netmon/obsidian-lte-wiki`.
4. Browse the graph view to explore interactive node structures showing unidirectional/bidirectional LTE carrier handoffs!

---

## 🛡️ License & Disclaimer
This project is built purely for mobile security research, network optimization, and educational purposes. Always ensure you possess the required spectral permits and clearances in your jurisdiction before operating SDR receivers.
