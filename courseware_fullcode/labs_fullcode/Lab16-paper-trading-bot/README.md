# Lab 16 - Automation Stage: a Scheduled, Risk-Checked Forward Test and Live Paper Trading

Build pipeline/risk.py and pipeline/runner.py: `python -m pipeline run --once | --loop` with the market clock, risk checks, kill switch and trade log; run a 2025 forward test; run the strategy live on the paper account for a few cycles; and schedule it with cron, launchd or Windows Task Scheduler.

| File | What it is |
|---|---|
| `Lab16_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab16_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `run_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (risk.py, runner.py) |

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

**Run Lab 16**

```bash
python3 Lab16-paper-trading-bot/run_stage.py
(same as: python -m pipeline run)
```

**The complete code**

```bash
pipeline/risk.py, pipeline/runner.py
(reference copy: Lab16-paper-trading-bot/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
