import dash
from dash import Dash, html, dcc
from datetime import datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from model import prediction  # Ensure this file exists and is correct


def get_stock_price_fig(df):
    fig = px.line(df, x="Date", y=["Close", "Open"], title="Closing and Opening Price vs Date")
    return fig


def get_more(df):
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df, x="Date", y="EMA_20", title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig


app = Dash(__name__, external_stylesheets=["https://fonts.googleapis.com/css2?family=Roboto&display=swap"])
server = app.server

# HTML Layout
app.layout = html.Div([
    html.Div([
        html.P("WELCOME TO STOCK PREDICTION APPLICATION", className="start"),
        html.Div([
            html.P("🔘Input a stock code: "),
            html.Div([
                dcc.Input(id="dropdown_tickers", type="text"),
                html.Button("Submit", id='submit'),
            ], className="form")
        ], className="input-place"),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dt(1995, 8, 5),
                max_date_allowed=dt.now(),
                initial_visible_month=dt.now(),
                end_date=dt.now().date()
            ),
        ], className="date"),
        html.Div([
            html.Button("📊Stock Price", className="stock-btn", id="stock"),
            html.Button("📈📉Indicators", className="indicators-btn", id="indicators"),
            dcc.Input(id="n_days", type="text", placeholder="Input number of days"),
            html.Button("🕵️‍♀️Forecast", className="forecast-btn", id="forecast")
        ], className="buttons"),
    ], className="nav"),

    html.Div([
        html.Div([
            html.Img(id="logo"),
            html.P(id="ticker")
        ], className="header"),
        html.Div(id="description", className="decription_ticker"),
        html.Div([], id="graphs-content"),
        html.Div([], id="main-content"),
        html.Div([], id="forecast-content")
    ], className="content"),
], className="container")


# Callback for Company Info
@app.callback(
    [Output("description", "children"), Output("logo", "src"), Output("ticker", "children"),
     Output("stock", "n_clicks"), Output("indicators", "n_clicks"), Output("forecast", "n_clicks")],
    [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")]
)
def update_data(n, val):
    if n is None:
        return ("Data Visualization in the stock market helps traders make quick decisions and easily synthesize large amounts of complex information. "
                "*PLEASE enter a valid stock code to get details.*",
                "https://i.im.ge/2022/06/11/rHQ4qz.jpg",
                "STOCKS FORECASTER🕵️ AND VISUALIZER", None, None, None)

    if val is None:
        return dash.no_update

    ticker = yf.Ticker(val)
    inf = ticker.info
    df = pd.DataFrame().from_dict(inf, orient="index").T

    return df.get('longBusinessSummary', ["No description available"])[0], \
           df.get('logo_url', ["https://i.im.ge/2022/06/11/rHQ4qz.jpg"])[0], \
           df.get('shortName', ["Unknown Stock"])[0], None, None, None


# Callback for Stock Graphs
@app.callback(
    [Output("graphs-content", "children")],
    [Input("stock", "n_clicks"), Input('my-date-picker-range', 'start_date'), Input('my-date-picker-range', 'end_date')],
    [State("dropdown_tickers", "value")]
)
def stock_price(n, start_date, end_date, val):
    if n is None:
        return [""]

    if val is None:
        return ["Please enter a valid stock symbol"]

    df = yf.download(val, start=str(start_date) if start_date else None, end=str(end_date) if end_date else None)
    df.reset_index(inplace=True)

    return [dcc.Graph(figure=get_stock_price_fig(df))]


# Callback for Indicators
@app.callback(
    [Output("main-content", "children")],
    [Input("indicators", "n_clicks"), Input('my-date-picker-range', 'start_date'), Input('my-date-picker-range', 'end_date')],
    [State("dropdown_tickers", "value")]
)
def indicators(n, start_date, end_date, val):
    if n is None:
        return [""]

    if val is None:
        return [""]

    df_more = yf.download(val, start=str(start_date) if start_date else None, end=str(end_date) if end_date else None)
    df_more.reset_index(inplace=True)

    return [dcc.Graph(figure=get_more(df_more))]


# Callback for Forecast
@app.callback(
    [Output("forecast-content", "children")],
    [Input("forecast", "n_clicks")],
    [State("n_days", "value"), State("dropdown_tickers", "value")]
)
def forecast(n, n_days, val):
    if n is None:
        return [""]

    if val is None or n_days is None:
        return ["Please enter a valid stock symbol and number of days"]

    try:
        fig = prediction(val, int(n_days) + 1)
        return [dcc.Graph(figure=fig)]
    except Exception as e:
        return [f"Error generating forecast: {str(e)}"]


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
