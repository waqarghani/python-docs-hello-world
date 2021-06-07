'''
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import logging
import flask
import os

from src.simulation.plots import Plots
from src.simulation.components.left_nav_component import Left_nav
from src.simulation.components.middle_slider_component import Middle_slider
from src.simulation.components.right_tabs import Right_tabs
from src.simulation.components.callbacks import Callbacks
from src.simulation.helper import CURRENT_YEAR

# speed boat imports
from src.utils.config import config
'''
'''
server = flask.Flask(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA], server=server)
app.title = 'Simulation Tool'

# get optional environment variables
if "SQL_FLAG" in os.environ:
    sql_flag = os.environ["SQL_FLAG"]
else:
    sql_flag = "True"

if "APP_PORT" in os.environ:
    app_port = os.environ["APP_PORT"]
else:
    app_port = 80


class Simulation:
    """
    Holds all methods to create the parts of the app.

    - create_app() is used to create all parts in the correct sequence
    - set_layout() controls the overall layout of the app

    """

    def __init__(self, app_config: dict, app):
        self._log = logging.getLogger(__name__)
        self._config = app_config

        self.plots = Plots()
        self.app = app

    def combine_left_and_middle_components(self, left_nav_component, middle_slider):
        return dbc.Container(
            [
                dbc.Row([left_nav_component, middle_slider]),
                dbc.Row(
                    html.Div(
                        "Data source: SQL live connection, latest available KPIs from the market cube "
                        + CURRENT_YEAR
                        + "."
                    ),
                    style={"marginBottom": 0, "marginTop": 0, "marginLeft": 0,},
                ),
            ]
        )

    def set_layout(self, left_columns, tab_1, tab_2, tab_3):
        """
        Set the overall layout of the app
        :param left_columns: left navigation component including KPIs and sliders
        :param tab_1: waterfall simulation tab
        :param tab_2: break even simulation tab
        :param tab_3: KPI view simulation tab
        :return: initialized app layout
        """
        self.app.layout = dbc.Container(
            [
                dbc.Row(
                    # Logo and title
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    html.Img(
                                        src=self.app.get_asset_url("daimler_logo.png"),
                                        style={
                                            "height": 45,
                                            "width": 45,
                                            "font-family": "Times New Roman",
                                        },
                                    ),
                                    style={
                                        "marginBottom": 5,
                                        "marginTop": 5,
                                        "marginLeft": 0,
                                    },
                                ),
                            ],
                            style={"height": "10%", "marginLeft": 12},
                            width="auto",
                        ),
                        dbc.Col(
                            html.Div(
                                html.H1("Parts pricing simulator"),
                                style={
                                    "textAlign": "left",
                                    "marginTop": 8,
                                    "marginLeft": 10,
                                    "color": config.app.colors.heading,
                                },
                            )
                        ),
                    ],
                    className="h-5",
                    no_gutters=True,
                ),

                # Tab switcher: Simulation | Break-Even | Scenario comparison
                dbc.Row(
                    [
                        dbc.Col(left_columns, width={"size": 4}),
                        dbc.Col(
                            dcc.Tabs(
                                id="tabs-example",
                                value="tab-1",
                                children=[
                                    dcc.Tab(
                                        label="Simulation",
                                        value="tab-1",
                                        children=[tab_1],
                                        style=config.app.tab_style,
                                        selected_style=config.app.tab_selected_style,
                                    ),
                                    html.Div(
                                    dcc.Tab(
                                        label="Break-even",
                                        value="tab-2",
                                        children=[tab_2],
                                        style=config.app.tab_style,
                                        selected_style=config.app.tab_selected_style,
                                    ),
                                    hidden = True,
                                 ),
                                    html.Div(
                                        dcc.Tab(
                                            label="Scenario comparison",
                                            value="tab-3",
                                            children=[tab_3],
                                            style=config.app.tab_style,
                                            selected_style=config.app.tab_selected_style,
                                        ),
                                        hidden=True,
                                    ),
                                ],
                            ),
                            width={"size": 8},
                        ),
                    ],
                    justify="around",
                    className="h-100",
                ),
                html.Div(id="simulation_data_storage", style={"display": "none"}),
                html.Div(id="input_data_storage", style={"display": "none"}),
            ],
            fluid=True,
        )

    def create_app(self):
        """
        Run the methods of this class in the correct sequence to create the app
        """
        # assemble the left most column of the app (dropdown and kpis)
        left_nav_component = Left_nav().create()
        middle_slider_component = Middle_slider().create()

        left_columns = self.combine_left_and_middle_components(
            left_nav_component, middle_slider_component
        )

        tab_1 = Right_tabs().create_tab1()
        tab_2 = Right_tabs().create_tab2()
        tab_3 = Right_tabs().create_tab3()

        # assemble the left columns with the tabs
        self.set_layout(left_columns, tab_1, tab_2, tab_3)

        # define inputs, outputs and callbacks
        callbacks = Callbacks(app)

        callbacks.set_inputs()
        callbacks.set_outputs()
        callbacks.set_states()
        callbacks.create_callbacks()


simulation = Simulation(config, app)
simulation.create_app() '''

#if __name__ == "__main__":
    
    # simulation.app.run_server(port=app_port, debug=True, use_reloader=False)
    # simulation.app.run_server(port=app_port, debug=False, use_reloader=False)

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, Azure!"
