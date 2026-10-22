# Lab 20 - Capstone: One Command Runs the Pipeline End to End, with an Agentic Layer and Human Approval

Build pipeline/agents.py (analyst, researcher, trader and risk agents; rule-based by default, Claude optional) and pipeline/e2e.py (`python -m pipeline e2e`) that runs every stage in order with gates, then evaluate the pipeline and the role of human oversight.

| File | What it is |
|---|---|
| `Lab20_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab20_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `e2e_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (agents.py, e2e.py) |

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

**Run Lab 20**

```bash
python3 Lab20-agentic-capstone/e2e_stage.py
(same as: python -m pipeline e2e)
```

**The complete code**

```bash
pipeline/agents.py, pipeline/e2e.py
(reference copy: Lab20-agentic-capstone/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
