# Lab 06 - Strategy Prototype: TradingView Strategy Tester, Paper Trading from the Chart and Pipeline Reconciliation

Configure a Pine Script v6 strategy with costs, read the Strategy Tester, build `python -m pipeline reconcile` to check the Pine settings and reproduce the results, and place and manage paper trades from the chart with TradingView Paper Trading (and optionally an Alpaca paper account).

| File | What it is |
|---|---|
| `Lab06_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab06_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `reconcile_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (reconcile.py) |

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

**Run Lab 06**

```bash
python3 Lab06-pine-strategy-tester/reconcile_stage.py
(same as: python -m pipeline reconcile)
```

**The complete code**

```bash
pipeline/reconcile.py
(reference copy: Lab06-pine-strategy-tester/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
