import os
import dash
from dash import html, page_container

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server  # ← this line is critical for gunicorn to find the app

app.layout = html.Div([
    html.H1("📊 Webex Feature Review Visualizations", style={"textAlign": "center"}),
    html.Hr(),
    page_container
])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)
