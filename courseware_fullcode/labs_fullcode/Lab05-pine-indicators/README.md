# Lab 05 - Indicator Stage: Pine Script v6 Indicators and their Python Twins

Add the desk's Pine Script v6 indicators to a TradingView chart, build pipeline/indicators.py with twins of ta.ema, ta.sma, ta.rsi, ta.bb, ta.atr, ta.macd, ta.crossover and ta.crossunder, and cross-check the values against the TradingView Data Window.

| File | What it is |
|---|---|
| `Lab05_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab05_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `indicators_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (indicators.py) |

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

**Run Lab 05**

```bash
python3 Lab05-pine-indicators/indicators_stage.py
(same as: python -m pipeline indicators)
```

**The complete code**

```bash
pipeline/indicators.py
(reference copy: Lab05-pine-indicators/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
