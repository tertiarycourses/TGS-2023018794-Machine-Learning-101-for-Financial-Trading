# Lab 04 - Hypothesis Stage: from a Written Card to an Automated Statistical Test

Write a falsifiable hypothesis card in YAML (H1, H0, signal known at the close, outcome, test, decision rule, big-data use case) and build `python -m pipeline hypothesis` to test it with a Welch t-test, a bootstrap confidence interval and a robustness grid.

| File | What it is |
|---|---|
| `Lab04_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab04_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `hypothesis_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (hypothesis.py) |

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

**Run Lab 04**

```bash
python3 Lab04-trading-hypothesis/hypothesis_stage.py
(same as: python -m pipeline hypothesis)
```

**The complete code**

```bash
pipeline/hypothesis.py
(reference copy: Lab04-trading-hypothesis/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
