from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import plotly.offline as pyo

app = Flask(__name__)

def get_stock_data(ticker):
    df = yf.download(ticker, period="1y")

    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()

    return df

def create_chart(df, ticker):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="MA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], name="MA200"))

    fig.update_layout(
        title=f"{ticker} Analysis",
        xaxis_title="Date",
        yaxis_title="Price"
    )

    return pyo.plot(fig, output_type="div")

def get_prices(tickers):
    df = pd.DataFrame()

    for t in tickers:
        data = yf.download(t, period="1y")
        df[t] = data["Close"]

    return df

def get_correlation(df):
    return df.pct_change().corr()

def create_heatmap(corr):
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1
    )

    return fig.to_html()

def create_comparison_chart(data):
    fig = go.Figure()

    for ticker, df in data.items():
        fig.add_trace(go.Scatter(
            y=df,
            name=ticker
        ))

    return fig.to_html()

def create_chart(df, ticker):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        name="Close Price"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["MA50"],
        name="MA50"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["MA200"],
        name="MA200"
    ))

    fig.update_layout(
        title=f"{ticker} Stock Analysis",
        xaxis_title="Date",
        yaxis_title="Price"
    )

    return pyo.plot(fig, output_type="div")

@app.route("/", methods=["GET", "POST"])
def index():
    chart = None
    table = None
    heatmap = None
    ticker = None

    if request.method == "POST":

        tickers = request.form["ticker"].upper().split(",")

        tickers = [t.strip() for t in tickers]

        # si solo hay uno → gráfico individual
        if len(tickers) == 1:
            df = get_stock_data(tickers[0])
            chart = create_chart(df, tickers[0])
            table = df.tail(10).to_html()

        # si hay varios → comparación + correlación
        else:
            prices = get_prices(tickers)
            corr = get_correlation(prices)
            heatmap = create_heatmap(corr)

    return render_template(
        "index.html",
        chart=chart,
        table=table,
        heatmap=heatmap,
        ticker=ticker
    )

if __name__ == "__main__":
    app.run(debug=True)