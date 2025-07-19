#imports
from dash import callback, Input, Output
import pandas as pd
import plotly.express as px
from dash import callback, Input, Output, State, ctx, no_update

def register_callbacks(app):

    #barchart helper function to build all charts
    def build_bar_figure(df, x_col, y_col, label_col, title, y_title, hover_suffix=""):
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            text=label_col,
            color=y_col,
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig.update_traces(
            texttemplate="%{text}",
            textposition="outside",
            marker_line_color='black',
            marker_line_width=1,
            hovertemplate=f"<b>%{{x}}</b><br>{y_title}: %{{y:.3f}}{hover_suffix}<extra></extra>"
        )
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_title,
            font=dict(family="Computer Modern", size=14),
            height=500,
            width=600,
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            margin=dict(t=80, b=80, l=60, r=40),
            xaxis_tickangle=-30,
            yaxis=dict(gridcolor="black")
        )
        return fig

    #shapley graph callback
    @callback(
        Output("shapley-graph", "figure"),
        [Input("graph-data", "data"), Input("reset-btn", "n_clicks")]
    )
    def update_shapley(graph_data, reset_clicks):
        #reset graph on reset button hit
        if ctx.triggered_id == "reset-btn":
            return px.bar(title="no data")

        #get graph data
        data = graph_data.get("metric_data") if graph_data else None
        #if theres no data, return empty chart
        if not data:
            return px.bar(title="no data")

        #get pandas dataframe with Shapley values
        df = pd.DataFrame([
            {"Control": k, "Shapley Value": v.get("shapley_value", 0), "Rounded Label": round(v.get("shapley_value", 0), 3)}
            for k, v in data.items()
        ]).sort_values("Shapley Value", ascending=False)

        #build bar chart from control Shapley values
        return build_bar_figure(df, "Control", "Shapley Value", "Rounded Label","Marginal Contribution of Controls (Shapley Value)","Shapley Value (Unitless)")

    #rosi graph callback
    @callback(
        Output("rosi-graph", "figure"),
        [Input("graph-data", "data"), Input("reset-btn", "n_clicks")]
    )
    def update_rosi(graph_data, reset_clicks):
        #reset graph on reset button hit
        if ctx.triggered_id == "reset-btn":
            return px.bar(title="no data")

        #get graph data
        data = graph_data.get("metric_data") if graph_data else None
        #if theres no data, return empty chart
        if not data:
            return px.bar(title="no data")

        #get pandas dataframe with ROSI scores and sort values
        df = pd.DataFrame([
            {"Control": k, "ROSI": float(v.get("rosi_score", 0))}
            for k, v in data.items() if v.get("rosi_score") is not None
        ]).sort_values("ROSI", ascending=False)

        #build figure with ROSI scores
        fig = build_bar_figure(df, "Control", "ROSI", "ROSI","Return on Security Investment (ROSI) by Control", "ROSI (%)", hover_suffix="%")


        
        #return barchart with control ROSI data
        return fig

    #viability graph callback
    @callback(
        Output("viability-graph", "figure"),
        [Input("graph-data", "data"), Input("reset-btn", "n_clicks")]
    )
    def update_viability(graph_data, reset_clicks):
        #reset graph on reset hit
        if ctx.triggered_id == "reset-btn":
            return px.bar(title="no data")

        #retrieve graph data
        data = graph_data.get("metric_data") if graph_data else None
        #if theres no data, return empty chart
        if not data:
            return px.bar(title="no data")

        #get pandas dataframe with viability scores
        df = pd.DataFrame([
            {"Control": k, "Viability Score": v.get("viability", 0), "Rounded Label": round(v.get("viability", 0), 3)}
            for k, v in data.items() if "viability" in v
        ]).sort_values("Viability Score", ascending=False)

        #return barchart with control viability data
        return build_bar_figure(df, "Control", "Viability Score", "Rounded Label","Viability Scores for Optimal Security Controls","Viability Score (Normalised)")