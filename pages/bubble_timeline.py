import pandas as pd
from dash import dcc, html, Input, Output, register_page
import plotly.express as px
import dash

# Register as a Dash page
register_page(__name__, path="/bubble", name="Bubble Timeline")

# STEP 1: Load the datasets
features_df = pd.read_excel("aggregated_features.xlsx")
reviews_df = pd.read_excel("Cleaned_Reviews_with_Sentiment.xlsx")

# STEP 2: Clean & merge
features_df['Release Version'] = features_df['Release Version'].astype(str).str.strip()
reviews_df['Release Version'] = reviews_df['Release Version'].astype(str).str.strip()

# Convert dates
reviews_df['reviewCreatedAt'] = pd.to_datetime(reviews_df['reviewCreatedAt'], errors='coerce')
features_df['Feature Description'] = features_df['Feature Description'].fillna("")

# Drop reviews with invalid dates
reviews_df.dropna(subset=['reviewCreatedAt'], inplace=True)

# Merge so we can show mapped features
merged_df = pd.merge(
    reviews_df, features_df,
    on="Release Version",
    how="left"
)

# Compute text length for bubble size if needed
merged_df['text_length'] = merged_df['content'].astype(str).fillna("").apply(len)

# Fill NaN sentiment with 'Unknown' to avoid issues
merged_df['sentiment'] = merged_df['sentiment'].fillna("Unknown")

# Dropdown options for bubble size
size_options = [
    {'label': 'Thumbs Up Count', 'value': 'thumbsUpCount'},
    {'label': 'Text Length', 'value': 'text_length'}
]

layout = html.Div([
    html.Div([
        html.H2("Bubble Timeline: Reviews Over Time", className="section-title"),
        html.A("← Back to Home", href="/", className="back-button")
    ], className="page-header"),

    html.Label("Select Bubble Size Metric:"),
    dcc.Dropdown(
        id="size-metric-dropdown",
        options=size_options,
        value="thumbsUpCount",
        clearable=False,
        style={"width": "300px", "margin-bottom": "20px"}
    ),

    dcc.Graph(id="bubble-timeline-graph")
])

@dash.callback(
    Output("bubble-timeline-graph", "figure"),
    Input("size-metric-dropdown", "value")
)
def update_bubble_chart(selected_metric):
    if merged_df.empty:
        return px.scatter()

    fig = px.scatter(
        merged_df,
        x="reviewCreatedAt",
        y="Release Version",
        size=selected_metric,
        color="sentiment",
        title=f"Bubble Timeline (Bubble size = {selected_metric})",
        hover_data={
            "content": True,
            "Feature Description": True,
            selected_metric: True,
            "Release Version": True
        }
    )

    fig.update_layout(
        xaxis_title="Review Date",
        yaxis_title="Release Version",
        height=600
    )

    return fig
