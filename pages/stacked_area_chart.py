import pandas as pd
from dash import dcc, html, Input, Output, register_page
import plotly.express as px
import dash

# Register the page with Dash Pages
register_page(__name__, path="/stacked", name="Stacked Area Chart")

# Load the Reviews Dataset
reviews_df = pd.read_excel("Cleaned_Reviews_with_Sentiment.xlsx")

# Clean Release Version and parse dates
reviews_df['Release Version'] = reviews_df['Release Version'].astype(str).str.strip()
reviews_df['reviewCreatedAt'] = pd.to_datetime(reviews_df['reviewCreatedAt'], errors='coerce')

# Remove rows where dates are invalid
reviews_df.dropna(subset=['reviewCreatedAt'], inplace=True)

# Helper function to aggregate reviews
def aggregate_reviews(df, time_freq='M', stack_dim='Release Version'):
    temp = df.copy()
    temp['Period'] = temp['reviewCreatedAt'].dt.to_period(time_freq).dt.start_time
    grouped = temp.groupby(['Period', stack_dim], as_index=False)['reviewId'].count()
    grouped.rename(columns={'reviewId': 'review_count'}, inplace=True)
    return grouped

layout = html.Div([
    html.Div([
        html.H2("Stacked Area Chart: Review Volume Over Time", className="section-title"),
        html.A("← Back to Home", href="/", className="back-button")
    ], className="page-header"),

    html.Div([
        html.Label("Select Time Granularity:"),
        dcc.Dropdown(
            id='stacked-freq-dropdown',
            options=[
                {'label': 'Monthly', 'value': 'M'},
                {'label': 'Weekly', 'value': 'W'},
            ],
            value='M',
            clearable=False
        ),
    ], style={'width': '300px', 'marginBottom': '20px'}),

    html.Div([
        html.Label("Stack By:"),
        dcc.Dropdown(
            id='stacked-stack-dropdown',
            options=[
                {'label': 'Release Version', 'value': 'Release Version'},
                {'label': 'Sentiment', 'value': 'sentiment'},
            ],
            value='Release Version',
            clearable=False
        ),
    ], style={'width': '300px', 'marginBottom': '20px'}),

    dcc.Graph(id='stacked-area-chart-graph')
])

@dash.callback(
    Output('stacked-area-chart-graph', 'figure'),
    Input('stacked-freq-dropdown', 'value'),
    Input('stacked-stack-dropdown', 'value')
)
def update_area_chart(selected_freq, stack_dim):
    grouped = aggregate_reviews(reviews_df, time_freq=selected_freq, stack_dim=stack_dim)
    grouped.sort_values('Period', inplace=True)

    fig = px.area(
        grouped,
        x='Period',
        y='review_count',
        color=stack_dim,
        title=f"Review Volume Over Time (By {stack_dim}, freq={selected_freq})"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="# of Reviews"
    )

    return fig
