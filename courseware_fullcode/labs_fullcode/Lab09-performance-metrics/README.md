# Lab 09 - Evaluation Stage: Performance and Risk Metrics with a Benchmark Table

Build `python -m pipeline evaluate` to compute total return, CAGR, volatility, Sharpe, Sortino, maximum drawdown, Calmar, win rate, profit factor, exposure, turnover, alpha and beta for every signal against a buy-and-hold benchmark, and interpret the ranking.

| File | What it is |
|---|---|
| `Lab09_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab09_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `evaluate_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (evaluate.py) |

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

**Run Lab 09**

```bash
python3 Lab09-performance-metrics/evaluate_stage.py
(same as: python -m pipeline evaluate)
```

**The complete code**

```bash
pipeline/evaluate.py
(reference copy: Lab09-performance-metrics/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
