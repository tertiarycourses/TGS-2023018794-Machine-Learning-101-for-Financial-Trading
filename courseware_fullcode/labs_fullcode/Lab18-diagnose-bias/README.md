# Lab 18 - Diagnostics Stage: Automated Bias Checks before Go-Live

Build `python -m pipeline diagnose` to run automated look-ahead (features and execution), cost-drag, overfitting and survivorship checks on any strategy and on the junior quant's exhibit, and write a PASS / WARN / FAIL report with a go-live verdict.

| File | What it is |
|---|---|
| `Lab18_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab18_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `diagnose_stage.py` | Runs this lab's pipeline stage |
| `buggy_backtest.py` | Extra script used in this lab |
| `solution/` | Reference copy of the complete code (diagnose.py) |

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

**Run Lab 18**

```bash
python3 Lab18-diagnose-bias/diagnose_stage.py
(same as: python -m pipeline diagnose)
```

**Also in this lab: buggy_backtest.py**

```bash
python3 Lab18-diagnose-bias/buggy_backtest.py
```

**The complete code**

```bash
pipeline/diagnose.py
(reference copy: Lab18-diagnose-bias/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
