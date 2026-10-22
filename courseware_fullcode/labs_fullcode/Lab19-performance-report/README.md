# Lab 19 - Monitoring and Reporting Stage: Automated Tearsheet and Backtest-vs-Forward Report

Build `python -m pipeline report` to compare the research backtest with the runner's forward-test logs, run monitoring checks with thresholds, and generate a tearsheet and a markdown report with data-driven insights and a recommendation.

| File | What it is |
|---|---|
| `Lab19_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab19_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `report_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (report.py) |

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

**Run Lab 19**

```bash
python3 Lab19-performance-report/report_stage.py
(same as: python -m pipeline report)
```

**The complete code**

```bash
pipeline/report.py
(reference copy: Lab19-performance-report/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
