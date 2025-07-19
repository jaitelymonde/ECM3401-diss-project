#import dash, cytoscape, and stylesheet
from dash import html, dcc
import dash_cytoscape as cyto
from logic.graph_utils import generate_stylesheet

#style definitions
font_style = {
    "font-family": "Computer Modern, Georgia, Times New Roman, serif",
    "font-size": "12px",
    "color": "#222",
    "line-height": "1.3"
}

#button style
button_style = {
    "font-size": "12px",
    "font-family": "Computer Modern, Georgia, Times New Roman, serif",
    "padding": "5px 10px",
    "border": "1px solid #888",
    "border-radius": "3px",
    "background-color": "#f4f4f4",
    "cursor": "pointer",
    "margin": "2px"
}

#set layout
layout = html.Div(style=font_style, children=[
    #title
    html.H2("Cybersecurity Control Optimisation Tool", style={
        'text-align': 'center',
        'margin-top': '5px',
        'margin-left': '150px',
        'margin-bottom': '10px',
        'font-weight': 'normal'
    }),

    #output message box for optimsiation
    html.Div(id='output-msg', style={
        'color': 'darkred',
        'text-align': 'center',
        'margin-bottom': '10px'
    }),

    #store graph data for saving json file
    dcc.Store(id='graph-data', storage_type="memory", data={}),
    dcc.Store(id='page-load-trigger', data={'loaded': False}),


    html.Div(style={'display': 'flex', 'gap': '0px', 'align-items': 'flex-start'}, children=[

        #list of manual parameter inputs
        html.Div(style={
            'width': '25%',
            'margin-right': '1%',
            'height': '480px',
            'padding': '10px',
            'background-color': '#f9f9f9',
            'border': '1px solid #ccc',
            'overflow-y': 'auto'
        }, children=[

            #nodes
            html.H4("Nodes", style={'margin-top': '0px', 'margin-bottom': '5px'}),
            dcc.Input(id='node-name', type='text', placeholder='Node Name', style={'width': '99%'}),
            dcc.Input(id='single-loss', type='number', min=0, placeholder='Single Loss Expectancy', style={'width': '99%', 'margin-top': '4px'}),
            dcc.Input(id='occurance-rate', type='number', min=0, placeholder='Annual Rate of Occurrence', style={'width': '99%', 'margin-top': '4px'}),
            html.Div([
                html.Button('Add Node', id='add-node-btn', n_clicks=0, style={**button_style, 'width': '100%', 'margin-top': '6px'}),
            ], style={'margin-top': '6px'}),

            #edges
            html.H4("Edges", style={'margin-top': '12px', 'margin-bottom': '5px'}),
            dcc.Input(id='node1', type='text', placeholder='Source Node', style={'width': '99%'}),
            dcc.Input(id='node2', type='text', placeholder='Target Node', style={'width': '99%', 'margin-top': '4px'}),
            html.Button('Add Edge', id='add-edge-btn', n_clicks=0, style={**button_style, 'width': '100%', 'margin-top': '6px'}),
            
            #controls
            html.H4("Controls", style={'margin-top': '12px', 'margin-bottom': '5px'}),
            dcc.Dropdown(id='edge-dropdown', placeholder="Select an Edge", style={'width': '99%'}),
            dcc.Input(id='control-name', type='text', placeholder='Control Name', style={'width': '99%', 'margin-top': '4px'}),
            dcc.Input(id='effectiveness', type='number', min=0, max=1, step=0.01, placeholder='Effectiveness', style={'width': '99%', 'margin-top': '4px'}),
            dcc.Input(id='direct-cost', type='number', min=0, placeholder='Direct Cost', style={'width': '99%', 'margin-top': '4px'}),
            dcc.Input(id='indirect-cost', type='number', min=0, placeholder='Indirect Cost', style={'width': '99%', 'margin-top': '4px'}),
            html.Button('Add Control to Edge', id='add-ctrl-btn', n_clicks=0, style={**button_style, 'width': '100%', 'margin-top': '6px'}),

        ]),

        html.Div(style={'width': '73%'}, children=[
            html.Div(style={'display': 'flex'}, children=[
                #attack graph formatting
                cyto.Cytoscape(
                    id='cytoscape-graph',
                    zoomingEnabled=True,
                    userZoomingEnabled=True,
                    panningEnabled=True,
                    userPanningEnabled=True,
                    layout={'name': 'preset'},
                    style={'width': '90%', 'height': '500px', 'border': '1px solid #ccc'},
                    elements=[],
                    stylesheet=generate_stylesheet(),
                    minZoom=0.1,
                    maxZoom=3
                ),
                html.Div(style={
                    'width': '28%',
                    'margin-left': '1%',
                    'display': 'flex',
                    'flex-direction': 'column',
                    'gap': '10px'
                }, children=[ 
                    html.H4("Click Nodes or Edges:", style={ #tooltip box title 
                        'margin': '0',
                        'padding-bottom': '0px',
                        'border-bottom': '1px solid #ccc',
                        'font-size': '12px',
                        'font-weight': 'normal'
                    }),
                    html.Div(id="tooltip-box", style={ #node/control tooltip box to the right of atatck graph
                        "height": "375px", "border": "1px solid #ccc", "padding": "10px",
                        "overflow-y": "auto", "background-color": "#f9f9f9"
                    }),
                    html.Div(id="cost-box", style={ #cost box for total indirect, direct, and total control costs
                        "height": "48px", "border": "1px solid #ccc", "padding": "10px",
                        "overflow-y": "auto", "background-color": "#f9f9f9"
                    })
                ])
            ]),

            html.Div(style={
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'center',
                'flex-wrap': 'wrap',
                'gap': '10px',
                'margin-top': '5px',
                'margin-bottom': '5px',
                'margin-right': '300px'
            }, children=[
                dcc.Input(
                    id='direct-budget',
                    type='number',
                    min=0,
                    placeholder='Direct Budget',
                    style={'width': '120px'}
                ),
                dcc.Input(
                    id='indirect-budget',
                    type='number',
                    min=0,
                    placeholder='Indirect Budget',
                    style={'width': '120px'}
                ),
                html.Div([
                    html.Label("Baseline Edge Probability", style={'margin-left': '30px','font-weight': 'bold', 'font-size': '11px'}),
                    dcc.Slider(
                        id='baseline-prob-slider',
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        value=1.0,
                        marks={0.01: '0.01', 0.25: '0.25', 0.5: '0.5', 0.75: '0.75', 1.0: '1.0'},
                        tooltip={"placement": "bottom", "always_visible": True},
                        included=True
                    )
                ], style={'width': '200px', 'display': 'flex', 'flexDirection': 'column', 'gap': '2px'}),

                html.Button('Run Optimiser', id='run-btn', n_clicks=0, style=button_style),
            ]),
            html.Div(style={
                'display': 'flex',
                'justify-content': 'center',
                'gap': '10px',
                'margin-top': '5px',
                'margin-bottom': '5px',
                'margin-right': '200px'
            }, children=[
                html.Button('Reset Graph', id='reset-btn', n_clicks=0, style=button_style),
                html.Button('Save Graph', id='save-btn', n_clicks=0, style=button_style),
                dcc.Upload(
                    id='upload-json',
                    children=html.Button('Upload Graph', style=button_style),
                    accept='.json'
                ),
                dcc.Download(id="download-graph-json")
            ]),

            html.Div(id="upload-feedback", style={
                "text-align": "center",
                "margin-top": "5px",
                "font-style": "italic",
                "color": "#444"
            }),

            html.Div(style={
                'display': 'flex',
                'justify-content': 'space-between',
                'margin-top': '20px',
                'gap': '15px'
            }, children=[
                html.Div(id='graph-output', style={ #milp output box
                    'white-space': 'pre-wrap',
                    'word-wrap': 'break-word',
                    'border': '1px solid #ccc',
                    'padding': '10px',
                    'width': '50%',
                    'height': '140px',
                    'overflow-y': 'auto',
                    'background-color': '#f9f9f9'
                }),
                html.Div(id='path-output', style={ #shortest path box
                    'white-space': 'pre-wrap',
                    'word-wrap': 'break-word',
                    'border': '1px solid #ccc',
                    'padding': '10px',
                    'width': '50%',
                    'height': '140px',
                    'overflow-y': 'auto',
                    'background-color': '#f9f9f9'
                }),
            ]),

            html.Div(
                style={
                    'display': 'flex',
                    'justify-content': 'flex-start',
                    'gap': '40px',
                    'marginTop': '30px',
                    'padding': '0 20px',
                    'flex-wrap': 'wrap',
                    'align-items': 'flex-start'
                },
                children=[
                    dcc.Graph( #empty rosi graph
                        id='rosi-graph',
                        config={'displayModeBar': False},
                        style={
                            'width': '65%',
                            'height': '550px',
                            'minWidth': '320px',
                            'border': '1px solid #ccc',
                            'padding': '10px',
                            'boxSizing': 'border-box'
                        }
                    ),
                    dcc.Graph( #empty shap graph
                        id='shapley-graph',
                        config={'displayModeBar': False},
                        style={
                            'width': '65%',
                            'height': '550px',
                            'minWidth': '320px',
                            'border': '1px solid #ccc',
                            'padding': '10px',
                            'boxSizing': 'border-box'
                        }
                    ),
                    dcc.Graph( #empty viab graph
                        id='viability-graph',
                        config={'displayModeBar': False},
                        style={
                            'width': '65%',
                            'height': '550px',
                            'minWidth': '320px',
                            'border': '1px solid #ccc',
                            'padding': '10px',
                            'boxSizing': 'border-box'
                        }
                    ),
                ]
            )
        ])
    ])
])