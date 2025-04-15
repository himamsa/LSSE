import pandas as pd
from dash import dcc, html, Input, Output, register_page
import plotly.express as px
import dash

# Register this as a Dash page
register_page(__name__, path="/feature-review", name="Feature Review Summary")

# Load datasets
features_df = pd.read_excel("aggregated_features.xlsx")
reviews_df = pd.read_excel("Cleaned_Reviews_with_Sentiment.xlsx")

# Strip only leading and trailing spaces in Release Version
features_df['Release Version'] = features_df['Release Version'].astype(str)
reviews_df['Release Version'] = reviews_df['Release Version'].astype(str).str.strip()

# Merge datasets on Release Version
merged_df = pd.merge(reviews_df, features_df, on='Release Version', how='left')

# Unique versions for dropdown (from features_df only)
versions = sorted(features_df['Release Version'].dropna().unique(), key=lambda x: [int(part) for part in x.split('.') if part.isdigit()])

# Layout definition
layout = html.Div([
    html.Div([
        html.H2("Feature-Review Timeline Viewer", className="section-title"),
        html.A("← Back to Home", href="/", className="back-button")
    ], className="page-header"),

    dcc.Dropdown(
        id='version-selector',
        options=[{'label': ver, 'value': ver} for ver in versions],
        placeholder="Select a Release Version",
        style={'width': '300px', 'marginBottom': '20px'}
    ),

    html.Div(id='features-display', style={'margin': '20px 0'}),
    dcc.Graph(id='timeline-graph'),
    html.H3("Review Score Distribution"),
    dcc.Graph(id='score-histogram')
])

@dash.callback(
    Output('timeline-graph', 'figure'),
    Output('score-histogram', 'figure'),
    Output('features-display', 'children'),
    Input('version-selector', 'value')
)
def update_output(selected_version):
    if not selected_version:
        return {}, {}, ""

    filtered = merged_df[merged_df['Release Version'] == selected_version]

    # Timeline scatter plot
    timeline_fig = px.scatter(
        filtered,
        x='reviewCreatedAt',
        y='score',
        color='sentiment',
        title=f"Review Timeline for Version {selected_version}",
        hover_data=['content']
    )

    # Score histogram
    hist_fig = px.histogram(
        filtered,
        x='score',
        color='sentiment',
        nbins=5,
        title=f"Review Score Distribution for Version {selected_version}"
    )

    # Feature description beautified using cards
    features = filtered['Feature Description'].dropna().unique()
    if features.size:
        feature_list = [
            html.Div([
                html.H4(f"Feature {i+1}"),
                html.P(feat.strip())
            ], className="feature-card")
            for feature_block in features
            for i, feat in enumerate(feature_block.split("###")) if feat.strip()
        ]
    else:
        feature_list = html.P("No feature info available.")

    return timeline_fig, hist_fig, feature_list
