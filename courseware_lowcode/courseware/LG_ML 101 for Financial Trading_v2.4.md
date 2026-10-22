# Learner Guide - Machine Learning 101 for Financial Trading

FSE-DAT-3019-1.1 Data Analytics and Computational Modelling (Proficiency Level 3) | Version 2.4 (22 October 2026) | Tertiary Infotech Academy Pte Ltd

> Lion City Capital and every scenario in these materials are fictitious and for training only. All trading in this course is paper (simulated) trading. Nothing in these materials is investment advice or a recommendation to trade any security.

## Learning outcomes

- **LO1** (A1, A6, K1, K9): Develop hypotheses for implementing data analytics and computational modelling activities in algorithmic trading, and identify possible big data applications across the forms of data within financial services.
- **LO2** (A2, A3, K3, K5, K7): Identify appropriate statistical algorithms and data models to test trading hypotheses, and use appropriate analytics platforms, analytical tools and statistical methods given specific analytics and reporting requirements.
- **LO3** (A4, A5, K2, K4, K6): Conduct statistical modelling of market data with machine learning models to derive patterns and solutions, and perform A/B testing of trading strategies based on different hypotheses.
- **LO4** (A7, A8, A9, A10, K7, K8): Perform coding and configuration of an automated trading program based on selected models or algorithms, conduct tests on its actions and outcomes, diagnose unintended outcomes, and draw insights from the results to support decisions and report accordingly.

## Course structure

| Topic | Title | Day | Labs |
|---|---|---|---|
| 1 | Foundations of Quant and Algorithmic Trading: From Thorp to AI Agents | 1 | 1-4 |
| 2 | Technical Indicators, Trading Strategies and Metrics with TradingView and Alpaca | 1 | 5-9 |
| 3 | Machine Learning Models, Statistical Modelling and A/B Testing for Trading Signals | 2 | 10-14 |
| 4 | Building an End-to-End Algorithmic Trading Pipeline: Backtest, Forward Test and Performance Analysis | 2 | 15-20 |


## Topic 1: Foundations of Quant and Algorithmic Trading: From Thorp to AI Agents

**Learning outcome:** Develop hypotheses for implementing data analytics and computational modelling activities in algorithmic trading, and identify possible big data applications across the forms of data within financial services.


### 1.1 Quant Success Stories: What Systematic Trading Has Achieved

- Ed Thorp - from blackjack to markets: his fund (Convertible Hedge Associates, 1969; Princeton Newport Partners from 1974) is often called the first market-neutral hedge fund and earned about 20% a year after fees for two decades by hedging warrants and convertibles with probability models.
- Renaissance Technologies - mathematician Jim Simons founded Monemetrics in 1978 (renamed 1982). Its Medallion fund (1988) trades purely on mathematical models of market data and averaged about 66% a year before fees (about 39% after fees) from 1988 to 2018.
- D.E. Shaw - founded in 1988 by computer-science professor David Shaw, a former member of Morgan Stanley's quantitative trading group; it builds mathematical models and software to exploit market anomalies and manages about US$60-65 billion.
- Man AHL - founded in 1987 as a systematic trend-following futures manager whose founders typed historical prices in by hand; it grew into a multi-strategy quant business trading momentum models across 800+ markets.
- Two Sigma - founded in 2001, it applies artificial intelligence, machine learning and distributed computing to trading, and manages about US$70 billion.
- Quant market makers - Jane Street reported about US$20.5 billion of net trading revenue in 2024 and nearly a quarter of primary US-listed ETF activity; Citadel Securities is estimated to handle about a quarter of all US equities trading.
- The common thread: a testable hypothesis, clean data, rigorous out-of-sample testing, realistic costs and strict risk control - exactly the pipeline this course builds.

### 1.2 The Evolution of Quant: From Thorp and Renaissance to High-Frequency Trading

- Algorithmic trading is the use of a computer program that follows a defined set of instructions to generate and execute orders automatically, based on price, timing, volume or a mathematical model.
- Foundations (1950s-1970s): Markowitz's 'Portfolio Selection' (1952) measures risk as variance; Thorp's 'Beat the Market' (1967) applies probability to hedging; the Black-Scholes option formula is published as the CBOE opens in April 1973.
- Factors and program trading (1970s-1980s): Barr Rosenberg's Barra builds multi-factor risk models of style, industry and size; computers trade baskets of stocks against new index futures. Black Monday (19 October 1987) shows portfolio-insurance program selling can deepen a crash.
- Statistical arbitrage (1980s-1990s): Gerry Bamberger and Nunzio Tartaglia's group at Morgan Stanley trades pairs of stocks that move together, by rule rather than intuition. Alumni and imitators - D.E. Shaw (1988) and Renaissance's Medallion (1988) - industrialise many small, market-neutral edges.
- Lessons from failure: Long-Term Capital Management, a highly leveraged relative-value fund, lost US$4.6 billion in 1998 and was recapitalised under Federal Reserve supervision; in the 'quant quake' of August 2007 crowded quant equity market-neutral funds lost heavily in days as positions unwound.
- From quant to high-frequency trading (1996-2010s): electronic order books such as Island ECN (1996), decimalisation (2001) and Regulation NMS (2005, in force 2007) reward speed. HFT firms co-locate servers at exchanges; Spread Networks' US$300 million straight fibre cut about 3 ms off New York-Chicago, and microwave links soon beat it.
- The speed race meets regulation: the 6 May 2010 Flash Crash and Knight Capital's loss of more than US$460 million in 45 minutes (2012) lead to kill switches and testing rules - MiFID II (2018), the SEC Market Access Rule - and IEX's 350-microsecond 'speed bump' exchange (2016). In Singapore, SGX RegCo's Regulatory Guide on Algorithmic Trading (2020) sets the expectations.
- Democratisation and AI (2018-present): API-first brokers such as Alpaca (2018) open algorithmic stock trading to individuals; machine learning and alternative data widen the signal set; LLMs and multi-agent systems now read text and propose trades.

### 1.3 The Paradigm Shift from Machine Learning to LLMs, and Its Impact on Quant

- Classical machine-learning quant works on structured data - prices, volumes, fundamentals - with features engineered by the quant (lagged returns, RSI, factor scores) and models such as regression, random forests and gradient boosting fitted to labelled history.
- The LLM paradigm adds unstructured text - news, filings, earnings-call transcripts, research - read directly by a pretrained language model. Lopez-Lira and Tang (2023) found that ChatGPT's good / bad scores for news headlines predict next-day stock returns, most strongly for small stocks and negative news.
- Finance-specific LLMs: BloombergGPT (March 2023) is a 50-billion-parameter model trained with 363 billion tokens of Bloomberg financial data plus general text, aimed at sentiment, entity recognition and news classification.
- Automated alpha research: systems such as Alpha-GPT turn a quant's idea in plain language into formulaic alpha factors, and AlphaAgent targets alpha decay by steering away from crowded, homogeneous factors. Coding agents now draft strategy code and backtests that the quant reviews.
- New risks: an LLM may already 'know' what happened in its training period, so in-sample backtests can carry look-ahead bias and a 'distraction' effect from what the model knows about the company (Glasserman and Lin, 2023). Test only on data after the model's knowledge cutoff and anonymise company names.
- Faster crowding: Lopez-Lira and Tang report that the returns to LLM news strategies decline as LLM adoption rises - prices become more efficient, so an LLM signal decays like any other alpha.
- The paradigm shift: AI now writes the code. Coding assistants and agents produce the Python, Pine Script and pipelines, so the quant's value moves from writing every line to the big concepts - the hypothesis, how the algorithm decides, unbiased testing with costs, risk control and judging the results. This course is taught that way: AI codes, you own the algorithm.
- What does not change: the hypothesis, out-of-sample testing, costs, risk limits and human accountability - the quant specifies, tests and supervises the models and agents, and answers for every trade.

### 1.4 Agentic AI versus AI Agents in Trading, and Multi-Agent Trading Systems

- Agentic AI is the capability of AI to plan and act: it calls tools (market-data and broker APIs), uses skills and memory, and follows instructions and guardrails to complete multi-step work when it is asked - for example, an LLM that fetches a stock's bars and news, checks its memory of past trades and proposes an order within its instructions.
- An AI agent is a special class of agentic AI that stands by 24/7 and works all the time: it is always on, woken by schedules, events and messages rather than by a prompt, and keeps long-term memory across days. Examples: OpenClaw (an open-source, self-hosted agent), Hermes Agent (Nous Research, February 2026) and OpenAI Dots (always-on agents in ChatGPT, September 2026). In trading, an AI agent is a round-the-clock monitor that watches prices and news overnight and proposes paper trades within limits.
- Multi-agent systems are agentic AI with several specialised agents - analysts, researchers, a trader and a risk manager - that coordinate, debate and decide; run continuously, the same desk becomes an always-on AI agent.
- TradingAgents (Xiao et al., 2024) simulates a stock-trading firm: fundamental, sentiment, news and technical analyst agents, bullish and bearish researchers who debate, a trader agent and a risk-management team.
- Other stock-trading agent systems: FinMem (2023, an LLM trading agent with layered memory making Buy / Sell / Hold decisions), FinAgent (2024, multimodal - prices, news and chart images), StockAgent (2024, LLM investors in a simulated stock market), QuantAgent (2025, indicator, pattern, trend and risk agents for high-frequency trading), the open-source AI Hedge Fund and Agentic Trading Lab, which paper-trades through the Alpaca API.
- Agentic systems introduce new failure modes: hallucinated figures, prompt injection from news text, over-trading and unclear accountability. Controls: hard risk limits coded outside the LLM, paper trading first, a full decision log and a human who approves every live order.
- Regulatory context in Singapore: MAS's FEAT principles (2018); the MAS Technology Risk Management Guidelines; and the MAS Guidelines on Artificial Intelligence Risk Management, issued on 7 October 2026 and effective from 7 October 2027, which require AI inventories, materiality assessment and lifecycle controls.

### 1.5 Forms of Data within Financial Services and Big Data Applications in Trading

- Market data: OHLCV bars (open, high, low, close, volume) at timeframes from one minute to one month; quotes (best bid and ask); trades (every print); and order-book depth. Alpaca's Market Data API serves bars, quotes, trades and news.
- Reference and corporate-action data: symbols, exchanges, trading calendars, splits and dividends. Using unadjusted prices across a split creates a false crash in a backtest.
- Fundamental and macroeconomic data: financial statements, ratios (P/E, P/B, ROE), earnings; interest rates, inflation and central-bank decisions - the inputs to factor models.
- Alternative data: news and social-media sentiment, earnings-call transcripts, web traffic, satellite imagery and card spending - increasingly turned into trading signals by NLP and LLMs.
- The four Vs of big data in trading: volume (tick data runs to billions of rows), velocity (streaming quotes), variety (prices, text, images) and veracity (bad ticks, survivorship, restatements).
- Big data applications in trading: tick-level execution analytics and smart order routing, cross-asset regime detection, news-driven event trading, sentiment signals, intraday risk monitoring, and surveillance of order and trade data for market abuse.

### 1.6 Developing Hypotheses for Quant and Algorithmic Trading Models

- Every trading model starts with a hypothesis: a precise, testable statement about market behaviour - not 'buy good stocks' but 'when SPY closes below its lower Bollinger Band, its average 5-day forward return exceeds its unconditional 5-day return'.
- A good trading hypothesis states the universe, the signal, the holding period, the expected effect and the benchmark, and is written down BEFORE looking at the results - otherwise it is curve-fitting.
- Express it as a null hypothesis (H0: no difference) and an alternative (H1: the signal earns more than the benchmark), with the test and the significance level chosen in advance.
- Economic rationale matters: trend following rests on under-reaction and herding; mean reversion on over-reaction and liquidity provision; momentum on slow diffusion of information; pairs trading on a stable economic link between two stocks. A pattern with no rationale is more likely to be noise.
- The quant model-building steps: frame the hypothesis, collect data, define the target and features, split by time, train, validate, test out of sample, then paper trade before risking capital.
- Business use cases for data analytics and modelling in trading: signal generation, execution cost reduction, portfolio construction, risk forecasting and trade surveillance - each with its own success metric.

### Quant success stories

| Firm / person | Year | Story |
|---|---|---|
| Ed Thorp - Princeton Newport | 1969 | First market-neutral quant fund: about 20% a year after fees for two decades by hedging warrants and convertibles |
| Renaissance - Medallion | 1988 | Purely model-driven; about 66% a year before fees, 39% after (1988-2018); closed to outsiders, employee-owned |
| D.E. Shaw | 1988 | Founded by a computer-science professor from Morgan Stanley's quant group; models and software; about US$60-65bn |
| Man AHL | 1987 | Systematic trend following from hand-typed price histories to momentum models across 800+ markets |
| Two Sigma | 2001 | AI, machine learning and distributed computing applied to trading; about US$70bn under management |
| Jane Street | 2024 | Quant market maker: about US$20.5bn net trading revenue; nearly a quarter of primary US ETF activity |
| Citadel Securities | Today | Quant market maker estimated to handle about a quarter of all US equities trading |


### Timeline: the evolution of quant and algorithmic trading

| Year | Milestone | Significance |
|---|---|---|
| 1952 | Modern portfolio theory | Markowitz's 'Portfolio Selection' measures risk as variance: diversification becomes maths |
| 1967 | Thorp's 'Beat the Market' | Ed Thorp applies probability to hedging warrants - an early quant trading playbook |
| 1969 | First market-neutral quant fund | Thorp's fund (Princeton Newport from 1974) earns about 20% a year after fees for two decades |
| 1973 | Black-Scholes and the CBOE | Option-pricing formula published as the CBOE opens (Apr 1973); CBOE adopts it by 1975 |
| Mid-1970s | Factor risk models | Barr Rosenberg's Barra models portfolio risk from style, industry and size factors |
| 1978 | Renaissance is founded | Mathematician Jim Simons founds Monemetrics; renamed Renaissance Technologies in 1982 |
| 1980s | Statistical arbitrage | Bamberger and Tartaglia's Morgan Stanley group trades pairs of co-moving stocks by rule |
| 1987 | Black Monday | Dow falls 22.6% on 19 Oct; portfolio-insurance program selling deepens the crash |
| 1988 | Medallion and D.E. Shaw | Renaissance launches Medallion; ex-Morgan Stanley quant David Shaw founds D.E. Shaw |
| 1996 | Island ECN | Fast electronic order book (trading from 1997) becomes a hub for early HFT firms |
| 1998 | LTCM collapses | Leveraged relative-value fund loses US$4.6bn; Fed-supervised US$3.65bn recapitalisation |
| 2001 | Decimalisation | US stocks quote in cents, not 1/16ths; spreads narrow and electronic market making grows |
| 2005 | Regulation NMS | SEC rule (in force 2007) links venues; fragmentation rewards speed and smart order routing |
| 2007 | The quant quake | Week of 6 Aug: crowded quant market-neutral funds suffer sudden losses as positions unwind |
| 2010 | Flash Crash | 6 May: the Dow drops nearly 1,000 points in minutes after a large algorithmic sell order |
| 2010 | The speed race | US$300m straight fibre New York-Chicago cuts about 3 ms; microwave links soon beat it |
| 2012 | Knight Capital | A faulty deployment sends millions of orders in 45 minutes; Knight loses over US$460m |
| 2016 | IEX speed bump | SEC approves IEX as an exchange with a 350-microsecond delay against latency arbitrage |
| 2018 | MiFID II | EU requires algorithm testing, kill switches and records; HFT formally defined |
| 2018 | API-first brokers | Alpaca's commission-free trading API opens algorithmic stock trading to individuals |
| 2020 | SGX RegCo algo guide | Sets expectations for governance, risk controls and testing of algorithms by SGX members |
| 2023 | LLM trading signals | ChatGPT headline sentiment predicts next-day stock returns (Lopez-Lira and Tang) |
| 2024 | Multi-agent LLM trading | TradingAgents (Dec 2024): analyst, debate, trader and risk agents trade stocks |
| 2026 | MAS AI Risk Management | Guidelines issued 7 Oct 2026, effective 7 Oct 2027: AI inventories and lifecycle controls |


### Machine-learning quant versus LLM-era quant

| Dimension | Machine-learning quant | LLM-era quant |
|---|---|---|
| Main data | Structured: prices, volumes, fundamentals | Adds unstructured text: news, filings, earnings calls, research |
| Features | Hand-engineered by the quant (lags, RSI, factors) | Text read directly; LLM scores sentiment and events |
| Model building | Fit regressions, trees, boosting on labelled data | Prompt or fine-tune pretrained LLMs; agents propose alphas |
| Who writes the code | The quant, line by line | AI writes it; the quant directs and reviews |
| Research workflow | The quant writes every line of code | Coding agents draft code and backtests; the quant reviews |
| Alpha decay | Signals fade as more funds trade them | LLM signals fade too as LLM adoption rises |
| New risks | Overfitting; look-ahead in features | LLM training-data look-ahead and 'distraction'; homogeneous factors |
| Human role | Model builder | Supervisor: hypothesis, testing, risk sign-off |


### Lab 1: Pipeline Skeleton, Configuration and the Alpaca Paper Account

*K5 | 20 min | stage: Configuration | folder: [`labs_lowcode/Lab01-alpaca-setup/`](../labs_lowcode/Lab01-alpaca-setup/)*

Get the simulator running, decide between the offline demo and an Alpaca paper account, and check every integration's status.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 01: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Load the demo data**

Open Settings and press 'Load / refresh demo data'. This caches 12 symbols of daily bars 2018-2025, SPY hourly bars, sample headlines, two custom strategies and sample backtests.

Open: <http://localhost:8000/#/settings> (Settings > Demo data)

*Check:* Settings shows about 29,000 bars and at least 8 backtests.

**Step 2. Check the integrations**

Open Integrations. Without keys, Alpaca shows 'not configured' and the app uses the simulator broker and the offline data. To connect Alpaca paper: alpaca.markets > Paper Trading > API Keys > Generate, then paste the Key ID and Secret into the Alpaca card and press Save & test.

Open: <http://localhost:8000/#/integrations> (Integrations)

*Check:* Alpaca test says 'Paper account ACTIVE' (online) - or you understand the app runs fully offline.

**Step 3. Check the AI agent login**

On the Integrations page read the OpenAI Codex and Claude cards. They are optional: without them the multi-agent desk runs its rule-based agents and every lab still works.

Open: <http://localhost:8000/#/integrations> (Integrations > AI providers)

*Check:* You can say which brain the desk will use: codex, claude, openai or the rule-based fallback.

**Step 4. Read the market clock**

Look at the US session badge in the top bar. Singapore is 12-13 hours ahead of New York, so a 09:00-18:30 SGT class sits in the US overnight and pre-market sessions.

Open: <http://localhost:8000/#/trading> (Paper Trading > clock)

*Check:* You can explain why orders placed during class become extended-hours LIMIT orders.

**Step 5. Tour the Pipeline Map**

Open the Pipeline Map and hover each of the 14 stages. Click 'Data ingestion' to see its recent activity.

Open: <http://localhost:8000/#/pipeline> (Pipeline Map)

*Check:* Data ingestion and Backtesting are green; you can name the stage that enforces the kill switch.

**Expected in the app:** A working app with demo data loaded, a verified Alpaca paper account or the simulator, and a known AI-agent brain.


### Lab 2: Data-Validation Stage: Cross-Check Pipeline Bars against TradingView

*A3, K5, K9 | 20 min | stage: Data validation | folder: [`labs_lowcode/Lab02-tradingview-charts/`](../labs_lowcode/Lab02-tradingview-charts/)*

Prove the app's prices are right: compare its bars with TradingView's Data Window and explain adjusted vs unadjusted prices.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 02: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Read TradingView's Data Window**

In TradingView open NASDAQ:AAPL, daily timeframe, hover the bar of 2025-12-31 and read open/high/low/close in the Data Window (default settings: dividends NOT adjusted).

Open: <http://localhost:8000/#/data?tab=reference&ref=AAPL> (Data > Validate vs TradingView (AAPL))

*Check:* You have four numbers from TradingView.

**Step 2. Compare with RAW and ADJUSTED bars**

Type your TradingView values into the 'Your TradingView reading' row. The app shows the difference against RAW (split-adjusted only) and ADJUSTED (split + dividend) bars.

Open: <http://localhost:8000/#/data?tab=reference&ref=AAPL> (Data > Validate vs TradingView)

*Check:* Verdict 'PASS - TradingView matches RAW' (to within 0.1%).

**Step 3. Repeat for SGX:D05 (DBS)**

Select SGX:D05. DBS pays large dividends, so the adjustment factor is far from 1.

Open: <http://localhost:8000/#/data?tab=reference&ref=D05.SI> (Data > Validate vs TradingView (D05))

*Check:* You can explain why the ADJUSTED close is lower than the RAW close and why a model trained on adjusted prices must never be fed raw live prices.

**Step 4. Inspect the chart**

Open the AAPL chart and compare its shape with TradingView.

Open: <http://localhost:8000/#/data?tab=chart&symbol=AAPL> (Data > Chart AAPL)

*Check:* The candles match TradingView's daily chart (allowing for the adjustment).

**Expected in the app:** A PASS / FAIL validation for SGX:D05 and NASDAQ:AAPL on 2025-12-31, with the dividend-adjustment factor explained.


### Lab 3: Ingestion Stage: Multi-Timeframe Bars, Headlines and Data Quality

*A6, K9 | 20 min | stage: Ingestion | folder: [`labs_lowcode/Lab03-alpaca-market-data/`](../labs_lowcode/Lab03-alpaca-market-data/)*

Ingest bars from Alpaca / Twelve Data / yfinance (or the demo files), run the data-quality checks and score news sentiment.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 03: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Fetch data**

Data > Instruments & ingestion: fetch AAPL with source 'auto' (Alpaca if keys, else the demo file). Online, try 'yfinance' or 'Twelve Data' too (Twelve Data needs TWELVEDATA_API_KEY).

Open: <http://localhost:8000/#/data?tab=instruments&symbol=AAPL> (Data > Fetch AAPL)

*Check:* A toast reports the number of bars, the source and the quality status.

**Step 2. Read the data-quality report**

Open Data quality for SPY. Look at missing values, duplicate timestamps, gaps over 4 days and big moves (possible unadjusted splits).

Open: <http://localhost:8000/#/data?tab=quality&symbol=SPY> (Data > Quality SPY)

*Check:* Status OK or CHECK; the big-move dates include March 2020.

**Step 3. Switch timeframes**

On the chart, switch SPY between 1Day, 1Week, 1Month and 1Hour.

Open: <http://localhost:8000/#/data?tab=chart&symbol=SPY&timeframe=1Week> (Data > Chart SPY weekly)

*Check:* Weekly and monthly bars are resampled from daily bars; hourly bars are US/Eastern.

**Step 4. Headlines and sentiment**

Data > News & sentiment for NVDA: press 'Fetch & score headlines'. Online with NEWSAPI_KEY it calls NewsAPI.org; otherwise Alpaca News or the synthetic sample headlines. Try the sentiment box with your own sentence.

Open: <http://localhost:8000/#/data?tab=news&symbol=NVDA> (Data > News NVDA)

*Check:* Each headline has a VADER score between -1 and +1; the daily sentiment chart appears.

**Expected in the app:** A cached universe, a data-quality report and scored headlines with daily sentiment.


### Lab 4: Hypothesis Stage: from a Written Card to an Automated Statistical Test

*A1, A6, K1 | 15 min | stage: Hypothesis | folder: [`labs_lowcode/Lab04-trading-hypothesis/`](../labs_lowcode/Lab04-trading-hypothesis/)*

Write H0 and H1 before looking at results and test them with a Welch t-test and a bootstrap CI.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 04: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Write the hypothesis card**

Research > Hypothesis test. Keep signal 'losing streak' n = 3, horizon 1 day, alpha 0.05, min edge 3 bps. Read the H1 and H0 text.

Open: <http://localhost:8000/#/research/hypothesis> (Research > Hypothesis (SPY, losing streak 3))

*Check:* H0 and H1 are written before you press Run.

**Step 2. Run the test**

Press 'Run the test'.

Open: <http://localhost:8000/#/research/hypothesis>

*Check:* You can read the signal-day mean, the other-day mean, Welch t and p, and the 95% bootstrap CI.

**Step 3. Robustness and multiple testing**

Read the robustness grid (other streak lengths and QQQ) and the Bonferroni alpha.

Open: <http://localhost:8000/#/research/hypothesis>

*Check:* You can explain why trying many variants inflates false positives.

**Expected in the app:** A decision (SUPPORTED / NOT SUPPORTED) with p-value, edge in bps and a robustness grid.


## Topic 2: Technical Indicators, Trading Strategies and Metrics with TradingView and Alpaca

**Learning outcome:** Identify appropriate statistical algorithms and data models to test trading hypotheses, and use appropriate analytics platforms, analytical tools and statistical methods given specific analytics and reporting requirements.


### 2.1 Technical Indicators: Trend, Momentum, Volatility and Volume

- Simple Moving Average (SMA): the average close over n bars. Exponential Moving Average (EMA): a weighted average with smoothing factor 2/(n+1), reacting faster to recent prices. Both are trend indicators.
- Relative Strength Index (RSI): 100 - 100/(1 + RS), where RS is the ratio of average gains to average losses over 14 bars (Wilder smoothing). Readings above 70 are conventionally 'overbought', below 30 'oversold'.
- The number in brackets is the look-back period. RSI(2) uses the last 2 bars and swings to extremes after a 1-2 day move (SPY RSI(2) was below 10 on 9.6% of days in 2018-2025); RSI(14) moves slowly (below 30 on 1.7% of days). On 10 October 2025 SPY fell 2.7%: RSI(2) dropped to 5.8 while RSI(14) read a neutral 42.5. SMA(50), EMA(20), Bollinger(20, 2) and ATR(14) follow the same convention.
- MACD: the 12-period EMA minus the 26-period EMA, with a 9-period EMA 'signal line'. A MACD cross above its signal line is a momentum buy signal.
- Bollinger Bands: a 20-period SMA plus and minus 2 standard deviations. The bands widen in volatile markets and narrow in quiet ones; closes outside the bands feed both mean-reversion and breakout strategies.
- Average True Range (ATR): the average of the true range (the largest of high-low, |high-previous close| and |low-previous close|). Used to size positions and to set volatility-based stops.
- Volume indicators: Volume-Weighted Average Price (VWAP), the benchmark price for execution quality, and On-Balance Volume (OBV), which accumulates volume on up days and subtracts it on down days.
- Every indicator is a statistical transformation of past prices; none predicts the future on its own. Indicators lag, and many are highly correlated with each other - adding more rarely adds information.

### 2.2 Classification of Algorithmic Trading and Quant Algorithms

- By purpose, trading algorithms fall into seven families: execution, market making, arbitrage, directional (alpha), statistical arbitrage and pairs (hedged), factor and portfolio construction, and hedging and risk control.
- Execution algorithms work a large order at low cost and market impact: TWAP slices evenly over time; VWAP follows the day's volume curve; percentage-of-volume (POV) trades a fixed share of live volume; implementation shortfall minimises cost versus the arrival price; iceberg orders show only part of the size; smart order routing chooses the venue.
- The SEC's 2010 Concept Release on Equity Market Structure groups high-frequency strategies into four types: passive market making (resting bids and offers that provide liquidity), arbitrage (pricing inefficiencies between related products, such as an ETF and its basket), structural (exploiting structural vulnerabilities, such as stale quotes), and directional (short-term positions anticipating an intraday move).
- Directional (alpha) strategies: trend following (moving-average crossover), momentum (hold recent winners), breakout (new n-day high), mean reversion (Bollinger Bands, RSI(2)) and event or news-driven trading.
- Long and short positions: a long buys first and profits when the price rises (the most it can lose is the amount paid); a short borrows shares and sells them first, buys them back later and profits when the price falls (losses are unlimited, and it needs a margin account - Alpaca requires at least $2,000 of equity). Selling shares you own only closes a long.
- Mean reversion buys when the price is stretched below its normal range (a close below the lower Bollinger Band, RSI(14) below 30, RSI(2) below 10, or a losing streak) and exits at the average. Compared with trend following it has a high win rate but rare large losses when a dip becomes a crash, so it needs a stop-loss or time limit, a trend filter (price above its 200-day SMA) and stable markets.
- Statistical arbitrage and pairs trading are hedged: long one asset and short a related one, so most market moves cancel and the profit comes from the spread reverting (Topic 3.6).
- By holding period: high-frequency (microseconds to seconds), intraday (minutes to hours), swing (days to weeks) and position (weeks to months). By model: rule-based, statistical, machine learning, reinforcement learning, and LLM / agentic.
- Matching the algorithm to the hypothesis - and to the right statistical test - is the A2 skill: a difference in means needs a t-test or bootstrap, a direction forecast needs a classifier, a regime question needs clustering, and a spread needs a cointegration test.

### 2.3 Analytics Platforms and Tools: TradingView versus Alpaca, and Python

- TradingView is a charting and strategy-design platform: global markets including SGX, built-in indicators, the Pine Script language, the Strategy Tester for backtests, alerts and webhooks (webhooks need a paid plan), and a built-in Paper Trading account opened from the chart's Trading Panel with your own starting capital and commission.
- Alpaca is an API-first US broker: commission-free US stocks and ETFs, plus options and crypto; a free paper-trading account that mirrors the live API; the Trading API (account, orders, positions, clock) and the Market Data API (bars, quotes, trades, news; the free plan uses the IEX feed); and the official alpaca-py Python SDK.
- The key difference: TradingView is where a strategy is designed, visualised and first tested; Alpaca is where a program places and manages orders automatically. TradingView has no machine learning and a simplified backtester; Alpaca has no charting or strategy tester - in this course the Trading Simulator provides them, so no coding is needed.
- Trading hours for automation from Singapore: Alpaca offers 24/5 trading of US stocks (8 pm ET Sunday to 8 pm ET Friday) - outside the regular session only limit orders with extended hours enabled are accepted, at lower liquidity.
- They work together: a TradingView alert can send a webhook to your server, which places the order on Alpaca; and an Alpaca account can be connected in TradingView's trading panel to trade from the chart.
- Python - pandas, NumPy, scikit-learn, XGBoost, SciPy, matplotlib and alpaca-py - joins them: data handling, machine learning, statistical tests, cost-aware backtests and the automation loop.
- API keys are credentials: paste them only into a protected settings store such as the simulator's Integrations page - never into code, chats or files you share - and use separate paper and live keys.

### 2.4 Coding Languages for Algorithms and Signals, and Order Placement

- Pine Script v6 (TradingView's language): every script starts with //@version=6 and declares indicator() or strategy(). Built-in functions such as ta.ema, ta.rsi, ta.crossover and strategy.entry express a signal in a few lines.
- Python: the dominant language for quantitative research - readable, with mature data and machine learning libraries. A signal is typically a pandas Series of +1 / 0 / -1 aligned to the bar index.
- Other languages: C++ and Java for low-latency execution systems, R for statistics, SQL for data stores, and MQL for MetaTrader. LLMs can now draft code in all of them, but the developer remains accountable for testing it.
- Order types on Alpaca: market (fill now at the best price), limit (fill only at the limit price or better), stop (becomes a market order when the stop is hit), stop-limit, and trailing stop.
- Time in force: day, gtc (good till cancelled), opg (market on open), cls (market on close), ioc (immediate or cancel) and fok (fill or kill). Order classes: simple, bracket (entry with take-profit and stop-loss), OCO and OTO.
- The order lifecycle: new, accepted, partially filled, filled, cancelled, expired or rejected. A program must read the order status rather than assume a fill.
- Paper trading simulates fills against real market quotes but cannot model your own market impact or queue position - a limitation to remember when comparing paper and live results.

### 2.5 Performance and Risk Metric Definitions

- Return metrics: total return; compound annual growth rate CAGR = (ending value / starting value)^(1/years) - 1; and the benchmark-relative excess return.
- Risk metrics: annualised volatility = standard deviation of daily returns x sqrt(252); maximum drawdown = the largest peak-to-trough fall in the equity curve.
- Risk-adjusted metrics: Sharpe ratio = (mean return - risk-free rate) / standard deviation, annualised by sqrt(252); Sortino ratio uses only downside deviation; Calmar ratio = CAGR / |maximum drawdown|.
- Trade metrics: number of trades, win rate (% of profitable trades), profit factor (gross profit / gross loss), average win and loss, expectancy = win rate x average win - loss rate x average loss.
- Activity metrics: exposure (% of time in the market) and turnover (traded value / average capital). High turnover multiplies the drag of trading costs.
- Market-relative metrics: beta (sensitivity to the benchmark) and alpha (return not explained by beta), estimated by regressing strategy returns on benchmark returns.
- No single metric is enough: report return, risk and cost together, and always against a buy-and-hold benchmark for the same period.

### Classification of trading algorithms

| Family | Purpose | Examples |
|---|---|---|
| Execution algorithms | Work a large order at low cost and market impact | VWAP, TWAP, POV, implementation shortfall, iceberg, smart order routing |
| Market making | Quote bids and offers, earn the spread, manage inventory | Passive market making with resting limit orders |
| Arbitrage | Capture mispricing between related products or markets | ETF versus its basket, index futures versus stocks |
| Directional / alpha | Take a view on the direction of price | Trend following, momentum, breakout, mean reversion, news |
| Statistical arbitrage and pairs | Hedged: long one asset, short a related one; trade the spread | Pairs trading, cointegration, market-neutral baskets |
| Factor and portfolio | Build and rebalance portfolios from return drivers and risk | Value, momentum, size factors; mean-variance optimisation |
| Hedging and risk | Offset unwanted exposure and enforce limits | Delta hedging, beta hedging, pairs hedge, kill switch |


### TradingView versus Alpaca

|  | TradingView | Alpaca |
|---|---|---|
| What it is | Charting and strategy-design platform | API-first US broker for automated trading |
| Markets | Global charts incl. SGX, US, FX, crypto | US stocks and ETFs, options, crypto |
| Strategy design | Pine Script v6 indicators and strategies | Through the API - in this course the Trading Simulator does it for you |
| Backtesting | Strategy Tester (simplified costs and fills) | None built in - the Trading Simulator runs the cost-aware backtest |
| Paper trading | Built-in Paper Trading account from the chart | Paper account mirroring the live API |
| Automation | Alerts; webhooks on paid plans | Trading API: orders, positions, clock; 24/5 trading |
| Data | Charts and Data Window | Market Data API: bars, quotes, trades, news (IEX free) |
| Machine learning | Not supported | Through code - in this course the Trading Simulator has built-in logistic regression, random forest and XGBoost |
| Best used for | Designing, visualising and first-testing a rule | Executing and forward-testing it automatically |


### Strategy Families: the Idea, When It Works, When It Will Not

| Family | The idea | When it works | When it will not work |
|---|---|---|---|
| Trend Following (Lab 7: EMA 20/50 on SPY) | Prices that have started to move tend to keep moving. Buy when a fast average is above a slow one (or price is above its 200-day average); exit when the trend turns. | Long, persistent moves - bull or bear markets, macro trends lasting months. A few big winners pay for many small losses. | Sideways, choppy markets: price crosses the averages again and again (whipsaws), every crossing costs money, and signals arrive late at turns. |
| Mean Reversion (Lab 7: Bollinger 20 / k = 2.0 and 1.5 on KO) | Like a rubber band, short-term over-reactions snap back. Buy when price is stretched below its normal range (lower Bollinger Band, RSI(2) below 10) and sell when it returns to the average. | Range-bound, liquid markets and stable large stocks, where extremes tend to snap back within days. | A real trend or a news shock: 'cheap' keeps getting cheaper. A high win rate hides rare large losses - as in March 2020. |
| Momentum (Lab 7: 126-day time-series momentum on QQQ) | Winners keep winning for months. Buy what has risen over the last 6-12 months (time-series) or what has risen most among its peers (cross-sectional). | Persistent market or sector themes, spread across many assets and rebalanced regularly. | Sharp reversals - 'momentum crashes' such as the 2009 rebound, when last year's losers rally hardest - and choppy markets that churn the portfolio. |
| Breakout (Lab 7: Donchian 20 / 10 on QQQ) | A close above the recent range (for example the 20-day high, the Donchian channel) signals the start of a new move: buy the breakout, exit on a shorter low. | Volatility expanding after a quiet period and a new trend starting - indices and commodities in strong regimes. | False breakouts in a range: price pokes above the high and falls back. A low win rate, so exits must be disciplined and costs kept low. |


### Key Metrics Defined


#### Sharpe Ratio

- **Definition:** Return earned per unit of risk taken: the average excess return divided by its volatility, annualised.
- **Formula:** Sharpe = (mean daily return - daily risk-free rate) / std of daily returns x sqrt(252).
- **How to read it:** Below 0.5 weak, about 1 good, above 2 rare for a daily strategy - check for errors. Always compare with buy-and-hold over the same period.
- **Insight:** Volatility counts as risk whether it is up or down, and a short or costless backtest inflates it - 2020 returned 18% but at 33% volatility, a Sharpe of only 0.67.

#### Maximum Drawdown

- **Definition:** The largest fall of the equity curve from a previous peak to a later low - the worst loss an investor would have lived through before a new high.
- **Formula:** Drawdown(t) = equity(t) / running peak(t) - 1.  Max drawdown = the most negative drawdown over the period.
- **How to read it:** A -20% drawdown needs +25% to recover; -50% needs +100%. Compare with buy-and-hold and with the loss the investor can tolerate.
- **Insight:** One path-dependent number: it does not say how long recovery took, and a short backtest may simply miss a bad period. SPY 2018-2025: -33.7% in five weeks of 2020.

### Indicator by Indicator


#### Moving Averages (SMA and EMA)

- **Definition:** The average closing price over the last n bars - a smoothed line that shows the trend. The EMA weights recent bars more, so it turns sooner.
- **Formula:** SMA(n) = (C1 + C2 + ... + Cn) / n.  EMA(t) = a x C(t) + (1 - a) x EMA(t-1), with a = 2 / (n + 1).
- **How to read it:** Price above a rising average = uptrend. The 50 / 200-day pair is the classic trend filter; EMA 20 tracks the short-term trend.
- **Insight:** Every average lags: the longer n, the smoother - and the later each signal. In sideways markets price whipsaws across it.

#### MACD (Moving Average Convergence Divergence)

- **Definition:** A momentum-of-trend gauge: the gap between a fast and a slow EMA, with a signal line and a histogram that show whether momentum is growing.
- **Formula:** MACD = EMA12(C) - EMA26(C).  Signal = EMA9(MACD).  Histogram = MACD - Signal.
- **How to read it:** MACD crossing above its signal line = momentum turning up; MACD above zero = the 12-day trend is above the 26-day trend.
- **Insight:** A shrinking histogram warns that a move is losing strength before price turns - but it is built from EMAs, so it lags and whipsaws in ranges.

#### RSI (Relative Strength Index)

- **Definition:** An oscillator from 0 to 100 that compares the size of recent gains with recent losses - how stretched the latest move is.
- **Formula:** RS = average gain / average loss over n bars (Wilder smoothing, n = 14).  RSI = 100 - 100 / (1 + RS).
- **How to read it:** Above 70 = overbought, below 30 = oversold. Short look-backs such as RSI(2) are used for mean-reversion entries.
- **Insight:** In a strong trend RSI can stay above 70 for weeks: overbought is not a sell signal by itself. Test the thresholds - they are conventions.

#### Donchian Channel

- **Definition:** A channel drawn through the highest high and the lowest low of the last n bars - the levels a breakout must clear.
- **Formula:** Upper(n) = max(High, last n bars).  Lower(n) = min(Low, last n bars).  Classic n = 20 (the Turtle traders used 20 and 55).
- **How to read it:** A close above the prior upper band = upside breakout; exit on a break of a shorter (e.g. 10-day) low.
- **Insight:** Breakout systems win rarely but big. Compare today's close with the channel up to YESTERDAY - including today's high is look-ahead.

#### Bollinger Bands

- **Definition:** A moving average with bands set a number of standard deviations above and below it, so the bands widen and narrow with volatility.
- **Formula:** Middle = SMA20(C).  Upper / Lower = Middle +/- 2 x StDev20(C).  %B = (C - Lower) / (Upper - Lower).
- **How to read it:** Mean reversion: buy a close below the lower band, exit at the middle. A 'squeeze' (narrow bands) often comes before a big move.
- **Insight:** Returns are not normal: closes fall outside the bands far more often than the 5% a normal curve implies. In a trend, 'oversold' keeps falling.

#### ATR (Average True Range)

- **Definition:** The average size of a day's price range, including overnight gaps - a volatility ruler in price units.
- **Formula:** TR = max(H - L, |H - previous C|, |L - previous C|).  ATR = average of TR over n bars (Wilder smoothing, n = 14).
- **How to read it:** Set stops at 2-3 x ATR and size positions as risk budget / (k x ATR), so every trade carries similar risk.
- **Insight:** ATR says how far, not which way. Compare instruments with ATR as a % of price, since ATR rises with the price level.

#### VWAP (Volume-Weighted Average Price)

- **Definition:** The average price paid during the session, weighted by the volume traded at each price. It resets at every session open.
- **Formula:** Typical price P = (H + L + C) / 3.  VWAP = sum(P x Volume) / sum(Volume), summed from the session open.
- **How to read it:** The execution benchmark: buying below VWAP is a good fill. Intraday traders read price above VWAP as buyers in control.
- **Insight:** Institutions judge execution algorithms against VWAP. It needs intraday data - on daily bars it is only an approximation.

#### OBV (On-Balance Volume)

- **Definition:** A running total of volume that adds a day's volume when the close rises and subtracts it when the close falls.
- **Formula:** OBV(t) = OBV(t-1) + Volume(t) if C(t) > C(t-1); - Volume(t) if C(t) < C(t-1); unchanged if equal.
- **How to read it:** A rising OBV confirms an up-trend; OBV making new highs before price is read as accumulation. Read the slope, not the level.
- **Insight:** Volume shows the conviction behind a move. An OBV that falls while price rises (divergence) is a warning, not a signal on its own.

### Algorithm: Moving-Average Crossover (Trend Following)

- **How it works:** Two moving averages of the close: a fast one reacts quickly, a slow one shows the trend.
- **Rule:** Fast crosses ABOVE slow (golden cross): buy. Fast crosses BELOW (death cross): sell or go flat.
- **Works best when:** Markets trend for months - it rides the move and cuts losers when the trend turns.
- **Watch out for:** Whipsaws in sideways markets; signals lag; trade on the next bar, not the crossing bar.

### Algorithm: Bollinger Band Mean Reversion

- **How it works:** Bands = 20-day mean +/- 2 standard deviations. A close outside the band is 'stretched'.
- **Rule:** Close below the lower band: buy. Exit when the price returns to the middle band (the mean).
- **Works best when:** Range-bound markets where over-reactions snap back, e.g. a defensive stock such as KO.
- **Watch out for:** Strong trends keep 'stretching' - add a stop-loss or a trend filter; many small wins, rare big losses.

### Algorithm: RSI and MACD Momentum Oscillators

- **How it works:** RSI = 100 - 100/(1+RS), RS = average gain / average loss over 14 bars. MACD = EMA12 - EMA26.
- **Rule:** RSI < 30 oversold / > 70 overbought. MACD crossing above its 9-EMA signal line = momentum buy.
- **Works best when:** As filters or confirmation for a trend or mean-reversion rule, not as stand-alone predictors.
- **Watch out for:** Oscillators can stay overbought in strong trends; RSI and MACD are highly correlated with price.

### Algorithm: Cross-Sectional Momentum

- **How it works:** Rank a universe by past return (e.g. 12 months, skipping the last month) each month.
- **Rule:** Hold the top-ranked assets, avoid or short the bottom-ranked; rebalance monthly.
- **Works best when:** Information spreads slowly and winners keep winning for several months.
- **Watch out for:** Sharp 'momentum crashes' when markets reverse; turnover costs at every rebalance.

### Algorithm: Donchian Channel Breakout

- **How it works:** Track the highest high and lowest low of the last n bars (n = 20 here).
- **Rule:** Close above the 20-day high: buy the breakout. Exit below the 20-day low (or a trailing stop).
- **Works best when:** New trends start with a break of a range - the rule used by the 1980s 'Turtle Traders'.
- **Watch out for:** False breakouts in choppy markets; the channel must use PREVIOUS bars only (no look-ahead).

### Algorithm: VWAP and TWAP Execution

- **How it works:** Split a large parent order into child orders through the day to reduce market impact.
- **Rule:** TWAP: equal slices per time interval. VWAP: slices proportional to the typical volume curve.
- **Works best when:** Working client or fund orders too large to trade at once; benchmarked to the day's VWAP.
- **Watch out for:** VWAP relies on a volume forecast; both are predictable to other traders - add randomisation.

### Algorithm: Market Making

- **How it works:** Quote a bid below and an ask above the mid price at the same time.
- **Rule:** Earn the spread when both sides fill; skew quotes down when long, up when short, to cut inventory.
- **Works best when:** Liquid markets with steady two-way flow - the business of quant market makers.
- **Watch out for:** Adverse selection by better-informed traders; inventory risk in fast moves; needs low latency.

### Lab 5: Indicator Stage: Pine Script v6 Indicators and their Python Twins

*A3, K3, K7 | 25 min | stage: Indicators | folder: [`labs_lowcode/Lab05-pine-indicators/`](../labs_lowcode/Lab05-pine-indicators/)*

Plot SMA/EMA, Bollinger Bands, RSI and MACD and export a Pine Script v6 strategy for TradingView.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 05: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Overlay trend indicators**

Data > Chart for SPY: toggle sma:50, sma:200, ema:20 and bollinger.

Open: <http://localhost:8000/#/data?tab=chart&symbol=SPY&overlays=sma:50,sma:200,bollinger> (Data > Chart SPY with SMA 50/200 and Bollinger)

*Check:* Lines draw over the candles (TradingView Lightweight Charts).

**Step 2. Oscillators**

Switch the lower pane between RSI(14) and MACD.

Open: <http://localhost:8000/#/data?tab=chart&symbol=SPY&osc=macd> (Data > Chart SPY MACD)

*Check:* RSI has 30/70 guide lines; the MACD histogram changes colour above and below 0.

**Step 3. Export Pine Script v6**

Strategy Library > EMA crossover > Pine Script v6 > Copy. In TradingView open the Pine Editor, paste, 'Add to chart'.

Open: <http://localhost:8000/#/strategies?key=ema_cross> (Strategies > EMA crossover)

*Check:* TradingView shows the two EMAs; their last values match the app's chart.

**Expected in the app:** A chart with overlays and an oscillator pane, and a Pine Script pasted into TradingView whose values match.


### Lab 6: Strategy Prototype: TradingView Strategy Tester, Paper Trading from the Chart and Pipeline Reconciliation

*A2, A3, K3, K7 | 30 min | stage: Strategy prototype | folder: [`labs_lowcode/Lab06-pine-strategy-tester/`](../labs_lowcode/Lab06-pine-strategy-tester/)*

Run the same MA-crossover in TradingView's Strategy Tester and in the app, reconcile the results, and try TradingView Paper Trading.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 06: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Backtest the SMA 50/200 crossover in the app**

Run the preset backtest: SMA crossover 50/200 on SPY, Alpaca-style costs, next-bar-open fills.

Open: <http://localhost:8000/#/backtest?strategy=sma_cross&symbols=SPY&fast=50&slow=200&costs=alpaca_retail> (Backtest SPY SMA 50/200, Alpaca costs)

*Check:* About 5 round trips 2018-2025; note the net CAGR and Sharpe.

**Step 2. Run it in TradingView**

Export the SMA crossover Pine Script and add it to an AMEX:SPY daily chart. Open the Strategy Tester.

Open: <http://localhost:8000/#/strategies?key=sma_cross> (Strategies > SMA crossover > Pine)

*Check:* The Strategy Tester list of trades has the same entry dates (TradingView also fills on the next bar's open).

**Step 3. Reconcile and paper trade on TradingView**

Explain any differences (adjusted vs raw data, commission per order, slippage ticks). Optionally connect TradingView Paper Trading and place one order from the chart.

Open: <http://localhost:8000/#/backtest?strategy=sma_cross&symbols=SPY&fast=50&slow=200&costs=alpaca_retail>

*Check:* You can list at least two reasons the two backtests differ.

**Expected in the app:** Trade counts and net profit that agree within the expected differences (fills, costs, data).


### Lab 7: Signal Stage: a Library of Trend, Mean-Reversion, Momentum and Breakout Signals

*A2, K3, K7 | 25 min | stage: Signals | folder: [`labs_lowcode/Lab07-technical-indicators/`](../labs_lowcode/Lab07-technical-indicators/)*

Pick and customise one strategy from each family and compare them after costs.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 07: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Trend: EMA 20/50 on SPY**

Run the preset.

Open: <http://localhost:8000/#/backtest?strategy=ema_cross&symbols=SPY&fast=20&slow=50&costs=alpaca_retail> (Backtest SPY EMA 20/50, Alpaca costs)

*Check:* Note Sharpe and max drawdown vs buy-and-hold.

**Step 2. Mean reversion: Bollinger on KO**

Run Bollinger Band mean reversion on KO (window 20, k 2.0), then change k to 1.5 and run it again. Set Benchmark to KO so the buy-and-hold figures under each metric are KO's, not SPY's.

Open: <http://localhost:8000/#/backtest?strategy=bollinger_reversion&symbols=KO&window=20&k=2> (Backtest KO Bollinger 20/2)

*Check:* Win rate is high, but losses are larger than wins - 'many small wins, rare big losses'.

**Step 3. Momentum and breakout**

On the Backtest page choose Time-series momentum, look-back 126, symbol QQQ, Benchmark QQQ, and run it. Then run the Donchian breakout on QQQ (entry 20, exit 10).

Open: <http://localhost:8000/#/backtest?strategy=donchian_breakout&symbols=QQQ&entry=20&exit=10> (Backtest QQQ Donchian 20/10)

*Check:* Open the 'Price & trades' tab: buy arrows follow 20-day highs.

**Step 4. Read each strategy's explanation**

Strategy Library: open each card and read How it works / Rule / Works best when / Watch out for.

Open: <http://localhost:8000/#/strategies>

*Check:* You can say which family suits a trending market and which a range-bound one.

**Expected in the app:** Four backtests with tuned parameters and an explanation of when each family works.


### Lab 8: Execution Stage: an Order Manager that Trades the Paper Account in Any Session

*A3, K5 | 30 min | stage: Execution | folder: [`labs_lowcode/Lab08-paper-orders/`](../labs_lowcode/Lab08-paper-orders/)*

Place market, limit, stop and bracket paper orders, including an extended-hours limit order, and follow each order's lifecycle.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 08: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Market order in the regular session**

Open Paper Trading > Order ticket, fill in the fields below and press Send paper order. A market order buys straight away at the current price; it is accepted in the regular session.

- **Account:** Default paper account - the simulator's built-in paper broker (not TradingView). Keep it for every step: Session (sim) works only on this account, while the Alpaca paper account always uses the real clock.
- **Symbol:** SPY
- **Side:** buy
- **Qty:** 10
- **Type:** market
- **Time in force:** day
- **Limit price, Stop price:** leave blank
- **extended hours:** leave unticked
- **Bracket take-profit, Bracket stop-loss:** leave blank
- **Session (sim):** regular - pretends New York is in its regular session (21:30-04:00 Singapore time, 22:30-05:00 in winter); 'real clock' uses the actual time

Open: <http://localhost:8000/#/trading?tab=ticket> (Paper Trading > Order ticket)

*Check:* The Result panel shows ACCEPTED - all checks passed, 'BUY 10 SPY MARKET DAY -> filled', and each risk check (kill_switch, duplicate, session, allow_list, long_only, daily_loss, max_order_qty, max_order_value, max_position_pct) marked ok.

**Step 2. Extended-hours limit order (Singapore class hours)**

Keep the Step 1 ticket and change only the fields below, then press Send paper order. Session (sim) = overnight pretends New York is in its overnight session - where it is during Singapore class hours. Only LIMIT orders are accepted then, so 'auto' builds one for you: time in force DAY, extended hours on, and a limit price 0.25% (25 bps) above the ask for a buy, which caps the price you pay. Then send a market order in the same session to see it blocked.

- **Type:** auto (session-aware)
- **Session (sim):** overnight
- **Limit price:** leave blank - auto sets it from the quote
- **extended hours:** leave unticked - auto switches it on
- **Everything else:** as in Step 1
- **Second send:** Type = market, Session (sim) still overnight

Open: <http://localhost:8000/#/trading?tab=ticket>

*Check:* First send: ACCEPTED, 'BUY 10 SPY LIMIT DAY extended_hours limit <price> -> filled'; the Orders tab shows 'limit day ext-hrs', session overnight. Second send (market): BLOCKED - the session check reads 'overnight session accepts only LIMIT orders with extended_hours=True'.

**Step 3. Bracket order**

A bracket order is an entry plus two automatic exits: a take-profit (a sell limit above the price, to lock in a gain) and a stop-loss (a sell stop below it, to cap a loss). Brackets are accepted in the regular session only, and both exit prices must be filled in. Fill in the fields below and press Send paper order, then open the Orders tab and click each status badge to see that order's lifecycle.

- **Qty:** 5
- **Type:** market
- **Session (sim):** regular
- **Bracket take-profit:** about 3% above the current SPY price - e.g. SPY at 770 -> 793.10 (read the price in the Fill column of your Step 1 order)
- **Bracket stop-loss:** about 2% below it - e.g. SPY at 770 -> 754.60
- **Limit price, Stop price:** leave blank
- **extended hours:** leave unticked
- **Everything else:** as in Step 1

Open: <http://localhost:8000/#/trading?tab=ticket>

*Check:* Orders tab: the parent 'buy 5 SPY market day bracket' is filled, and two sell legs appear with status new - 'limit gtc bracket (leg)' at the take-profit and 'stop gtc bracket (leg)' at the stop-loss. They were held until the parent filled; when one leg fills, the other is cancelled (one-cancels-other).

**Step 4. Queue while closed and cancel**

Session (sim) = closed pretends the US market is shut (weekends and US holidays). 'auto' turns the order into a GTC (good-till-cancelled) limit order that queues for the next session instead of filling. First clear the two bracket fields - the ticket keeps them from Step 3. Press Send paper order, then open the Orders tab and cancel the queued order.

- **Qty:** 10
- **Type:** auto (session-aware)
- **Session (sim):** closed
- **Bracket take-profit, Bracket stop-loss:** clear both (blank)
- **Limit price:** leave blank - auto sets it
- **Time in force:** leave as day - auto changes it to gtc
- **Everything else:** as in Step 1
- **Then:** Orders tab > the new 'limit gtc' row (status accepted) > press the red cancel at the right-hand end

Open: <http://localhost:8000/#/trading?tab=ticket>

*Check:* Result: ACCEPTED, 'BUY 10 SPY LIMIT GTC limit <price> -> accepted', and the session check reads 'market closed - GTC limit order will queue for the next session'. After cancel the status is canceled; click the badge to see new -> accepted -> canceled. Tip: while the real US market is open (21:30-04:00 Singapore time) the simulator's background market can fill a queued order within a minute - cancel straight away, or send it again if it already filled.

**Expected in the app:** A blotter with filled, working, queued and cancelled orders and the risk checks for each.


### Lab 9: Evaluation Stage: Performance and Risk Metrics with a Benchmark Table

*A3, K3 | 25 min | stage: Evaluation | folder: [`labs_lowcode/Lab09-performance-metrics/`](../labs_lowcode/Lab09-performance-metrics/)*

Read the full metrics table and compare a strategy with buy-and-hold.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 09: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Open the analytics**

Analytics: choose the EMA 10/30 seeded backtest. Hover every metric for its formula.

Open: <http://localhost:8000/#/analytics> (Analytics)

*Check:* You can define Sharpe, Sortino, Calmar, max drawdown, profit factor, expectancy, exposure and turnover.

**Step 2. Compare with buy-and-hold**

Tick the EMA backtest and 'Buy and hold SPY' and press Compare.

Open: <http://localhost:8000/#/analytics>

*Check:* Buy-and-hold has higher CAGR but a deeper drawdown; the strategy has lower exposure.

**Step 3. Glossary**

Open Help & Glossary > Metric glossary.

Open: <http://localhost:8000/#/help?tab=glossary>

*Check:* Each formula matches the course slides.

**Expected in the app:** A metrics table you can explain line by line.


## Topic 3: Machine Learning Models, Statistical Modelling and A/B Testing for Trading Signals

**Learning outcome:** Conduct statistical modelling of market data with machine learning models to derive patterns and solutions, and perform A/B testing of trading strategies based on different hypotheses.


### 3.1 Types of Statistical Analyses, Data Models, Algorithms and Computational Methods

- Descriptive analysis summarises what happened (mean return, volatility, skew, correlation); inferential analysis tests whether an effect is real (t-test, bootstrap); predictive analysis forecasts (regression, classification); prescriptive analysis decides (optimisation).
- Supervised learning learns a mapping from features to a known target - regression for a continuous target (tomorrow's return), classification for a category (up or down).
- Unsupervised learning finds structure without a target - clustering (market regimes) and dimensionality reduction (PCA of a yield curve or a sector basket).
- Reinforcement learning learns a policy from rewards by interacting with an environment - used in research for execution and portfolio allocation, but data-hungry and fragile.
- Advanced computational methods: grid and random search over strategy parameters, Monte Carlo simulation and bootstrapping, walk-forward optimisation, and gradient-boosted ensembles.
- Strategy search is itself an algorithm: testing many parameter combinations on in-sample data and then confirming only the best few out of sample - always counting how many combinations were tried.

### 3.2 Supervised Learning Models for Trading Signals

- Target and features: the target is what you predict (next-day direction); the features are what you know at prediction time (lagged returns, RSI, MACD, volatility, volume change). Any feature using future data is leakage.
- Linear regression predicts a continuous return as a weighted sum of features; logistic regression outputs the probability of an up day and is a strong, interpretable baseline.
- Naive Bayes applies Bayes' theorem with an independence assumption; fast and surprisingly useful for text such as news headlines.
- Decision trees split the data on feature thresholds; random forests average many decorrelated trees; XGBoost builds trees sequentially, each correcting the last - typically the strongest tabular models.
- Neural networks (multi-layer perceptrons, LSTMs, Transformers) can model non-linear and sequential patterns, but need far more data and are easy to overfit on daily prices.
- Evaluation: accuracy, precision, recall, F1 and ROC AUC for classifiers; RMSE and R-squared for regressors. In trading, a model is judged finally by its net-of-cost strategy performance, not by accuracy alone.
- Turning probabilities into positions: go long when P(up) exceeds a threshold such as 0.55, stay flat otherwise, and re-train on a rolling window.

### 3.3 Unsupervised Learning: Clustering and PCA for Market Regimes

- K-means clustering partitions observations into k groups by minimising within-cluster variance. Applied to rolling return and volatility features it separates calm-bull, choppy and stressed market regimes.
- Hierarchical clustering builds a tree (dendrogram) of similarity - used to group correlated assets and to build more diversified portfolios.
- Principal Component Analysis (PCA) finds orthogonal combinations that explain the most variance. For equities the first component is usually 'the market'; for yield curves the first three are level, slope and curvature.
- Always standardise features before clustering or PCA, and choose k with the elbow method or silhouette score - then name the clusters by inspecting their average characteristics.
- Regime-aware trading: run trend following in trending regimes and mean reversion in range-bound ones, or cut position size in the high-volatility regime.
- Clusters found on the whole history use future information; for trading, fit the clustering on past data only and assign new observations as they arrive.

### 3.4 Statistical Modelling Techniques for Financial Time Series

- Returns, not prices: model log or simple returns, which are closer to stationary. Prices trend and wander; regressions on raw prices produce spurious results.
- Stylised facts of returns: fat tails, volatility clustering, weak autocorrelation of returns but strong autocorrelation of absolute returns. Normal-distribution assumptions understate tail risk.
- Time-ordered validation: never shuffle a time series. Use a chronological train / validation / test split, scikit-learn's TimeSeriesSplit, or walk-forward analysis that re-fits as time advances.
- Feature engineering: lagged returns, rolling statistics, indicator values, calendar effects and cross-asset features - each computed only from data available at the decision time.
- Regularisation (L1/L2 penalties, tree depth limits, early stopping) controls overfitting; fewer, well-motivated features usually beat many.
- Classical time-series models - autoregression (AR), ARIMA and GARCH for volatility - remain useful baselines against which a machine learning model must prove its value.

### 3.5 A/B Testing Trading Strategies

- An A/B test compares variant A (for example a 20/50 crossover) with variant B (a 10/30 crossover, or the same rule with an RSI filter) on the same data and period, to decide whether B is genuinely better.
- State the hypotheses first: H0 - the mean daily returns (or Sharpe ratios) are equal; H1 - variant B's is higher. Choose the significance level (commonly 5%) before running the test.
- Tests: Welch's t-test on daily returns; a paired test on the daily return difference; and a bootstrap confidence interval for the Sharpe difference, which does not assume normality.
- Interpretation: a p-value below 0.05 rejects H0; a confidence interval for the difference that excludes zero tells the same story with a size attached. Statistical significance is not economic significance - check the effect after costs.
- Multiple testing: trying 100 variants will produce about 5 'significant' results by chance. Apply a Bonferroni correction or hold out a final test period.
- Live A/B testing: run both variants side by side in separate paper accounts during forward testing to compare them on unseen data.

### 3.6 Pairs Trading: Statistical Arbitrage as a Hedging Algorithm

- Pairs trading holds one stock long and an economically linked stock short, in hedge-ratio proportion. Market moves that hit both legs largely cancel, so the position is a hedge: its profit or loss comes from the spread between the two, not from the direction of the market.
- Origins: pioneered by Gerry Bamberger and developed by Nunzio Tartaglia's quantitative group at Morgan Stanley in the 1980s; still used by statistical-arbitrage funds.
- Cointegration, not correlation: two prices are cointegrated when a weighted combination of them is stationary. Highly correlated stocks can still drift apart for ever; only a cointegrated spread is expected to revert.
- Engle-Granger method: (1) regress log price A on log price B - the slope is the hedge ratio and the residual is the spread; (2) run an ADF unit-root test on the residual. A test statistic below the Engle-Granger critical value (about -3.34 at 5%) indicates cointegration.
- Trading rule: standardise the spread as a z-score over a rolling window; go short the spread (short A, long B) when z > +2, long the spread when z < -2, and exit as z returns towards 0 (for example |z| < 0.5). Trade both legs on the next bar and charge costs on both.
- Evidence: Gatev, Goetzmann and Rouwenhorst (2006) found a simple pairs rule on US stocks earned average annualised excess returns of up to 11% from 1962 to 2002; later studies find smaller and less consistent profits.
- Risks: the relationship can break (re-test cointegration on a rolling basis), the hedge ratio drifts, costs are paid twice, short positions incur borrow costs, and screening many pairs creates false discoveries.

### Algorithm: Logistic Regression for Direction

- **How it works:** Fits P(up tomorrow) = 1 / (1 + e^-(b0 + b1 x1 + ...)) from features known today.
- **Rule:** Go long when P(up) exceeds a threshold such as 0.55; otherwise stay flat.
- **Works best when:** A transparent baseline: each coefficient shows how a feature moves the probability.
- **Watch out for:** Only linear effects unless you engineer features; daily direction is close to a coin toss.

### Algorithm: Decision Tree and Random Forest

- **How it works:** A tree splits the data on feature thresholds (e.g. RSI < 30) into leaves with an up/down share.
- **Rule:** A random forest averages hundreds of trees, each grown on a random sample of rows and features.
- **Works best when:** Non-linear, interacting signals - e.g. oversold AND low volatility.
- **Watch out for:** Deep trees memorise noise; limit depth and leaf size and validate walk-forward.

### Algorithm: Gradient Boosting (XGBoost)

- **How it works:** Builds trees one after another; each new tree corrects the errors of the ensemble so far.
- **Rule:** Prediction = sum of many small trees x learning rate; stop early when test loss stops falling.
- **Works best when:** Tabular features such as returns, indicators and volatility - usually the strongest model.
- **Watch out for:** Training loss keeps falling while test loss rises: classic overfitting (see the chart).

### Algorithm: K-Means Clustering for Market Regimes

- **How it works:** Groups days into k clusters by minimising the distance of each day to its cluster centre.
- **Rule:** Features: rolling return and volatility (standardised). Name clusters by their averages.
- **Works best when:** Switching or sizing strategies by regime: trend in calm markets, cut risk when stressed.
- **Watch out for:** Fit on past data only; choose k with the elbow or silhouette method; regimes shift.

### Algorithm: Principal Component Analysis (PCA)

- **How it works:** Finds uncorrelated combinations of assets that explain the most variance of returns.
- **Rule:** PC1 of a stock universe is 'the market'; later PCs are sector or style factors.
- **Works best when:** Reducing many correlated features; building factor-neutral and pairs portfolios.
- **Watch out for:** Standardise first; components change over time; PCs are statistical, not economic, factors.

### Method: Walk-Forward Validation

- **How it works:** Train on a past window, test on the next unseen block, then roll forward and repeat.
- **Rule:** Never shuffle time series; each test block is genuinely out of sample.
- **Works best when:** Estimating how a model or parameter set would really have performed live.
- **Watch out for:** Overlapping targets leak information - leave a gap between train and test.

### Method: A/B Testing Two Strategy Variants

- **How it works:** Compare variant A and B on the same days: H0 'no difference' vs H1 'B is better'.
- **Rule:** Welch / paired t-test on daily returns; bootstrap a 95% CI of the Sharpe difference.
- **Works best when:** Deciding which parameter set or filter to promote to paper trading.
- **Watch out for:** If the CI contains 0, do not reject H0; testing 100 variants gives ~5 false winners.

### Algorithm: Pairs Trading (Hedged Statistical Arbitrage)

- **How it works:** Long one stock, short a cointegrated partner in hedge-ratio proportion: market moves cancel.
- **Rule:** Spread z > +2: short A / long B. z < -2: long A / short B. Exit as z returns to 0.
- **Works best when:** Economically linked stocks (KO/PEP) whose spread has a stable mean.
- **Watch out for:** Cointegration can break; costs on both legs; short-borrow; screening many pairs.

### Lab 10: Strategy-Search Stage: Grid Search, Out-of-Sample Ranking and Decay

*A2, A4, K2 | 20 min | stage: Strategy search | folder: [`labs_lowcode/Lab10-strategy-grid-search/`](../labs_lowcode/Lab10-strategy-grid-search/)*

Grid-search SMA crossover parameters in-sample and measure how the ranking decays out of sample.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 10: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Run the grid**

Research > Strategy search: SMA crossover on SPY, in-sample to 2021-12-31, Alpaca costs. Press Search.

Open: <http://localhost:8000/#/research/grid?strategy=sma_cross&symbol=SPY> (Research > Grid SPY SMA cross)

*Check:* About 24 parameter sets; two heatmaps appear.

**Step 2. Read the decay**

Compare the in-sample and out-of-sample heatmaps and the IS->OOS rank correlation.

Open: <http://localhost:8000/#/research/grid>

*Check:* You can explain why the single best in-sample cell is usually not the best out of sample, and why a robust region is preferred.

**Step 3. Walk-forward**

Research > Walk-forward: SMA crossover on SPY (3-year train, 1-year test).

Open: <http://localhost:8000/#/research/walkforward?strategy=sma_cross> (Research > Walk-forward SPY)

*Check:* The stitched out-of-sample equity curve and the parameters chosen in each window.

**Expected in the app:** IS and OOS Sharpe heatmaps, a rank correlation and a robust parameter region.


### Lab 11: ML-Signal Stage: a Walk-Forward Classifier from Probability to Position

*A4, K4, K6 | 20 min | stage: ML signal | folder: [`labs_lowcode/Lab11-ml-signal-classifier/`](../labs_lowcode/Lab11-ml-signal-classifier/)*

Train logistic regression, random forest and XGBoost walk-forward and trade P(up) > threshold.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 11: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Train the classifiers**

Research > ML models on SPY, threshold 0.55.

Open: <http://localhost:8000/#/research/ml> (Research > ML SPY)

*Check:* AUC close to 0.5 - daily direction is close to a coin toss; read the verdict.

**Step 2. Backtest an ML strategy**

Backtest 'ML: XGBoost (walk-forward)' on SPY.

Open: <http://localhost:8000/#/backtest?strategy=ml_xgboost&symbols=SPY> (Backtest SPY XGBoost)

*Check:* Judge the model by the net-of-cost strategy, not by accuracy.

**Step 3. Check for leakage**

Research > Diagnostics on 'ML: logistic regression'.

Open: <http://localhost:8000/#/research/diagnostics?strategy=ml_logistic>

*Check:* Look-ahead check PASS: refits use only past bars.

**Expected in the app:** Accuracy / AUC table, feature importance and a net-of-cost backtest of the ML signal.


### Lab 12: Regime-Filter Stage: PCA and K-Means as a Gate on the Signals

*A4, K4, K6 | 15 min | stage: Regime filter | folder: [`labs_lowcode/Lab12-market-regimes/`](../labs_lowcode/Lab12-market-regimes/)*

Find market regimes with walk-forward K-means and gate a signal in the high-volatility regime.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 12: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Analyse regimes**

Research > Regimes: SPY, 3 clusters, gate the EMA crossover.

Open: <http://localhost:8000/#/research/regime> (Research > Regimes SPY)

*Check:* PC1 explains the largest share of variance (the market factor); the 2020 crash is in the stress regime.

**Step 2. Backtest the regime-filtered strategy**

Backtest 'Regime-filtered strategy (K-means gate)'.

Open: <http://localhost:8000/#/backtest?strategy=regime_filtered&symbols=SPY> (Backtest SPY regime filter)

*Check:* Compare max drawdown with the ungated EMA crossover.

**Expected in the app:** PCA explained variance, a regime timeline and gated vs ungated performance.


### Lab 13: A/B-Test Stage: a Statistical Decision before Capital Moves

*A5, K2 | 15 min | stage: A/B test | folder: [`labs_lowcode/Lab13-ab-testing/`](../labs_lowcode/Lab13-ab-testing/)*

Decide statistically between two variants before moving capital.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 13: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Run the A/B test**

Research > A/B test: A = Trend filter, B = Dip buy, SPY, alpha 0.05, 20 variants tried.

Open: <http://localhost:8000/#/research/abtest?a=trend_filter&b=dip_buy> (Research > A/B trend_filter vs dip_buy)

*Check:* Read the decision; if the CI contains 0, do not reject H0.

**Step 2. Your own variants**

A = EMA crossover {"fast": 10, "slow": 30}, B = EMA crossover {"fast": 20, "slow": 50}.

Open: <http://localhost:8000/#/research/abtest?a=ema_cross&b=ema_cross>

*Check:* You can explain the Bonferroni-adjusted alpha.

**Expected in the app:** Welch and paired t-tests, a bootstrap Sharpe CI and a decision with a multiple-testing caution.


### Lab 14: Pairs Stage: a Hedged, Market-Neutral Statistical-Arbitrage Sleeve

*A4, K6 | 20 min | stage: Pairs / stat-arb | folder: [`labs_lowcode/Lab14-pairs-trading/`](../labs_lowcode/Lab14-pairs-trading/)*

Screen pairs for cointegration and backtest a market-neutral KO/PEP spread.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 14: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Screen the pairs**

Research > Pairs screen (formation to 2022-12-31).

Open: <http://localhost:8000/#/research/pairs> (Research > Pairs screen)

*Check:* High correlation does not imply cointegration - compare the corr and ADF columns.

**Step 2. Backtest KO/PEP**

Backtest the pairs strategy on KO, PEP (both legs, short leg allowed, borrow cost charged).

Open: <http://localhost:8000/#/backtest?strategy=pairs_cointegration&symbols=KO,PEP> (Backtest KO/PEP pairs)

*Check:* Beta to SPY near 0 in 'All metrics'; the trade list has long and short legs.

**Expected in the app:** An Engle-Granger screen and a pairs backtest with beta near zero.


## Topic 4: Building an End-to-End Algorithmic Trading Pipeline: Backtest, Forward Test and Performance Analysis

**Learning outcome:** Perform coding and configuration of an automated trading program based on selected models or algorithms, conduct tests on its actions and outcomes, diagnose unintended outcomes, and draw insights from the results to support decisions and report accordingly.


### 4.1 Architecture of an End-to-End Algorithmic Trading Pipeline

- The pipeline: (1) strategy search and research, (2) data ingestion, (3) signal generation, (4) backtest with costs, (5) risk checks, (6) order execution, (7) forward test on paper, (8) monitoring, logging and performance reporting.
- Configuration lives outside the code: symbols, parameters, position limits and API keys sit in a config file or environment variables, so a change is a reviewed configuration change rather than an edit to the logic.
- Pre-trade risk controls: maximum position size, maximum order value, maximum daily loss, market-hours check, duplicate-order check and a kill switch that halts all trading - the controls regulators require of algorithmic traders.
- Event sources: a scheduled job (every bar), a streaming feed (every quote), or an external alert - such as a TradingView alert sent by webhook to your own server, which then places the order through Alpaca.
- Agentic extension: analyst agents produce a view, a trader agent proposes an order, and a risk-manager agent with hard limits approves or rejects it - the LLM never bypasses the coded risk checks.
- Every decision is logged: timestamp, inputs, signal, order request, broker response and fill - the audit trail for diagnosing problems and for compliance review.

### 4.2 Backtesting with Realistic Trading Costs

- A backtest replays a strategy on historical data. Vectorised backtests are fast (whole-array operations); event-driven backtests replay bar by bar and model orders more realistically.
- Execute on the NEXT bar: a signal computed on today's close can only be traded at tomorrow's open (or later). Same-bar execution is the commonest source of look-ahead bias.
- Trading costs: commission (Alpaca charges none on US equities, but most brokers do), the bid-ask spread, slippage and market impact, and regulatory fees on sells (the US SEC Section 31 fee and FINRA Trading Activity Fee). Short positions also incur borrow costs.
- Model costs explicitly: cost per trade = commission + (half-spread + slippage) x shares x price + regulatory fees. Express them in basis points of traded value so they scale with turnover.
- Report gross and net results side by side, the cost breakdown, and the break-even cost - the cost per trade at which the strategy stops making money.
- A strategy whose edge disappears at 5 to 10 basis points per trade is not tradeable for most desks, however good its gross Sharpe ratio looks.

### 4.3 Forward Testing with Automated Paper Trading

- Forward testing (paper trading) runs the strategy in real time on data it has never seen, placing simulated orders - the bridge between a backtest and live capital.
- The automated bot loop: wait for the bar to close; fetch the latest bars; compute the signal; run the risk checks; compare the target position with the actual position; submit the buy or sell order; read the order status; log everything; sleep until the next bar.
- Alpaca's market clock (is the market open?) and calendar prevent orders outside trading hours; the pattern-day-trader rule applies to paper accounts under USD 25,000 as it does to live ones.
- Run the forward test long enough to see a meaningful number of trades - weeks for a daily strategy - and compare its fills, slippage and returns with what the backtest predicted for the same period.
- Run variants side by side in separate paper accounts as a live A/B test, and only promote a strategy to live trading through a documented review.

### 4.4 Potential Reasons for Unintended Outcomes and How to Diagnose Them

- Overfitting: parameters tuned to noise. Signs - a spectacular in-sample Sharpe that collapses out of sample, and performance that is very sensitive to small parameter changes.
- Look-ahead bias: using information not available at the decision time - same-bar execution, centred rolling windows, or features normalised with full-sample statistics.
- Survivorship bias: testing only on today's index members, which excludes the companies that failed. Data-snooping bias: reporting the best of many tests without adjustment.
- Cost and execution drag: under-estimated spread and slippage, partial fills and rejected orders. Signs - paper or live returns persistently below the backtest by roughly the turnover x cost.
- Regime change and concept drift: the market behaves differently from the training period (2020 COVID volatility, the 2022 rate-hiking cycle). Monitor rolling performance and feature distributions.
- Data and software errors: unadjusted splits, time-zone mismatches, missing bars, duplicated orders, and stale positions after a restart. Knight Capital's 2012 loss came from obsolete code activated by a deployment error.
- Diagnosis method: reproduce the result, isolate the first step where it diverges from expectation (data, signal, order, fill), compare against a benchmark or a known-good run, fix, then re-test.

### 4.5 Performance Analysis, Insights and Reporting

- A tearsheet presents the equity curve against the benchmark, the drawdown chart, monthly returns, rolling Sharpe ratio, the metrics table and the cost breakdown on one page.
- Compare backtest and forward test for the same period: did the live fills, number of trades and returns behave as the backtest predicted? Explain every material gap.
- Draw insights, not just numbers: in which regimes did the strategy earn its returns, what drove its drawdowns, how sensitive is it to costs and parameters, and how correlated is it with the desk's existing book?
- Report for the decision-maker: lead with the recommendation (promote, extend the forward test, modify or retire), support it with three or four key figures, and state the risks and limitations plainly.
- Keep a model record: hypothesis, data, parameters, test results, version and approval - the documentation an investment committee and model-risk reviewer expect.

### Historical Data: Backtest, Tune, Then Forward Test

- **Backtest on history:** Replay the strategy's rules over past prices - next-bar fills, trading costs - to see how it would have performed.
- **Tune hyperparameters (in-sample):** Search the settings (MA lengths, RSI levels, model parameters) on the OLDER history only, by grid search or walk-forward.
- **Confirm out-of-sample:** Backtest the tuned settings ONCE on later history the search never saw. A big drop from in-sample = overfitting.
- **Forward test (paper):** Run the tuned strategy on NEW data as it arrives - paper orders, real fills and risk checks - before any capital.

Historical data (2018-2025) -> Tune in-sample (2018-2021) -> Backtest once out-of-sample (2022-2024) -> Forward test on paper (2025 onward) -> Go-live decision

*Tuning on the test period, or re-tuning after seeing out-of-sample results, turns the test into more tuning - the result will look better than reality (Labs 10, 15, 16).*


### Lab 15: Backtest-Engine Stage: Cost Models, Execution Timing and Break-Even

*A7, A8, K7 | 25 min | stage: Backtest engine | folder: [`labs_lowcode/Lab15-trading-costs/`](../labs_lowcode/Lab15-trading-costs/)*

Run the same strategy under four cost models and find its break-even cost.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 15: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Zero vs Alpaca vs high-cost**

Backtest Dip buy on SPY three times with cost model zero, alpaca_retail and high_cost.

Open: <http://localhost:8000/#/backtest?strategy=dip_buy&symbols=SPY&costs=high_cost> (Backtest SPY dip-buy, high-cost route)

*Check:* The 'Costs: gross vs net' tab shows the drag; dip-buy trades often, so costs bite.

**Step 2. Break-even and execution timing**

Read the break-even one-way cost; then switch Execution to 'next bar close' and compare.

Open: <http://localhost:8000/#/backtest?strategy=dip_buy&symbols=SPY&execution=next_close>

*Check:* A strategy whose break-even is only a few bps is fragile.

**Step 3. Stops and sizing**

Open 'position sizing, stop-loss, take-profit' and run EMA 20/50 with a 5% stop and volatility-target sizing.

Open: <http://localhost:8000/#/backtest?strategy=ema_cross&symbols=SPY&fast=20&slow=50&stop_loss_pct=5&sizing=vol_target>

*Check:* The trade list shows stop_loss exits.

**Expected in the app:** Gross vs net CAGR, a cost breakdown and the break-even bps.


### Lab 16: Automation Stage: a Scheduled, Risk-Checked Forward Test and Live Paper Trading

*A7, A8, K7 | 25 min | stage: Automation | folder: [`labs_lowcode/Lab16-paper-trading-bot/`](../labs_lowcode/Lab16-paper-trading-bot/)*

Create a bot, run it on a schedule, watch orders, positions and P&L live, and halt it with the kill switch.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 16: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Create the bot**

Paper Trading > + New bot: EMA crossover 10/30 on SPY, schedule 'every 10s', simulator broker, replay from 2025-01-02.

Open: <http://localhost:8000/#/trading?new=1&strategy=ema_cross> (Paper Trading > New bot (EMA cross))

*Check:* The bot appears with status stopped.

**Step 2. Start it and watch**

Press Start. Every cycle replays one trading day: it sees bars to yesterday's close and its orders fill at today's open. Or press 'Run one cycle now' repeatedly. (If the bot does not cycle, the simulator was started without its scheduler - ask your trainer.)

Open: <http://localhost:8000/#/trading>

*Check:* Equity curve grows cycle by cycle; the Pipeline Map path lights up during each cycle.

**Step 3. Kill switch**

Press the bot's Kill switch, then try 'Run one cycle now'. Release it. Try the global kill switch in the top bar too.

Open: <http://localhost:8000/#/trading>

*Check:* Cycles report 'kill switch ON - no orders sent'; the Risk stage turns red on the Pipeline Map.

**Step 4. Backtest vs forward**

Press Compare in 'Backtest vs forward test'.

Open: <http://localhost:8000/#/trading>

*Check:* The curves track closely; you can explain the remaining gap (whole shares, fills, timing).

**Expected in the app:** A bot equity curve, a blotter of its orders, a backtest-vs-forward comparison and a tested kill switch.


### Lab 17: Event-Driven Automation: TradingView Webhook to Signal, Risk and Execution

*A7, K5, K7 | 20 min | stage: Event-driven automation | folder: [`labs_lowcode/Lab17-tradingview-webhook/`](../labs_lowcode/Lab17-tradingview-webhook/)*

Send TradingView alerts to the app's webhook and see them pass validation, signal confirmation and risk into paper orders.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 17: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Copy the alert template**

Integrations > TradingView webhook: copy the URL and the JSON alert message (reveal the secret only on your own machine).

Open: <http://localhost:8000/#/integrations> (Integrations > TradingView webhook)

*Check:* You know which placeholders TradingView fills in.

**Step 2. Run the self-test**

Press 'Run self-test (7 simulated alerts)'.

Open: <http://localhost:8000/#/integrations>

*Check:* 7/7: valid buy and sell (200), wrong secret (401), symbol not allowed and qty too large (422), malformed (400), retry ignored (200 duplicate).

**Step 3. Real alerts (paid TradingView plan)**

Optional - trainer demonstration: with a paid TradingView plan, an alert on the exported Pine strategy can post to the simulator's webhook URL once the trainer has made the simulator reachable from the internet (a public tunnel URL). Watch the trainer's alert pass validation, signal confirmation and risk into a paper order.

Open: <http://localhost:8000/#/integrations>

*Check:* The alert appears in the audit log and its order in Paper Trading > Orders (source webhook).

**Expected in the app:** 7 simulated alerts handled as expected and the audit log.


### Lab 18: Diagnostics Stage: Automated Bias Checks before Go-Live

*A9, K8 | 20 min | stage: Diagnostics | folder: [`labs_lowcode/Lab18-diagnose-bias/`](../labs_lowcode/Lab18-diagnose-bias/)*

Run the automated diagnostics on a deliberately biased strategy, fix it, and re-run.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 18: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Diagnose the biased exhibit**

Research > Diagnostics on 'Lab 18 exhibit: biased smoothed momentum' (seeded custom strategy).

Open: <http://localhost:8000/#/research/diagnostics?strategy=custom_lab18_biased_smoothed_momentum> (Research > Diagnostics (Lab 18 exhibit))

*Check:* Look-ahead (features) FAIL: rolling(center=True) uses future bars. Verdict BLOCK.

**Step 2. Fix it in the Strategy Builder**

Open the exhibit in the Strategy Builder and change the single setting center=True to center=False (or let AI fix it: use the Lab 18 Strategy Builder prompt in the Prompt Library). Validate, Save.

Open: <http://localhost:8000/#/builder?key=custom_lab18_biased_smoothed_momentum> (Strategy Builder (exhibit))

*Check:* The validation's look-ahead check now passes.

**Step 3. Re-run diagnostics**

Diagnose the fixed strategy; compare the same-bar vs next-bar Sharpe and the cost-drag row.

Open: <http://localhost:8000/#/research/diagnostics?strategy=custom_lab18_biased_smoothed_momentum>

*Check:* No FAIL on look-ahead; cost drag and overfitting WARN explained.

**Expected in the app:** A FAIL on the biased exhibit, a PASS / WARN table for the fixed version and a verdict.


### Lab 19: Monitoring and Reporting Stage: Automated Tearsheet and Backtest-vs-Forward Report

*A8, A10 | 25 min | stage: Monitoring and reporting | folder: [`labs_lowcode/Lab19-performance-report/`](../labs_lowcode/Lab19-performance-report/)*

Produce a one-page tearsheet and explain the gap between backtest and forward test.

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 19: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Export the tearsheet**

Backtest page (or Analytics) > PDF tearsheet for your best backtest; also export the equity and trades CSV.

Open: <http://localhost:8000/#/analytics> (Analytics > PDF tearsheet)

*Check:* The PDF has equity vs benchmark, drawdown, monthly heatmap, metrics and the cost table.

**Step 2. Backtest vs forward**

Analytics: select your Lab 16 bot under 'Bot (backtest vs forward)'.

Open: <http://localhost:8000/#/analytics>

*Check:* Explain every material gap (fills, sizing, costs, timing).

**Step 3. Draw insights**

Monthly heatmap: in which regimes did the strategy earn its returns, what drove its drawdowns?

Open: <http://localhost:8000/#/analytics>

*Check:* Two or three insights, not just numbers.

**Expected in the app:** A PDF tearsheet and a written explanation of the backtest-vs-forward differences.


### Lab 20: Capstone: One Command Runs the Pipeline End to End, with an Agentic Layer and Human Approval

*A7, A10, K1 | 20 min | stage: End-to-end pipeline | folder: [`labs_lowcode/Lab20-agentic-capstone/`](../labs_lowcode/Lab20-agentic-capstone/)*

Run the whole pipeline end to end, get a human-approved proposal from the multi-agent desk, switch on the always-on agent, and create, backtest and forward-test your own strategy (from a template or written for you by AI).

#### Lab Steps - In the Trading Simulator

*No coding is needed. Make sure the Trading Simulator is running (installed once - see the guide 'Download, Install and Start the Trading Simulator Software') and open http://localhost:8000. In the sidebar open Course Labs > Lab 20: the app shows the same steps with a Go button that opens each page pre-filled. Every step works offline on the bundled demo data and the built-in paper broker.*

**Step 1. Run the multi-agent desk**

AI Agents > Run multi-agent analysis on NVDA, AAPL, SPY. Read each agent's card: three analysts, the two-round bull/bear debate, the trader, the risk manager, the hard-limit gate (code) and the portfolio manager.

Open: <http://localhost:8000/#/agents> (AI Agents > desk)

*Check:* Eight agent entries per symbol plus the code gate; the brain badge shows which provider or rules answered.

**Step 2. Human approval**

Approve (or reject) the proposals. Approved buys become paper bracket orders in the regular session or extended-hours limit orders overnight.

Open: <http://localhost:8000/#/agents>

*Check:* Run status 'executed' and the orders visible in Paper Trading (source agent).

**Step 3. Always-on agent**

AI Agents > Always-on agent: enable it with a 60-minute wake-up (the worker must run), or press 'Wake it now'. Check Memory.

Open: <http://localhost:8000/#/agents>

*Check:* A new always_on run and memory notes appear.

**Step 4. Create your own strategy**

Strategy Builder: start from a template and change only its parameters - or describe your idea in the Lab 20 prompt of the Prompt Library and paste the code the AI writes. Validate (look-ahead check), Save.

Open: <http://localhost:8000/#/builder?template=ema_rsi> (Strategy Builder (EMA + RSI template))

*Check:* Your strategy appears in the Strategy Library with an auto-generated parameter form.

**Step 5. Backtest, diagnose and forward-test it**

Backtest it, run Diagnostics, then create a paper bot for it and start it.

Open: <http://localhost:8000/#/trading?new=1>

*Check:* Pipeline Map > Strategy lifecycle for your strategy shows the gates it passed.

**Step 6. End-to-end on the Pipeline Map**

Open the Pipeline Map and press 'Run a bot cycle'. Then switch to 'Strategy lifecycle'.

Open: <http://localhost:8000/#/pipeline> (Pipeline Map)

*Check:* All 14 stages have run; you can walk a colleague through each stage.

**Expected in the app:** A Pipeline Map with every stage green, an approved agent proposal with its decision trace, and your custom strategy trading on paper.


## References

- [OpenClaw](https://en.wikipedia.org/wiki/OpenClaw)
- [Turing Post - What is Hermes Agent (Nous Research)](https://www.turingpost.com/p/hermes)
- [TechCrunch - OpenAI launches Dots (29 Sep 2026)](https://techcrunch.com/2026/09/29/openai-launches-dots-its-bubbly-agentic-avatar/)
- [D. E. Shaw & Co.](https://en.wikipedia.org/wiki/D._E._Shaw_%26_Co.)
- [Two Sigma](https://en.wikipedia.org/wiki/Two_Sigma)
- [Man AHL - who we are](https://www.man.com/ahl)
- [IFR - Jane Street thrives amid record trading](https://www.ifre.com/bonds/2246615/jane-street-thrives-amid-record-trading-bonanza)
- [IFR - Flow market maker: Citadel Securities](https://www.ifre.com/ifr-awards/2327839/flow-marketmaker-citadel-securities)
- [TradingView - Paper Trading main functionality](https://www.tradingview.com/support/solutions/43000516466-paper-trading-main-functionality/)
- [Alpaca - Trade with Alpaca on TradingView](https://alpaca.markets/learn/trade-with-alpaca-on-tradingview)
- [Alpaca - 24/5 trading](https://docs.alpaca.markets/us/docs/245-trading)
- [Alpaca - crypto spot trading (24/7)](https://docs.alpaca.markets/us/docs/crypto-trading)
- [Vaswani et al. (2017) Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Xiao et al. (2024) TradingAgents](https://arxiv.org/abs/2412.20138)
- [TradingAgents GitHub](https://github.com/TauricResearch/TradingAgents)
- [Open Finance Lab: AgenticTrading](https://github.com/Open-Finance-Lab/AgenticTrading)
- [Treleaven, Galas & Lalchand (2013) Algorithmic Trading Review](https://cacm.acm.org/research/algorithmic-trading-review/)
- [MathWorks: algorithmic trading](https://www.mathworks.com/discovery/algorithmic-trading.html)
- [ScienceDirect Topics: algorithmic trading](https://www.sciencedirect.com/topics/economics-econometrics-and-finance/algorithmic-trading)
- [Pepperstone: algorithmic trading](https://pepperstone.com/en-gb/learn-to-trade/glossary/algorithmic-trading)
- [IG: algorithmic trading](https://www.ig.com/en/trading-platforms/algorithmic-trading)
- [Equiti: guide to algorithmic trading](https://www.equiti.com/sc-en/news/trading-ideas/guide-to-algorithmic-trading/)
- [DBS: what is algorithmic trading (2026)](https://www.dbs.bank.in/in/treasures/articles/learning-centre/algorithmic-trading)
- [SEC & CFTC: Findings on the 6 May 2010 market events](https://www.sec.gov/news/studies/2010/marketevents-report.pdf)
- [SEC: Knight Capital market access charges (2013)](https://www.sec.gov/news/press-release/2013-222)
- [Nasdaq: Regulation NMS FAQ](https://nasdaqtrader.com/content/marketregulation/regnms/regnms_faqs.pdf)
- [SEC: decimalisation completed 9 Apr 2001](https://www.sec.gov/news/speech/spch509.htm)
- [Overdahl & McMillan (1998) NYSE Rule 80A](https://ideas.repec.org/a/ucp/jnlbus/v71y1998i1p27-53.html)
- [Commission Delegated Regulation (EU) 2017/589 (MiFID II RTS 6)](https://eur-lex.europa.eu/eli/reg_del/2017/589/oj)
- [Regulation Asia: SGX RegCo algorithmic trading guide (2020)](https://www.regulationasia.com/sgx-regco-publishes-regulatory-guide-on-algorithmic-trading/)
- [Alpaca: commission-free API brokerage (2018)](https://alpaca.markets/blog/commission-free-api-stock-algorithmic-trading/)
- [Wu et al. (2023) BloombergGPT](https://arxiv.org/abs/2303.17564)
- [TradingView: Pine Script v6 has landed (Dec 2024)](https://www.tradingview.com/blog/en/pine-script-v6-has-landed-48830/)
- [MAS: FEAT Principles (Nov 2018)](https://www.mas.gov.sg/news/media-releases/2018/mas-introduces-new-feat-principles-to-promote-responsible-use-of-ai-and-data-analytics)
- [MAS: Guidelines on AI Risk Management (Oct 2026)](https://www.mas.gov.sg/regulation/guidelines/guidelines-on-artificial-intelligence-risk-management-for-financial-institutions)
- [Markowitz (1952) Portfolio Selection, Journal of Finance](https://www.math.hkust.edu.hk/~maykwok/courses/ma362/07F/markowitz_JF.pdf)
- [Cboe - The creation of listed options (1973)](https://www.cboe.com/insights/posts/the-creation-of-listed-options-at-cboe)
- [Black-Scholes model history](https://www.macroption.com/black-scholes-history/)
- [Princeton Newport Partners (Thorp)](https://en.wikipedia.org/wiki/Princeton_Newport_Partners)
- [UCI Libraries - Edward O. Thorp career exhibit](https://exhibits.lib.uci.edu/thorp/career)
- [MSCI - Factor indexing through the decades (Barra)](https://www.msci.com/downloads/web/msci-com/research-and-insights/paper/factor-indexing-through-the-decades/factor-indexing-through-the-decades.pdf)
- [Renaissance Technologies](https://en.wikipedia.org/wiki/Renaissance_Technologies)
- [Pairs trade (Bamberger, Tartaglia, Morgan Stanley)](https://en.wikipedia.org/wiki/Pairs_trade)
- [Gatev, Goetzmann & Rouwenhorst - Pairs Trading (NBER w7032)](https://nber.org/papers/w7032)
- [Long-Term Capital Management](https://en.wikipedia.org/wiki/Long-Term_Capital_Management)
- [Khandani & Lo - What Happened to the Quants in August 2007?](https://www.nber.org/system/files/working_papers/w14465/w14465.pdf)
- [Island ECN](https://en.wikipedia.org/wiki/Island_ECN)
- [UNSW BusinessThink - speed bumps and HFT (Spread Networks, microwave)](https://www.businessthink.unsw.edu.au/articles/how-speed-bumps-are-curbing-high-frequency-traders)
- [IEX (350-microsecond speed bump; SEC approval 2016)](https://en.wikipedia.org/wiki/IEX)
- [SEC (2010) Concept Release on Equity Market Structure, Release 34-61358](https://www.sec.gov/files/rules/concept/2010/34-61358.pdf)
- [Lopez-Lira & Tang - Can ChatGPT Forecast Stock Price Movements?](https://arxiv.org/abs/2304.07619)
- [Glasserman & Lin - Look-ahead bias in GPT sentiment](https://arxiv.org/abs/2309.17322)
- [Alpha-GPT - human-AI interactive alpha mining](https://arxiv.org/abs/2308.00016)
- [FinMem - LLM trading agent with layered memory](https://arxiv.org/abs/2311.13743)
- [FinAgent - multimodal foundation agent for trading](https://arxiv.org/abs/2402.18485)
- [StockAgent - LLM stock trading in simulated markets](https://arxiv.org/abs/2407.18957)
- [QuantAgent - multi-agent LLMs for high-frequency trading](https://arxiv.org/abs/2509.09995)
- [AI Hedge Fund (open source)](https://github.com/virattt/ai-hedge-fund)
- [Chain-of-Alpha (2025) - LLM alpha mining, reviews Alpha-GPT and AlphaAgent](https://arxiv.org/abs/2508.06312)
