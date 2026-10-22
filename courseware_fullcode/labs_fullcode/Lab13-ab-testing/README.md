# Lab 13 - A/B-Test Stage: a Statistical Decision before Capital Moves

Build `python -m pipeline abtest` to compare any two library signals with a Welch t-test, a paired t-test and a block-bootstrap confidence interval for the Sharpe difference, and to record an accept or reject decision with a multiple-testing caution.

| File | What it is |
|---|---|
| `Lab13_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab13_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `abtest_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (abtest.py) |

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

**Run Lab 13**

```bash
python3 Lab13-ab-testing/abtest_stage.py
(same as: python -m pipeline abtest)
```

**The complete code**

```bash
pipeline/abtest.py
(reference copy: Lab13-ab-testing/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
