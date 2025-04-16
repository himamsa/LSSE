import dash
from dash import dcc, html, Input, Output, register_page
import pandas as pd
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

register_page(__name__, path="/wordcloud", name="Word Cloud")

# Load the reviews Excel file
df = pd.read_excel("Cleaned_Reviews_with_Sentiment.xlsx")
df['reviewCreatedAt'] = pd.to_datetime(df['reviewCreatedAt'])

layout = html.Div([
    html.Div([
        html.H2("💬 Word Cloud of Reviews per Feature", className="section-title"),
        html.A("← Back to Home", href="/", className="back-button")
    ], className="page-header"),

    html.Label("Select Release Version:"),
    dcc.Dropdown(
        options=[{"label": v, "value": v} for v in sorted(df["Release Version"].dropna().unique())],
        id="wordcloud-version-dropdown",
        placeholder="Choose a release version"
    ),

    html.Label("Select Sentiment:"),
    dcc.Dropdown(
        options=[{"label": s.capitalize(), "value": s} for s in df["sentiment"].dropna().unique()],
        id="wordcloud-sentiment-dropdown",
        placeholder="All sentiments"
    ),

    html.Label("Select Date Range:"),
    dcc.DatePickerRange(
        id="wordcloud-date-range",
        start_date=df['reviewCreatedAt'].min(),
        end_date=df['reviewCreatedAt'].max(),
        display_format='YYYY-MM-DD'
    ),

    html.Br(), html.Label("Dark Mode:"),
    dcc.Checklist(
        id="wordcloud-dark-mode",
        options=[{"label": " Enable", "value": "dark"}],
        value=[]
    ),

    html.Div(id="wordcloud-output-div", style={"marginTop": "20px"})
], style={"padding": "20px"})

@dash.callback(
    Output("wordcloud-output-div", "children"),
    Input("wordcloud-version-dropdown", "value"),
    Input("wordcloud-sentiment-dropdown", "value"),
    Input("wordcloud-date-range", "start_date"),
    Input("wordcloud-date-range", "end_date"),
    Input("wordcloud-dark-mode", "value")
)
def update_wordcloud(version, sentiment, start_date, end_date, dark_mode):
    filtered = df.copy()

    if version:
        filtered = filtered[filtered["Release Version"] == version]
    if sentiment:
        filtered = filtered[filtered["sentiment"] == sentiment]
    if start_date and end_date:
        filtered = filtered[
            (filtered["reviewCreatedAt"] >= pd.to_datetime(start_date)) &
            (filtered["reviewCreatedAt"] <= pd.to_datetime(end_date))
        ]

    if filtered.empty:
        return html.P("No reviews found for the selected filters.")

    text = " ".join(filtered["content"].dropna().astype(str))
    background = "black" if "dark" in dark_mode else "white"

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color=background,
        colormap="Pastel1" if background == "white" else "Pastel2"
    ).generate(text)

    buffer = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(buffer, format="png", facecolor=background)
    plt.close()
    buffer.seek(0)

    encoded_image = base64.b64encode(buffer.read()).decode()
    return html.Img(src=f"data:image/png;base64,{encoded_image}", style={"width": "100%", "maxWidth": "800px"})
