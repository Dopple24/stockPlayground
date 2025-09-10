from threading import Thread

import yfinance as yf
import pandas as pd
import time

# Read the TXT file (pipe-delimited)
df = pd.read_csv("nasdaqTickers.txt", sep="|")

# Extract just the tickers as a list (from the 'Symbol' column)
tickers = df["Symbol"].tolist()

batch_size = 50
batches = []

for i in range(0, len(tickers), batch_size):
    batch = tickers[i:i + batch_size]
    batches.append(batch)

# Now 'batches' is a list of lists
print("Number of batches:", len(batches))
print("First batch:", batches[0])

all_data = []

for batch in batches:
    # Batch request using yf.Tickers
    stockData = yf.Tickers(" ".join(batch))

    # Loop over each ticker in the batch
    for t_symbol, t_obj in stockData.tickers.items():
        try:
            info = t_obj.info

            # ---- 1. Price ----
            price = info.get("currentPrice")

            # ---- 2. Earnings Yield (/10) ----
            net_income = t_obj.financials.loc["Net Income"].iloc[0]
            shares = info.get("sharesOutstanding")
            eps = net_income / shares if shares else None
            earnings_yield = (eps / price * 100) if (eps and price) else None

            # ---- 3. PEG ----
            # Earnings Growth Rate
            net_income_prev = t_obj.financials.loc["Net Income"].iloc[1]
            eps_prev = net_income_prev / shares if shares else None
            growth_rate = ((eps - eps_prev) / eps_prev * 100) if eps_prev else None
            pe = (price / eps) if eps else None
            peg = (pe / growth_rate) if (pe and growth_rate and growth_rate) else None

            # ---- 4. Debt/Equity ----
            total_debt = t_obj.balance_sheet.loc["Total Debt"].iloc[0]
            bs = t_obj.balance_sheet

            # Try multiple possible labels
            equity_labels = ["Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"]
            equity = None
            for label in equity_labels:
                if label in bs.index:
                    equity = bs.loc[label].iloc[0]
                    break
            # Optional fallback to book value
            if equity is None:
                equity = t_obj.info.get("bookValue")

            de_ratio = (total_debt / equity) if (total_debt and equity and equity != 0) else None

            # ---- 5. Revenue Growth (/10) ----
            revenue_curr = t_obj.financials.loc["Total Revenue"].iloc[0]
            revenue_prev = t_obj.financials.loc["Total Revenue"].iloc[1]
            rev_growth = ((revenue_curr - revenue_prev) / revenue_prev * 100 / 10
                          if revenue_prev else None)

            # ---- 6. FCF Yield (/10) ----
            cf = t_obj.cashflow

            # Try multiple labels for Operating Cash Flow
            ocf_labels = ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]
            operating_cf = None
            for label in ocf_labels:
                if label in cf.index:
                    operating_cf = cf.loc[label].iloc[0]
                    break

            # Capital Expenditures
            capex_labels = ["Capital Expenditure"]
            capex = None
            for label in capex_labels:
                if label in cf.index:
                    capex = cf.loc[label].iloc[0]
                    break

            # Free Cash Flow (CapEx is usually negative)
            fcf = operating_cf + capex if (operating_cf is not None and capex is not None) else None

            # Market Cap
            shares = t_obj.info.get("sharesOutstanding")
            price = t_obj.info.get("currentPrice")
            market_cap = price * shares if (price and shares) else None

            # FCF Yield (/10)
            fcf_yield = (fcf / market_cap * 100) if (fcf and market_cap) else None

            all_data.append({
                "Ticker": t_symbol,
                "Price": price,
                "Earnings Yield": earnings_yield,
                "PEG": peg,
                "Debt/Equity": de_ratio,
                "Revenue Growth (/10)": rev_growth,
                "FCF Yield": fcf_yield
            })

            # polite delay to avoid overloading
            time.sleep(0.1)

        except Exception as e:
            print(f"Error fetching {t_symbol}: {e}")
            continue

# Convert to DataFrame
df = pd.DataFrame(all_data)
df.to_csv("stocks_database.csv", index=False)
