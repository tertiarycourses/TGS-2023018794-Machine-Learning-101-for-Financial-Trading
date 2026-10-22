# Lab 07 - Signal Stage: a Library of Trend, Mean-Reversion, Momentum and Breakout Signals

Build pipeline/signals.py with trend, mean-reversion, momentum and breakout signals that return target positions with next-bar alignment, a registry, an automated look-ahead test and a universe target file for the execution stage.

| File | What it is |
|---|---|
| `Lab07_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab07_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `signals_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (signals.py) |

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

**Run Lab 07**

```bash
python3 Lab07-technical-indicators/signals_stage.py
(same as: python -m pipeline signals)
```

**The complete code**

```bash
pipeline/signals.py
(reference copy: Lab07-technical-indicators/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
