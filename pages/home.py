from dash import html, register_page

register_page(__name__, path="/", name="Home")

# Define your pages and paths
pages = [
    ("Traceability Timeline", "/trace"),
    ("Bubble Timeline", "/bubble"),
    ("Wordcloud Map", "/wordcloud"),
    ("Slope Graph", "/slope"),
    ("Stacked Area Chart", "/stacked"),
    ("Sunburst Chart", "/sunburst"),
    ("Sentiment Heatmap", "/heatmap"),
    ("Feature Review Summary", "/feature-review")
]

layout = html.Div([
    html.H1("📊 Webex Visualization Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.A(title, href=link, className="card-link")
        ], className="card")
        for title, link in pages
    ], className="card-container")
])
