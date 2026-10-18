# Machine Learning 101 for Financial Trading

A hands-on IBF-accredited course on quant and algorithmic stock trading: learners turn trading ideas into testable hypotheses, model them with machine learning, backtest them with realistic costs and run them as an automated paper-trading pipeline on Alpaca and TradingView - with AI writing the code, so the focus stays on the algorithms.

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

## Labs

Each lab adds one stage to a single algorithmic-trading pipeline. Every lab folder holds a `LabNN_Instructions.pdf` lab manual (step-by-step instructions, AI-assistant prompts and checks) and its runnable `.py` / `.pine` files; all labs also run offline on bundled market data.

| Lab | Pipeline stage | Title | Lab manual |
|---|---|---|---|
| 01 | Configuration | [Pipeline Skeleton, Configuration and the Alpaca Paper Account](labs/Lab01-alpaca-setup/) | [PDF](labs/Lab01-alpaca-setup/Lab01_Instructions.pdf) |
| 02 | Data validation | [Data-Validation Stage: Cross-Check Pipeline Bars against TradingView](labs/Lab02-tradingview-charts/) | [PDF](labs/Lab02-tradingview-charts/Lab02_Instructions.pdf) |
| 03 | Ingestion | [Ingestion Stage: Multi-Timeframe Bars, Headlines and Data Quality](labs/Lab03-alpaca-market-data/) | [PDF](labs/Lab03-alpaca-market-data/Lab03_Instructions.pdf) |
| 04 | Hypothesis | [Hypothesis Stage: from a Written Card to an Automated Statistical Test](labs/Lab04-trading-hypothesis/) | [PDF](labs/Lab04-trading-hypothesis/Lab04_Instructions.pdf) |
| 05 | Indicators | [Indicator Stage: Pine Script v6 Indicators and their Python Twins](labs/Lab05-pine-indicators/) | [PDF](labs/Lab05-pine-indicators/Lab05_Instructions.pdf) |
| 06 | Strategy prototype | [Strategy Prototype: TradingView Strategy Tester, Paper Trading from the Chart and Pipeline Reconciliation](labs/Lab06-pine-strategy-tester/) | [PDF](labs/Lab06-pine-strategy-tester/Lab06_Instructions.pdf) |
| 07 | Signals | [Signal Stage: a Library of Trend, Mean-Reversion, Momentum and Breakout Signals](labs/Lab07-python-indicators/) | [PDF](labs/Lab07-python-indicators/Lab07_Instructions.pdf) |
| 08 | Execution | [Execution Stage: an Order Manager that Trades the Paper Account in Any Session](labs/Lab08-paper-orders/) | [PDF](labs/Lab08-paper-orders/Lab08_Instructions.pdf) |
| 09 | Evaluation | [Evaluation Stage: Performance and Risk Metrics with a Benchmark Table](labs/Lab09-performance-metrics/) | [PDF](labs/Lab09-performance-metrics/Lab09_Instructions.pdf) |
| 10 | Strategy search | [Strategy-Search Stage: Grid Search, Out-of-Sample Ranking and Decay](labs/Lab10-strategy-grid-search/) | [PDF](labs/Lab10-strategy-grid-search/Lab10_Instructions.pdf) |
| 11 | ML signal | [ML-Signal Stage: a Walk-Forward Classifier from Probability to Position](labs/Lab11-ml-signal-classifier/) | [PDF](labs/Lab11-ml-signal-classifier/Lab11_Instructions.pdf) |
| 12 | Regime filter | [Regime-Filter Stage: PCA and K-Means as a Gate on the Signals](labs/Lab12-market-regimes/) | [PDF](labs/Lab12-market-regimes/Lab12_Instructions.pdf) |
| 13 | A/B test | [A/B-Test Stage: a Statistical Decision before Capital Moves](labs/Lab13-ab-testing/) | [PDF](labs/Lab13-ab-testing/Lab13_Instructions.pdf) |
| 14 | Pairs / stat-arb | [Pairs Stage: a Hedged, Market-Neutral Statistical-Arbitrage Sleeve](labs/Lab14-pairs-trading/) | [PDF](labs/Lab14-pairs-trading/Lab14_Instructions.pdf) |
| 15 | Backtest engine | [Backtest-Engine Stage: Cost Models, Execution Timing and Break-Even](labs/Lab15-trading-costs/) | [PDF](labs/Lab15-trading-costs/Lab15_Instructions.pdf) |
| 16 | Automation | [Automation Stage: a Scheduled, Risk-Checked Forward Test and Live Paper Trading](labs/Lab16-paper-trading-bot/) | [PDF](labs/Lab16-paper-trading-bot/Lab16_Instructions.pdf) |
| 17 | Event-driven automation | [Event-Driven Automation: TradingView Webhook to Signal, Risk and Execution](labs/Lab17-tradingview-webhook/) | [PDF](labs/Lab17-tradingview-webhook/Lab17_Instructions.pdf) |
| 18 | Diagnostics | [Diagnostics Stage: Automated Bias Checks before Go-Live](labs/Lab18-diagnose-bias/) | [PDF](labs/Lab18-diagnose-bias/Lab18_Instructions.pdf) |
| 19 | Monitoring and reporting | [Monitoring and Reporting Stage: Automated Tearsheet and Backtest-vs-Forward Report](labs/Lab19-performance-report/) | [PDF](labs/Lab19-performance-report/Lab19_Instructions.pdf) |
| 20 | End-to-end pipeline | [Capstone: One Command Runs the Pipeline End to End, with an Agentic Layer and Human Approval](labs/Lab20-agentic-capstone/) | [PDF](labs/Lab20-agentic-capstone/Lab20_Instructions.pdf) |

## Course software

The labs are designed to run in the course's trading simulator, [alfredang/algorithmic-trader-bot](https://github.com/alfredang/algorithmic-trader-bot) - a local web app (uv or Docker Compose) for data, strategies, backtesting, paper trading, analytics and multi-agent AI. Download and installation steps are in the Learner Guide (Platform Guides) and the Lab 1 manual.

## Public package

| Item | Files |
|---|---|
| Trainer slides | [PPTX](courseware/Slides_ML%20101%20for%20Financial%20Trading_v2.0.pptx) · [PDF](courseware/Slides_ML%20101%20for%20Financial%20Trading_v2.0.pdf) |
| Lesson Plan | [DOCX](courseware/LP_ML%20101%20for%20Financial%20Trading_v2.0.docx) · [PDF](courseware/LP_ML%20101%20for%20Financial%20Trading_v2.0.pdf) |
| Learner Guide | [DOCX](courseware/LG_ML%20101%20for%20Financial%20Trading_v2.0.docx) · [PDF](courseware/LG_ML%20101%20for%20Financial%20Trading_v2.0.pdf) · [Markdown](courseware/LG_ML%20101%20for%20Financial%20Trading_v2.0.md) |
| Facilitator Guide (public edition, no assessment keys) | [DOCX](courseware/Facilitator-Guide_ML%20101%20for%20Financial%20Trading_v2.0.docx) · [PDF](courseware/Facilitator-Guide_ML%20101%20for%20Financial%20Trading_v2.0.pdf) |
| Labs | [`labs/`](labs/) - 20 labs with lab manuals, the `pipeline/` package, shared `common/` library and bundled data |

## Distribution boundary

This repository publishes the current learner and trainer courseware only. The assessment (question papers, answer keys, Practical Performance pack), the full Facilitator Guide and the Assessment Plan are trainer-only and are kept off GitHub. Credentials are never committed: put your own Alpaca paper keys in `labs/.env`, which is git-ignored. The bundled market data (Yahoo Finance via yfinance) is for training use only.

> Lion City Capital and every scenario are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing here is investment advice.

## Provider

Developed and delivered by **Tertiary Infotech Academy Pte Ltd** (UEN 201200696W), 12 Woodlands Square, #07-85/86/87, Woods Square Tower 1, Singapore 737715. Course version 2.0 (18 October 2026).
