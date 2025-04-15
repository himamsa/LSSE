import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import page_registry, page_container, register_page

import dash
from dash import html, page_container

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
app.title = "Webex Feature Review Dashboard"

app.layout = html.Div([
    html.H1("📊 Webex Feature Review Visualizations", style={"textAlign": "center"}),
    html.Hr(),
    page_container  # renders current page here
])

if __name__ == "__main__":
    app.run(debug=True)


