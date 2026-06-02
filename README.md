# 📡 LTE & GSM Automatic Spectrum Scanner & Wiki Ingestion System

An automated, passive LTE & GSM cellular network monitoring and intelligence-gathering system using SDR hardware (**LimeSDR Mini 2.0** / **Ettus USRP B205-mini**) to capture and decode 3GPP parameters (LTE MIB/SIBs & GSM L3 GSMTAP broadcasts), map cell topologies, and compile findings into an interactive, cross-linked **Obsidian Wiki Knowledge Base**.

---

## 🚀 Key Features

*   **Passive LTE Cell Discovery**: Captures MIB, SIB1, SIB2, SIB3, SIB4, SIB5, SIB6, and SIB7 broadcasts over-the-air with zero network trace.
*   **Passive GSM Cell Discovery**: Scans GSM900/DCS1800 bands, decodes real-time Layer 3 Radio Resource packets (SI3, SI2, SI2quater) over loopback UDP 4729 (GSMTAP stream).
*   **Turkish Operator Mapping (PLMN/MNC)**: Decodes PLMN codes to auto-identify and estimate Turkish network operators:
    *   `286-01` $\implies$ **Turkcell**
    *   `286-02` $\implies$ **Vodafone**
    *   `286-03` $\implies$ **Türk Telekom**
*   **Dual-Layer SI2quater Decoding**: Combines concurrent real-time JSON `tshark` stream parsing with offline PCAP fallback decoders to capture 3G/4G inter-RAT (EARFCN/UARFCN) neighbor relations from GSM base stations.
*   **Dual-SDR Dynamic Routing**: Automatically splits scanning queues based on frequency limits:
    *   **High-Band ($\ge$ 1500 MHz)**: Routed to LimeSDR LNAH port (LTE high bands & GSM DCS1800).
    *   **Low-Band ($<$ 1500 MHz)**: Routed to LimeSDR LNAW port (LTE low bands & GSM GSM900).
*   **Real-time CLI Dashboards**: Renders beautiful, ANSI-colored tables detailing Cell Inventories, LTE neighbor maps, and GSM BA lists.
*   **Obsidian Wiki Compiler**: Automatically distills raw cellular outputs into highly organized markdown pages (`cells/`, `bands/`, `references/`, `concepts/`) with cross-linked network topologies and interactive HTML network graphs.
*   **Scalable Microservice Architecture**: Decoupled hardware layer with the containerized **`hw-worker-sdr`** gRPC/ZMQ Python worker, featuring a joint busy kilit mechanism for secure SDR sharing.

---

## 📊 System Architecture

The core orchestrator controls hardware capabilities, parses low-level signals, and publishes them for high-fidelity database persistence and Obsidian Wiki visualization.

```
+-------------------------------------------------------------+
|                        Tauri GUI Frontend                   |
|                   (React / TypeScript Desktop App)          |
|------------------------------+------------------------------+
                               | (IPC / WebSocket)
                               v
+-------------------------------------------------------------+
|                          Go Backend                         |
|                 (Central Orchestrator Core)                 |
|--------------+-------------------------------+--------------+
               |                               ^
               | (gRPC Control Plane)          | (ZMQ PUB/SUB Data Plane)
               | SDRWorkerService              | sdr_{serial}_scan_progress
               v                               |
+----------------------------------------------+--------------+
|                     hw-worker-sdr Instance                  |
|                 (SDR Hardware Python Worker)                |
|  +-------------------------------------------------------+  |
|  |           srsue (srsRAN direct subprocess)            |  |
|  |             gr-gsm (GSMTAP UDP 4729 Stream)           |  |
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
├── hw-worker-sdr/            # [REPOSITORY] Containerized gRPC/ZMQ SDR Hardware Worker (LTE & GSM)
├── gsm-neighbor-scanner/     # Standalone GSM scan client orchestrator and CLI tools
│   ├── gsm_scan.py           # GSM full-band and targeted CLI scanner (interacts with gRPC worker)
│   └── scripts/
│       └── gsm_wiki_ingest_pipeline.py # Auto-wiki engine for GSM tarama logs & cellular nodes
├── obsidian-lte-wiki/        # The compiled Unified Obsidian Knowledge Base Vault
│   ├── cells/                # Note-per-cell with full SIB properties & reselection links (LTE & GSM)
│   ├── bands/                # LTE & GSM frequency band classifications
│   ├── references/           # 3GPP reference & frequency tables
│   ├── concepts/             # Mathematical formulas, EARFCN/ARFCN converting pages
│   └── logs/                 # Historic campaign scan reports (LTE campaigns & GSM Tarama Logs)
├── lte-sib-parser/           # Low-level srsRAN parser & SQLite dbparsers scripts
├── scan.py                   # High-fidelity LTE CLI automatic scan orchestrator
├── .skills/                  # Controlled custom AI skills (LTE & GSM specific agents)
├── hw-worker-sdr-handoff.md  # Comprehensive developer specification spec sheet
└── README.md                 # This file
```

---

## 🛠️ Getting Started & CLI Scanning

### Prerequisites
Make sure your LimeSDR Mini 2.0 or USRP B205 is connected to the USB 3.0 port and the UDEV rules are successfully loaded.

### 1. Direct LTE CLI Scanning
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

### 2. Direct GSM CLI Scanning
Run the gRPC-controlled GSM CLI orchestrator tool:
```bash
cd gsm-neighbor-scanner

# Scan full GSM900 band (automatic grgsm_scanner)
python3 gsm_scan.py --band GSM900

# Targeted scan on specific ARFCNs with 15s capture loops (livemon + tshark JSON/PCAP dual-parser)
python3 gsm_scan.py "60 48 120"
```

---

## 📖 Opening the Obsidian LTE & GSM Wiki

To navigate the cross-linked network topologies, GSM-to-LTE inter-RAT relations, and cell structures:
1. Open the **Obsidian** app.
2. Select **"Open folder as vault"**.
3. Choose the directory: `/home/mobsec/Desktop/netmon/obsidian-lte-wiki`.
4. Browse the graph view to explore interactive node structures showing unidirectional/bidirectional LTE carrier handoffs and inter-RAT GSM-to-LTE neighbor paths!

---

## 🛡️ License & Disclaimer
This project is built purely for mobile security research, network optimization, and educational purposes. Always ensure you possess the required spectral permits and clearances in your jurisdiction before operating SDR receivers.
