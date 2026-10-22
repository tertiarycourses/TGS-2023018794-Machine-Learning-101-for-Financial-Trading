# Lab 02 - Data-Validation Stage: Cross-Check Pipeline Bars against TradingView

Read daily bars for SGX:D05 and NASDAQ:AAPL from the TradingView Data Window, record them, and build a validation stage that compares TradingView with the pipeline's raw and dividend-adjusted bars and writes a validation report.

| File | What it is |
|---|---|
| `Lab02_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab02_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `validate_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (validate.py) |

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

**Run Lab 02**

```bash
python3 Lab02-tradingview-charts/validate_stage.py
(same as: python -m pipeline validate)
```

**The complete code**

```bash
pipeline/validate.py
(reference copy: Lab02-tradingview-charts/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
