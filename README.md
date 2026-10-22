# Machine Learning 101 for Financial Trading

A hands-on IBF-accredited course on quant and algorithmic stock trading: learners turn trading ideas into testable hypotheses, model them with machine learning, backtest them with realistic costs and run them as an automated paper-trading pipeline on Alpaca and TradingView - with no coding required: the default low-code edition runs every lab in the course's Trading Simulator.

| Course detail | Information |
|---|---|
| Course code | `TGS-2023018794` |
| Programme | IBF-STS accredited (non-WSQ) |
| Skills Framework | FSE-DAT-3019-1.1 Data Analytics and Computational Modelling, Proficiency Level 3 |
| Duration | 2 days, 16 hours (14 hours training + 2 hours assessment) |
| Registration | [View course details and register](https://www.tertiarycourses.com.sg/ibf-machine-learning-101-for-financial-trading.html) |
| Funding | Up to 70% IBF-STS funding for eligible participants (funding valid 8 Feb 2023 to 7 Feb 2028). Eligibility and terms apply. |

## About the course

Algorithms place most orders in today's equity markets, and machine learning and agentic AI are changing how trading ideas are found, tested and executed. The course opens with quant success stories and the evolution of quant - from Thorp and Renaissance through statistical arbitrage to high-frequency trading - and the paradigm shift in which AI now writes the code while the quant owns the hypothesis, the algorithm, the testing and the risk. Learners classify and use the main trading algorithms, build indicators and strategies on TradingView, train and A/B test machine-learning signals, build a hedged pairs-trading strategy, and run an end-to-end, automated pipeline that backtests with costs, forward-tests with automatic paper orders on Alpaca, diagnoses biases and reports performance. No real money is used.

## Learning outcomes

- **LO1** - Develop hypotheses for implementing data analytics and computational modelling activities in algorithmic trading, and identify possible big data applications across the forms of data within financial services.
- **LO2** - Identify appropriate statistical algorithms and data models to test trading hypotheses, and use appropriate analytics platforms, analytical tools and statistical methods given specific analytics and reporting requirements.
- **LO3** - Conduct statistical modelling of market data with machine learning models to derive patterns and solutions, and perform A/B testing of trading strategies based on different hypotheses.
- **LO4** - Perform coding and configuration of an automated trading program based on selected models or algorithms, conduct tests on its actions and outcomes, diagnose unintended outcomes, and draw insights from the results to support decisions and report accordingly.

## Topics covered

1. **Foundations of Quant and Algorithmic Trading: From Thorp to AI Agents** (Day 1, Labs 1-4) - Quant Success Stories: What Systematic Trading Has Achieved; The Evolution of Quant: From Thorp and Renaissance to High-Frequency Trading; The Paradigm Shift from Machine Learning to LLMs, and Its Impact on Quant; Agentic AI versus AI Agents in Trading, and Multi-Agent Trading Systems; Forms of Data within Financial Services and Big Data Applications in Trading; Developing Hypotheses for Quant and Algorithmic Trading Models.
2. **Technical Indicators, Trading Strategies and Metrics with TradingView and Alpaca** (Day 1, Labs 5-9) - Technical Indicators: Trend, Momentum, Volatility and Volume; Classification of Algorithmic Trading and Quant Algorithms; Analytics Platforms and Tools: TradingView versus Alpaca, and Python; Coding Languages for Algorithms and Signals, and Order Placement; Performance and Risk Metric Definitions.
3. **Machine Learning Models, Statistical Modelling and A/B Testing for Trading Signals** (Day 2, Labs 10-14) - Types of Statistical Analyses, Data Models, Algorithms and Computational Methods; Supervised Learning Models for Trading Signals; Unsupervised Learning: Clustering and PCA for Market Regimes; Statistical Modelling Techniques for Financial Time Series; A/B Testing Trading Strategies; Pairs Trading: Statistical Arbitrage as a Hedging Algorithm.
4. **Building an End-to-End Algorithmic Trading Pipeline: Backtest, Forward Test and Performance Analysis** (Day 2, Labs 15-20) - Architecture of an End-to-End Algorithmic Trading Pipeline; Backtesting with Realistic Trading Costs; Forward Testing with Automated Paper Trading; Potential Reasons for Unintended Outcomes and How to Diagnose Them; Performance Analysis, Insights and Reporting.

## Two editions

| Edition | Who it is for | Labs |
|---|---|---|
| **Low code (default for learners)** - [`courseware_lowcode/`](courseware_lowcode/) | The IBF course as delivered in class. No coding: every lab is done in the Trading Simulator, and an optional [Prompt Library](courseware_lowcode/labs_lowcode/Prompt_Library.md) gives one AI prompt per lab for learners who want the code generated for them. | [`labs_lowcode/`](courseware_lowcode/labs_lowcode/) - one instruction PDF per lab |
| Full code (optional) - [`courseware_fullcode/`](courseware_fullcode/) | Supplementary edition for learners who want to write and run the Python themselves. Each lab is a simulator step followed by the same pipeline stage in code. | [`labs_fullcode/`](courseware_fullcode/labs_fullcode/) - instruction PDFs, starter `.py` / `.pine` files, solutions, the `pipeline/` package and bundled data |

Start with the low-code edition. The full-code edition covers the same topics and labs and is not required for the course or its assessment.

## Labs

Each lab adds one stage to a single algorithmic-trading pipeline, and every lab runs offline on bundled market data.

| Lab | Pipeline stage | Title | Low code (default) | Full code |
|---|---|---|---|---|
| 01 | Configuration | Pipeline Skeleton, Configuration and the Alpaca Paper Account | [Lab manual](courseware_lowcode/labs_lowcode/Lab01-alpaca-setup/Lab01_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab01-alpaca-setup/) |
| 02 | Data validation | Data-Validation Stage: Cross-Check Pipeline Bars against TradingView | [Lab manual](courseware_lowcode/labs_lowcode/Lab02-tradingview-charts/Lab02_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab02-tradingview-charts/) |
| 03 | Ingestion | Ingestion Stage: Multi-Timeframe Bars, Headlines and Data Quality | [Lab manual](courseware_lowcode/labs_lowcode/Lab03-alpaca-market-data/Lab03_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab03-alpaca-market-data/) |
| 04 | Hypothesis | Hypothesis Stage: from a Written Card to an Automated Statistical Test | [Lab manual](courseware_lowcode/labs_lowcode/Lab04-trading-hypothesis/Lab04_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab04-trading-hypothesis/) |
| 05 | Indicators | Indicator Stage: Pine Script v6 Indicators and their Python Twins | [Lab manual](courseware_lowcode/labs_lowcode/Lab05-pine-indicators/Lab05_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab05-pine-indicators/) |
| 06 | Strategy prototype | Strategy Prototype: TradingView Strategy Tester, Paper Trading from the Chart and Pipeline Reconciliation | [Lab manual](courseware_lowcode/labs_lowcode/Lab06-pine-strategy-tester/Lab06_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab06-pine-strategy-tester/) |
| 07 | Signals | Signal Stage: a Library of Trend, Mean-Reversion, Momentum and Breakout Signals | [Lab manual](courseware_lowcode/labs_lowcode/Lab07-technical-indicators/Lab07_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab07-technical-indicators/) |
| 08 | Execution | Execution Stage: an Order Manager that Trades the Paper Account in Any Session | [Lab manual](courseware_lowcode/labs_lowcode/Lab08-paper-orders/Lab08_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab08-paper-orders/) |
| 09 | Evaluation | Evaluation Stage: Performance and Risk Metrics with a Benchmark Table | [Lab manual](courseware_lowcode/labs_lowcode/Lab09-performance-metrics/Lab09_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab09-performance-metrics/) |
| 10 | Strategy search | Strategy-Search Stage: Grid Search, Out-of-Sample Ranking and Decay | [Lab manual](courseware_lowcode/labs_lowcode/Lab10-strategy-grid-search/Lab10_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab10-strategy-grid-search/) |
| 11 | ML signal | ML-Signal Stage: a Walk-Forward Classifier from Probability to Position | [Lab manual](courseware_lowcode/labs_lowcode/Lab11-ml-signal-classifier/Lab11_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab11-ml-signal-classifier/) |
| 12 | Regime filter | Regime-Filter Stage: PCA and K-Means as a Gate on the Signals | [Lab manual](courseware_lowcode/labs_lowcode/Lab12-market-regimes/Lab12_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab12-market-regimes/) |
| 13 | A/B test | A/B-Test Stage: a Statistical Decision before Capital Moves | [Lab manual](courseware_lowcode/labs_lowcode/Lab13-ab-testing/Lab13_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab13-ab-testing/) |
| 14 | Pairs / stat-arb | Pairs Stage: a Hedged, Market-Neutral Statistical-Arbitrage Sleeve | [Lab manual](courseware_lowcode/labs_lowcode/Lab14-pairs-trading/Lab14_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab14-pairs-trading/) |
| 15 | Backtest engine | Backtest-Engine Stage: Cost Models, Execution Timing and Break-Even | [Lab manual](courseware_lowcode/labs_lowcode/Lab15-trading-costs/Lab15_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab15-trading-costs/) |
| 16 | Automation | Automation Stage: a Scheduled, Risk-Checked Forward Test and Live Paper Trading | [Lab manual](courseware_lowcode/labs_lowcode/Lab16-paper-trading-bot/Lab16_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab16-paper-trading-bot/) |
| 17 | Event-driven automation | Event-Driven Automation: TradingView Webhook to Signal, Risk and Execution | [Lab manual](courseware_lowcode/labs_lowcode/Lab17-tradingview-webhook/Lab17_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab17-tradingview-webhook/) |
| 18 | Diagnostics | Diagnostics Stage: Automated Bias Checks before Go-Live | [Lab manual](courseware_lowcode/labs_lowcode/Lab18-diagnose-bias/Lab18_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab18-diagnose-bias/) |
| 19 | Monitoring and reporting | Monitoring and Reporting Stage: Automated Tearsheet and Backtest-vs-Forward Report | [Lab manual](courseware_lowcode/labs_lowcode/Lab19-performance-report/Lab19_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab19-performance-report/) |
| 20 | End-to-end pipeline | Capstone: One Command Runs the Pipeline End to End, with an Agentic Layer and Human Approval | [Lab manual](courseware_lowcode/labs_lowcode/Lab20-agentic-capstone/Lab20_Instructions.pdf) | [Code + manual](courseware_fullcode/labs_fullcode/Lab20-agentic-capstone/) |

## Course software

The labs run in the course's Trading Simulator, [alfredang/algorithmic-trader-bot](https://github.com/alfredang/algorithmic-trader-bot) - a local web app (uv or Docker Compose) for data, strategies, backtesting, paper trading, analytics and multi-agent AI. Its Course Labs page opens each lab step pre-filled. Download and installation steps are in the Learner Guide and the Lab 01 manual.

## Public package

**Low-code edition (default)**

| Item | Files |
|---|---|
| Trainer slides | [PPTX](courseware_lowcode/courseware/Slides_ML%20101%20for%20Financial%20Trading_v2.3.pptx) · [PDF](courseware_lowcode/courseware/Slides_ML%20101%20for%20Financial%20Trading_v2.3.pdf) |
| Lesson Plan | [DOCX](courseware_lowcode/courseware/LP_ML%20101%20for%20Financial%20Trading_v2.3.docx) · [PDF](courseware_lowcode/courseware/LP_ML%20101%20for%20Financial%20Trading_v2.3.pdf) |
| Learner Guide | [DOCX](courseware_lowcode/courseware/LG_ML%20101%20for%20Financial%20Trading_v2.3.docx) · [PDF](courseware_lowcode/courseware/LG_ML%20101%20for%20Financial%20Trading_v2.3.pdf) · [Markdown](courseware_lowcode/courseware/LG_ML%20101%20for%20Financial%20Trading_v2.3.md) |
| Facilitator Guide (public edition, no assessment keys) | [DOCX](courseware_lowcode/courseware/Facilitator-Guide_ML%20101%20for%20Financial%20Trading_v2.3.docx) · [PDF](courseware_lowcode/courseware/Facilitator-Guide_ML%20101%20for%20Financial%20Trading_v2.3.pdf) |
| Labs | [`labs_lowcode/`](courseware_lowcode/labs_lowcode/) - 20 lab manuals and the [Prompt Library](courseware_lowcode/labs_lowcode/Prompt_Library.html) |

**Full-code edition (optional)**

| Item | Files |
|---|---|
| Trainer slides | [PPTX](courseware_fullcode/courseware/Slides_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.pptx) · [PDF](courseware_fullcode/courseware/Slides_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.pdf) |
| Lesson Plan | [DOCX](courseware_fullcode/courseware/LP_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.docx) · [PDF](courseware_fullcode/courseware/LP_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.pdf) |
| Learner Guide | [DOCX](courseware_fullcode/courseware/LG_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.docx) · [PDF](courseware_fullcode/courseware/LG_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.pdf) · [Markdown](courseware_fullcode/courseware/LG_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.md) |
| Facilitator Guide (public edition, no assessment keys) | [DOCX](courseware_fullcode/courseware/Facilitator-Guide_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.docx) · [PDF](courseware_fullcode/courseware/Facilitator-Guide_ML%20101%20Fin%20Trading%20Full%20Code_v2.3.pdf) |
| Labs | [`labs_fullcode/`](courseware_fullcode/labs_fullcode/) - 20 labs with manuals, starter code and solutions, the `pipeline/` package, shared `common/` library and bundled data |

## Distribution boundary

This repository publishes the current learner and trainer courseware of both editions. The assessment (question papers, answer keys, rubric, Practical Performance pack), the full Facilitator Guide and the Assessment Plan are trainer-only and are kept off GitHub. Credentials are never committed: learners enter their own Alpaca paper keys in the simulator's Integrations page (full-code learners may use a git-ignored `.env`, see `.env.example`). The bundled market data (Yahoo Finance via yfinance) is for training use only.

> Lion City Capital and every scenario are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing here is investment advice.

## Provider

Developed and delivered by **Tertiary Infotech Academy Pte Ltd** (UEN 201200696W), 12 Woodlands Square, #07-85/86/87, Woods Square Tower 1, Singapore 737715. Course version 2.3 (22 October 2026).
