# Lab 17 - Event-Driven Automation: TradingView Webhook to Signal, Risk and Execution

Build pipeline/webhook.py: a webhook receiver that turns TradingView alert JSON into a pipeline decision (validation -> signal -> risk -> execution), test it with a local alert simulator and a self-test, and configure a real TradingView strategy alert.

| File | What it is |
|---|---|
| `Lab17_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab17_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `webhook_stage.py` | Runs this lab's pipeline stage |
| `send_test_alert.py` | Extra script used in this lab |
| `solution/` | Reference copy of the complete code (webhook.py) |

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

**Run Lab 17**

```bash
python3 Lab17-tradingview-webhook/webhook_stage.py
(same as: python -m pipeline webhook)
```

**Also in this lab: send_test_alert.py**

```bash
python3 Lab17-tradingview-webhook/send_test_alert.py
```

**The complete code**

```bash
pipeline/webhook.py
(reference copy: Lab17-tradingview-webhook/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
