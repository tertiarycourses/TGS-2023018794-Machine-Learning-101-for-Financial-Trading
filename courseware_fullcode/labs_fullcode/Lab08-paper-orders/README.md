# Lab 08 - Execution Stage: an Order Manager that Trades the Paper Account in Any Session

Build pipeline/execution.py: a session-aware, idempotent order manager that sizes orders from target weights, sends market, extended-hours limit, GTC-queued or bracket PAPER orders, polls their lifecycle, cancels protective legs before exits, and falls back safely when an order is rejected.

| File | What it is |
|---|---|
| `Lab08_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab08_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `execution_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (execution.py) |

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

**Run Lab 08**

```bash
python3 Lab08-paper-orders/execution_stage.py
(same as: python -m pipeline execute)
```

**The complete code**

```bash
pipeline/execution.py
(reference copy: Lab08-paper-orders/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
