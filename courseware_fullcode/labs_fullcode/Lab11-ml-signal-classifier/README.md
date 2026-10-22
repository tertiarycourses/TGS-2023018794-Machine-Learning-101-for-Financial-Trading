# Lab 11 - ML-Signal Stage: a Walk-Forward Classifier from Probability to Position

Build pipeline/ml.py: engineer causal features, train logistic regression, random forest and XGBoost with walk-forward TimeSeriesSplit validation, turn P(up) into a target position and backtest it after costs.

| File | What it is |
|---|---|
| `Lab11_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab11_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `ml_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (ml.py) |

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

**Run Lab 11**

```bash
python3 Lab11-ml-signal-classifier/ml_stage.py
(same as: python -m pipeline ml)
```

**The complete code**

```bash
pipeline/ml.py
(reference copy: Lab11-ml-signal-classifier/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
