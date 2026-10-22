# Lab 14 - Pairs Stage: a Hedged, Market-Neutral Statistical-Arbitrage Sleeve

Build pipeline/pairs.py: screen pairs with the Engle-Granger cointegration test, estimate the hedge ratio, trade the spread z-score out of sample with next-bar execution and costs on both legs, confirm market neutrality and output leg targets.

| File | What it is |
|---|---|
| `Lab14_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab14_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `pairs_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (pairs.py) |

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

**Run Lab 14**

```bash
python3 Lab14-pairs-trading/pairs_stage.py
(same as: python -m pipeline pairs)
```

**The complete code**

```bash
pipeline/pairs.py
(reference copy: Lab14-pairs-trading/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
