# Lab 01 - Pipeline Skeleton, Configuration and the Alpaca Paper Account

Create the pipeline package and its config.yaml (universe, strategy parameters, risk limits, costs, secret names), build a validating configuration loader and a market-clock module, and run `python -m pipeline check` against the Alpaca paper account or the offline simulator.

| File | What it is |
|---|---|
| `Lab01_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab01_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `check_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (check.py, clock.py, config.py) |

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

**Run Lab 01**

```bash
python3 Lab01-alpaca-setup/check_stage.py
(same as: python -m pipeline check)
```

**The complete code**

```bash
pipeline/check.py, pipeline/clock.py, pipeline/config.py
(reference copy: Lab01-alpaca-setup/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
