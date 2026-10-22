# Lab 03 - Ingestion Stage: Multi-Timeframe Bars, Headlines and Data Quality

Build `python -m pipeline ingest` to fetch and cache daily, weekly, monthly and hourly bars for the universe, run automated data-quality checks, ingest headlines as unstructured data, and describe the forms of data and the 3 Vs of big data.

| File | What it is |
|---|---|
| `Lab03_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab03_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `ingest_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (ingest.py) |

## How to run

Run every command from the `labs_fullcode` folder.

**Open a terminal in the labs_fullcode folder**

```bash
cd labs_fullcode
```

**Create and activate a virtual environment (once)**

```bash
python3 -m venv .venv
source .venv/bin/activate     (Windows: .venv\Scripts\activate)
```

**Install the libraries (once)**

```bash
pip install -r requirements.txt
```

**Optional: your Alpaca paper keys (leave blank to run OFFLINE)**

```bash
cp .env.example .env     (Windows: copy .env.example .env)
then paste APCA_API_KEY_ID and APCA_API_SECRET_KEY into .env
```

**Run Lab 03**

```bash
python3 Lab03-alpaca-market-data/ingest_stage.py
(same as: python -m pipeline ingest)
```

**The complete code**

```bash
pipeline/ingest.py
(reference copy: Lab03-alpaca-market-data/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
