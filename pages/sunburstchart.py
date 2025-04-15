import pandas as pd
from dash import dcc, html, Input, Output, register_page
import plotly.express as px
import dash

# Register this as a page in the app
register_page(__name__, path="/sunburst", name="Sunburst Chart")

# STEP 1: Load the datasets
features_df = pd.read_excel("aggregated_features.xlsx")
reviews_df = pd.read_excel("Cleaned_Reviews_with_Sentiment.xlsx")

# STEP 2: Clean & merge
features_df['Release Version'] = features_df['Release Version'].astype(str).str.strip()
reviews_df['Release Version'] = reviews_df['Release Version'].astype(str).str.strip()
reviews_df['reviewCreatedAt'] = pd.to_datetime(reviews_df['reviewCreatedAt'], errors='coerce')
features_df['Feature Description'] = features_df['Feature Description'].fillna("")
reviews_df.dropna(subset=['reviewCreatedAt'], inplace=True)

merged_df = pd.merge(
    reviews_df, features_df,
    on="Release Version",
    how="left"
)

merged_df['text_length'] = merged_df['content'].astype(str).fillna("").apply(len)
merged_df['sentiment'] = merged_df['sentiment'].fillna("Unknown")

layout = html.Div([
    html.Div([
        html.H2("Sunburst Chart: Feature → Sentiment Breakdown", className="section-title"),
        html.A("← Back to Home", href="/", className="back-button")
    ], className="page-header"),

    html.Div([
        dcc.Graph(id="sunburst-chart")
    ], className="graph-container")
])



# Callback for this page
@dash.callback(
    Output("sunburst-chart", "figure"),
    Input("sunburst-chart", "id")
)
def update_sunburst(_):
    if merged_df.empty:
        return px.sunburst()

    grouped = merged_df.groupby([
        'Feature Description', 'Release Version', 'sentiment'
    ]).size().reset_index(name='review_count')

    fig = px.sunburst(
        grouped,
        path=['Feature Description', 'Release Version', 'sentiment'],
        values='review_count',
        color='sentiment',
        title="Sentiment Breakdown by Feature and Release Version"
    )

    fig.update_layout(margin=dict(t=50, l=0, r=0, b=0))
    return fig
