# Lab 15 - Backtest-Engine Stage: Cost Models, Execution Timing and Break-Even

Build pipeline/backtest.py around the common backtester: run any library signal under every cost scenario (and a custom one), break the cost into commission, spread, slippage and regulatory fees, find each strategy's break-even cost and test next-open versus next-close execution.

| File | What it is |
|---|---|
| `Lab15_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab15_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `backtest_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (backtest.py) |

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

**Run Lab 15**

```bash
python3 Lab15-trading-costs/backtest_stage.py
(same as: python -m pipeline backtest)
```

**The complete code**

```bash
pipeline/backtest.py
(reference copy: Lab15-trading-costs/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
