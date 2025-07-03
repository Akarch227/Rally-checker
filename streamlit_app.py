import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📈 Stock Rally Analysis Tool")

symbol = st.text_input("Enter stock symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")
years = st.slider("Years to analyze", 1, 20, 15)
volume_factor = st.slider("Volume spike factor", 1.0, 2.0, 1.2, step=0.1)
rally_pct = st.slider("Minimum rally % in 7 days", 1, 20, 5)

if st.button("Run Analysis"):
    df = yf.download(symbol, period=f"{years}y")
    df["20d_avg_volume"] = df["Volume"].rolling(20).mean()
    results = []
    for i in range(20, len(df) - 7):
        today, prev, future = df.iloc[i], df.iloc[i-1], df.iloc[i+7]
        vol_ok = float(today["Volume"]) > volume_factor * float(today["20d_avg_volume"])
        pct = (float(future["Close"]) - float(today["Close"])) / float(today["Close"]) * 100
        pattern = None

        if prev["Close"] < prev["Open"] and today["Close"] > today["Open"] \
           and today["Close"] > prev["Open"] and today["Open"] < prev["Close"]:
            pattern = "Bullish Engulfing"

        body = abs(today["Close"] - today["Open"])
        lower = min(today["Open"], today["Close"]) - today["Low"]
        upper = today["High"] - max(today["Open"], today["Close"])
        if lower > 2 * body and upper < body:
            pattern = "Hammer"

        if i >= 2:
            c1, c2 = df.iloc[i-2], df.iloc[i-1]
            if (c1["Close"] < c1["Open"] and
                abs(c2["Close"] - c2["Open"]) < 0.3 * (c1["Open"] - c1["Close"]) and
                today["Close"] > (c1["Open"] + c1["Close"]) / 2):
                pattern = "Morning Star"

        resistance = df["High"].iloc[i-20:i].max()
        if today["Close"] > resistance:
            pattern = "Resistance Breakout"

        if pattern and vol_ok:
            results.append({
                "Date": today.name.date(),
                "Pattern": pattern,
                "Close": round(today["Close"], 2),
                "Rally %": round(pct, 2)
            })

    res_df = pd.DataFrame(results)
    st.subheader("Analysis Results")
    st.write(f"Total signals found: {len(res_df)}")
    st.dataframe(res_df)
    if not res_df.empty:
        st.line_chart(res_df["Rally %"])
