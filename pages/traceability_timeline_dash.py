import pandas as pd
from dash import dcc, html, Input, Output, register_page
import plotly.graph_objects as go
import dash

register_page(__name__, path="/trace", name="Traceability Timeline")

# Load datasets
features_df = pd.read_excel("aggregated_features.xlsx")
reviews_df = pd.read_excel("Cleaned_Reviews_with_Sentiment.xlsx")

# Clean release version strings (trim spaces only)
features_df['Release Version'] = features_df['Release Version'].astype(str).str.strip()
reviews_df['Release Version'] = reviews_df['Release Version'].astype(str).str.strip()

# Ensure datetime format
features_df['Release Date'] = pd.to_datetime(features_df['Release Date'], errors='coerce')
reviews_df['reviewCreatedAt'] = pd.to_datetime(reviews_df['reviewCreatedAt'], errors='coerce')

# Unique versions for dropdown (from features_df only)
versions = sorted(features_df['Release Version'].dropna().unique(), key=lambda x: [int(p) for p in x.split('.') if p.isdigit()])

layout = html.Div([
    html.Div([
        html.H2("Feature → Review Timeline with Connectors", className="section-title"),
        html.A("← Back to Home", href="/", className="back-button")
    ], className="page-header"),
    html.Div([
        html.H2("Feature → Review Timeline with Connectors", className="section-title"),
        html.A("← Back to Home", href="/", className="back-button")
    ], className="page-header"),

    dcc.Dropdown(
        id='version-selector',
        options=[{'label': ver, 'value': ver} for ver in versions],
        placeholder="Select a Release Version"
    ),

    dcc.Graph(id='timeline-graph-trace')
])

@dash.callback(
    Output('timeline-graph-trace', 'figure'),
    Input('version-selector', 'value')
)
def update_timeline(version):
    if not version:
        return go.Figure()

    feature_row = features_df[features_df['Release Version'] == version]
    if feature_row.empty or pd.isna(feature_row.iloc[0]['Release Date']):
        return go.Figure().update_layout(title=f"No feature data for version {version}")

    feature_date = pd.to_datetime(feature_row.iloc[0]['Release Date'], errors='coerce')

    filtered_reviews = reviews_df[
        (reviews_df['Release Version'] == version) & (~reviews_df['reviewCreatedAt'].isna())
    ].copy()

    filtered_reviews['reviewCreatedAt'] = pd.to_datetime(
        filtered_reviews['reviewCreatedAt'], errors='coerce')
    filtered_reviews.dropna(subset=['reviewCreatedAt'], inplace=True)

    if filtered_reviews.empty:
        return go.Figure().update_layout(
            title=f"No reviews found for version {version}",
            xaxis_title="Date",
            yaxis=dict(showticklabels=False, range=[-0.5, 1.5]),
            height=500
        )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[feature_date],
        y=[1],
        mode='markers+text',
        marker=dict(size=12, color='blue'),
        name='Feature Released',
        text=[f"Feature: {version}"],
        textposition="top center"
    ))

    sentiment_map = {'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
    marker_colors = [sentiment_map.get(sent, 'black') for sent in filtered_reviews['sentiment'].fillna('')]

    fig.add_trace(go.Scatter(
        x=filtered_reviews['reviewCreatedAt'],
        y=[0] * len(filtered_reviews),
        mode='markers',
        marker=dict(size=8, color=marker_colors),
        text=filtered_reviews['content'],
        hoverinfo='text',
        name='Reviews'
    ))

    line_x, line_y = [], []
    for _, row in filtered_reviews.iterrows():
        line_x += [feature_date, row['reviewCreatedAt'], None]
        line_y += [1, 0, None]

    fig.add_trace(go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines',
        line=dict(color='lightgray', width=1),
        name='Connectors',
        showlegend=False
    ))

    min_date = min(feature_date, filtered_reviews['reviewCreatedAt'].min())
    max_date = max(feature_date, filtered_reviews['reviewCreatedAt'].max())
    padding_days = pd.Timedelta(days=5)
    x_start = min_date - padding_days
    x_end = max_date + padding_days

    fig.update_layout(
        title=f"Traceability Timeline for Release Version {version}",
        xaxis=dict(range=[x_start, x_end], title="Date"),
        yaxis=dict(showticklabels=False, range=[-0.5, 1.5]),
        height=500
    )

    return fig
