About:
This project is a Python Dash web application for cybersecurity decision support.
It analyzes network graphs, calculates financial and risk metrics (ROSI and Shapley values), and optimises security control selections under budget constraints by quantifying controls with the outlined metrics.

Requirements:
pip install dash
pip install pandas
pip install plotly
pip install networkx
pip install pulp
pip install dash-cytoscape

Modules:
app.py — main Dash app file (run this) with python app.py within the directory or run manually on file itself
logic/data_store.py — stores network graph data and related information
logic/graph_utils.py — helper functions to generate graph visuals
optimise.py — contains optimisation MILP solver logic
rosi.py — calculates Return on Security Investment (ROSI)
shapley.py — calculates Shapley values for controls
viability.py — assesses viability metrics with combined normalisation of existing optimise, rosi, shapley
paths.py — computes shortest path probabilities for attacks on network

Running:
python app.py or manually run
Open in browser http://127.0.0.1:8050/

If you want to test the case study input, click 'Upload Graph' button below the attack graph display and select inputdata.json, enter a desired direct and indirect budget (e.g. 10, 10) and click 'Run Optimiser'. Scroll down and click on specific edges or nodes to display outputs

Note that if a control is placed with a duplicate name they are considered identical controls and as such must have the same effectiveness and costs.

Prior to running again on an entirely new graph hit 'Reset Graph' and then make another input unless you are manually altering the graph already present.

Notes:
There is a bug where the website can break when changing tabs if so, refresh the page and reset again.