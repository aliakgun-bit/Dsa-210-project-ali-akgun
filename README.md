# Dsa-210-project-ali-akgun
DSA210 Data Science Term Project
# Motivation
When a CEO is forced out of a company, it sends a direct signal to the market — but does the market actually react, and if so, how? Some dismissals are welcomed by investors as a necessary course correction; others create uncertainty and drive the stock price down. Understanding this dynamic has implications both for corporate governance research and for evaluating whether a short-term trading opportunity exists around these events.
This project investigates how stock prices of S&P 1500 companies react to forced CEO departures using an event study methodology. By calculating Cumulative Abnormal Returns (CAR) around dismissal dates and testing whether the reaction varies by departure type, crisis periods, and historical trends, I aim to quantify the market's response to CEO turnover.

# Data Source
The primary dataset is the CEO Dismissal Database compiled by Gentry, Harrison, Quigley & Boivie (2021), published in the Strategic Management Journal, Vol. 42(5), pp. 968-991.

Source: Kaggle / Zenodo (DOI: 10.5281/zenodo.4543893)
Coverage: S&P 1500 CEO departures, 1992–2019
Size: 9,390 departure records across 3,860 unique companies
Key variable: ceo_dismissal flag (1 = forced out, 0 = voluntary)

To study stock market reactions, I enriched the dataset by:

Mapping company identifiers (gvkey) to stock tickers via manual matching and notes extraction (29.6% match rate for dismissal events)
Downloading daily stock prices around each dismissal event using yfinance
Calculating abnormal returns using the market model with S&P 500 as benchmark

# Data Characteristics
Our analysis sample: 405 forced dismissals with matched tickers (1995–2019)
After price data collection & cleaning: ~210 events with valid CAR calculations
Outlier removal: Events with |CAR| > 100% excluded as data errors (delisted/wrong ticker matches)

# Research Questions
Main Question
Does the stock market exhibit a statistically significant reaction to forced CEO departures?
Sub-Questions

1.) Is the short-term abnormal return (CAR) following a CEO dismissal significantly negative?

2.) Does the market reaction differ by departure type (forced retirement vs interim replacement)?

3.) Is there evidence of mean reversion — do initial overreactions reverse in subsequent weeks?

4.) Are dismissal reactions more severe during financial crisis periods?

5.) Has the frequency of CEO dismissals increased over time?
