from flask import Flask, render_template, session, redirect, request, url_for
from flask_session import Session
from utils.plot_data import get_eth_price_graph
from utils.plot_data import get_eth_price_graph, create_trend_chart, create_sentiment_forecast
import plotly.io as pio
import os
from utils.sentiment import get_sentiment_data
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()
app.secret_key = "your-secret-key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

API_KEY = os.environ.get("TWITTER_API_KEY", "TWITTER_API_KEY")

def initialize_session():
    session.setdefault('sentiment_history', [])
    session.setdefault('recent_tweets', [])
    session.setdefault('paused', False)
    session.setdefault('viz_mode', 'tron')
    session.setdefault('theme_mode', 'night')
    session.setdefault('top_hashtags', ['#ETH', '#Ethereum', '#Crypto', '#Web3', '#DeFi'])

@app.route('/', methods=['GET', 'POST'])
def home():
    initialize_session()

    if request.method == 'POST':
        if 'toggle_pause' in request.form:
            session['paused'] = not session['paused']
        if 'theme_mode' in request.form:
            session['theme_mode'] = request.form['theme_mode']
        if 'viz_mode' in request.form:
            session['viz_mode'] = request.form['viz_mode']
        return redirect(url_for('home'))
    eth_chart = get_eth_price_graph()
    eth_chart_html = pio.to_html(eth_chart, full_html=False) if eth_chart else "<p>Failed to load chart</p>"
    current_score = get_sentiment_data(API_KEY, session)
    trend_chart = create_trend_chart(session['sentiment_history'])
    forecast_chart = create_sentiment_forecast(session['sentiment_history'])
    trend_chart_html = pio.to_html(trend_chart, full_html=False) if trend_chart else "<p>No Trend Data</p>"
    forecast_chart_html = pio.to_html(forecast_chart, full_html=False) if forecast_chart else "<p>Need more data</p>"
    return render_template("index.html",
                           paused=session['paused'],
                           viz_mode=session['viz_mode'],
                           theme_mode=session['theme_mode'],
                           top_hashtags=session['top_hashtags'],
                           recent_tweets=session['recent_tweets'],
                           eth_chart_html=eth_chart_html,
                           trend_chart_html=trend_chart_html,
                           forecast_chart_html=forecast_chart_html)


if __name__ == '__main__':
    app.run(debug=True)
