import requests
import pandas as pd
import plotly.graph_objs as go
from sklearn.linear_model import LinearRegression
import numpy as np
import time

def get_eth_price_graph(days=0.0417):  # ~1 hour
    try:
        url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
        params = {"vs_currency": "usd", "days": days}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()['prices']  # [[timestamp, price], ...]

        df = pd.DataFrame(data, columns=['time', 'price'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')

        fig = go.Figure(go.Scatter(
            x=df['time'], y=df['price'], mode='lines',
            line=dict(color='#6F42C1')
        ))

        fig.update_layout(
            title="Real-Time ETH Price Trend (Last Hour)",
            plot_bgcolor="#0a0a0f",
            paper_bgcolor="#0a0a0f",
            font_color="#ffffff",
            height=250,
            xaxis=dict(showgrid=False, title="Time"),
            yaxis=dict(showgrid=False),
            title_font=dict(color='#6F42C1', size=18)
        )

        return fig

    except Exception as e:
        print(f"Chart Error: {e}")
        return None
def create_trend_chart(sentiment_history):
    if not sentiment_history:
        return None
    df = pd.DataFrame(sentiment_history)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['score'],
        mode='lines+markers',
        line=dict(color='#6F42C1', width=2),
        fill='tozeroy',
        fillcolor='rgba(111,66,193,0.3)',
        marker=dict(size=5, color='#ff80ff', line=dict(width=1, color='#6F42C1')),
        hovertemplate='Time: %{x|%H:%M:%S}<br>Score: %{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="Ethereum Buzz Density Over Time",
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f",
        font_color="#ffffff",
        height=250,
        xaxis=dict(showgrid=False, tickformat='%H:%M:%S', title="Time"),
        yaxis=dict(showgrid=False, range=[-1, 1]),
        title_font=dict(color='#6F42C1', size=18),
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )

    return fig

def create_sentiment_forecast(sentiment_history):
    if len(sentiment_history) < 5:
        return None

    df = pd.DataFrame(sentiment_history)
    df['time_num'] = (df['time'] - df['time'].min()) / 60  # Minutes since start
    X = df['time_num'].values.reshape(-1, 1)
    y = df['score'].values

    model = LinearRegression().fit(X, y)
    future_times = np.array([df['time_num'].max() + i for i in range(1, 6)]).reshape(-1, 1)
    predictions = model.predict(future_times)

    fig = go.Figure(go.Scatter(
        x=list(range(1, 6)), y=predictions,
        mode='lines+markers',
        line=dict(color='#ff80ff')
    ))

    fig.update_layout(
        title="Sentiment Forecast (Next 5 Minutes)",
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f",
        font_color="#ffffff",
        height=250,
        xaxis=dict(showgrid=False, title="Minutes Ahead"),
        yaxis=dict(showgrid=False, range=[-1, 1]),
        title_font=dict(color='#6F42C1', size=18)
    )

    return fig