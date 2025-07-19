#imports
import dash
from dash import dcc, html

#load layout and callbacks
from layout import layout
from callbacks.cost_callbacks import register_callbacks as register_cost_callbacks
from callbacks.stats_callbacks import register_callbacks as register_stats_callbacks
from callbacks.store_callbacks import register_callbacks as register_store_callbacks
from callbacks.tooltip_callbacks import register_callbacks as register_tooltip_callbacks
from callbacks.update_callbacks import register_callbacks as register_update_callbacks

#create the dash application
app = dash.Dash(__name__, suppress_callback_exceptions=True)

#assign the layout from layout.py
app.layout = layout

#register the modular callbacks so they can be used in the app
register_cost_callbacks(app)
register_stats_callbacks(app)
register_store_callbacks(app)
register_tooltip_callbacks(app)
register_update_callbacks(app)

#run app
if __name__ == '__main__':
    app.enable_dev_tools(dev_tools_ui=False)
    app.run_server(debug=False)