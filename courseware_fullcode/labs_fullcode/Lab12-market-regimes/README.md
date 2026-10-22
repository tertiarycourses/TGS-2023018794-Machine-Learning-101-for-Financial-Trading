# Lab 12 - Regime-Filter Stage: PCA and K-Means as a Gate on the Signals

Build pipeline/regime.py: PCA on the universe's returns, K-means regimes on backward-looking SPY features, walk-forward regime labels, and a gate that forces signals flat in the stress regime, evaluated after costs.

| File | What it is |
|---|---|
| `Lab12_Instructions.pdf` | The lab manual: scenario, steps, checks and debrief |
| `Lab12_Prompts.pdf` | Every step with its AI prompt, ready to copy |
| `regime_stage.py` | Runs this lab's pipeline stage |
| `solution/` | Reference copy of the complete code (regime.py) |

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

**Run Lab 12**

```bash
python3 Lab12-market-regimes/regime_stage.py
(same as: python -m pipeline regime)
```

**The complete code**

```bash
pipeline/regime.py
(reference copy: Lab12-market-regimes/solution/)
```

**Outputs**

```bash
_outputs/  (charts, CSV files and reports written by the stage)
```

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.
