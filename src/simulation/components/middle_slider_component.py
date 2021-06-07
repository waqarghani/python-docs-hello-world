import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import logging

from src.utils.config import config


class Middle_slider:
    def __init__(self):
        self._log = logging.getLogger(__name__)

    def create_price_slider(self):
        """
        Creates the slider input to set the new NLP for the simulation
        """
        self.price_slider = dbc.Col(
            dbc.Card(
                [
                    html.Div(id="title_price_input", children="Price change(%)"),
                    dbc.Input(id="new_nlp", type="number", value=None,),
                ],
                style={"padding": 10},
            ),
            style={"marginTop": 10,},
        )

    def create_volume_slider(self):
        """
        Creates the input to set the new volume for the simulation
        """
        self.volume_slider = dbc.Col(
            dbc.Card(
                [
                    html.Div(id="title_volume_input", children="Volume change(%)"),
                    dbc.Input(
                        id="volume_change_perc",
                        type="number",
                        disabled=False,
                        value=None,
                    ),
                ],
                style={"padding": 10,},
            ),
            style={"marginTop": 10, "marginBottom": 10,},
        )

    def create_simulated_cm_component(self):
        """
        Creates fields to display the simulated CM below the sliders
        """

        table_header = [
            html.Thead(html.Tr([html.Th(""), html.Th("Current"), html.Th("Simulated")]))
        ]

        rows = []

        rows.append(
            html.Tr(
                [
                    html.Td("CV Gross"),
                    html.Td(id="sim_cv_gross_actual_id", children=None),
                    html.Td(id="sim_cv_gross_new_id", children=None),
                ]
            )
        )

        rows.append(
            html.Tr(
                [
                    html.Td("CV Net"),
                    html.Td(id="sim_cv_net_actual_id", children=None),
                    html.Td(id="sim_cv_net_new_id", children=None),
                ]
            )
        )

        rows.append(
            html.Tr(
                [
                    html.Td("LLP wo/ CV"),
                    html.Td(id="sim_llp_id", children=None),
                    html.Td(id="sim_new_llp_id", children=None),
                ]
            )
        )

        rows.append(
            html.Tr(
                [
                    html.Td("LLP"),
                    html.Td(id="sim_llp_cv_id", children=None),
                    html.Td(id="sim_new_llp_cv_id", children=None),
                ]
            )
        )

        rows.append(
            html.Tr(
                [
                    html.Td("NLP wo/ CV"),
                    html.Td(id="sim_nlp_id", children=None),
                    html.Td(id="sim_new_nlp_id", children=None),
                ]
            )
        )

        rows.append(
            html.Tr(
                [
                    html.Td("NLP"),
                    html.Td(id="sim_nlp_cv_id", children=None),
                    html.Td(id="sim_new_nlp_cv_id", children=None),
                ]
            )
        )

        rows.append(
            html.Tr(
                [
                    html.Td("Discount rate"),
                    html.Td(id="sim_discount_id", children=None),
                    html.Td(id="sim_new_discount_id", children=None),
                ]
            )
        )

        rows.append(
            html.Tr(
                [
                    html.Td("Per unit CM (PEP)"),
                    html.Td(id="sim_abs_pep_cm_id", children=None),
                    html.Td(id="sim_new_abs_pep_cm_id", children=None),
                ]
            )
        )

        rows.append(
            html.Tr(
                [
                    html.Td("Relative CM (PEP)"),
                    html.Td(id="sim_rel_pep_cm_id", children=None),
                    html.Td(id="sim_new_rel_pep_cm_id", children=None),
                ]
            )
        )

        table_body = [html.Tbody(rows)]

        self.simulated_cm_component = dbc.Col(
                dbc.Table(table_header + table_body, bordered=False)
        )

    def assemble_middle_slider_component(self):
        """
        Assembles the middle slider component into one Dash card
        """
        price_component_col = dbc.Col(self.price_slider,)

        volume_component_col = dbc.Col(self.volume_slider,)

        self.middle_slider_component = dbc.Col(
            dbc.Card(
                children=[
                    html.H4(
                        "Currency",
                        className="Card-title",
                        style={
                            "color": config.app.colors.heading,
                            "marginTop": 10,
                            "marginLeft": 10,
                        },
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.RadioItems(
                                    id="currency_radio_buttons",
                                    options=[
                                        {"label": "Euro", "value": "euro"},
                                        {
                                            "label": "Local currency",
                                            "value": "local_currency",
                                        },
                                    ],
                                    value="euro",
                                    style={"marginTop": 10, "marginLeft": 15,},
                                ),
                            ]
                        ),
                        style={"marginTop": 10, "marginBottom": 10,},
                    ),
                    html.H4(
                        "Price mode",
                        className="Card-title",
                        style={
                            "color": config.app.colors.heading,
                            "marginTop": 0,
                            "marginLeft": 10,
                        },
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.RadioItems(
                                    id="price_radio_buttons",
                                    options=[
                                        {
                                            "label": "LLP wo/ CV",
                                            "value": "llp_mode",
                                            "disabled": False,
                                        },
                                        {"label": "NLP wo/ CV", "value": "nlp_mode"},
                                    ],
                                    value="nlp_mode",
                                    style={"marginTop": 10, "marginLeft": 15,},
                                ),
                            ]
                        ),
                        style={"marginTop": 10, "marginBottom": 10,},
                    ),
                    html.H4(
                        "Price input",
                        className="Card-title",
                        style={
                            "color": config.app.colors.heading,
                            "marginTop": 10,
                            "marginLeft": 10,
                        },
                    ),
                    dbc.Row(
                        [price_component_col, volume_component_col], no_gutters=True,
                    ),
                    dbc.Collapse(
                        id="abs_rel_component",
                        children=[
                            dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.RadioItems(
                                            id="abs_rel_radio_buttons",
                                            options=[
                                                {
                                                    "label": "Absolute",
                                                    "value": "abs_mode",
                                                },
                                                {
                                                    "label": "Relative",
                                                    "value": "rel_mode",
                                                },
                                            ],
                                            labelStyle={"margin-right": "35px",},
                                            value="rel_mode",
                                            style={"marginTop": 10, "marginLeft": 15,},
                                        ),
                                    ]
                                ),
                                style={"marginTop": 10, "marginBottom": 10,},
                            )
                        ],
                        is_open=True,
                    ),
                    dbc.Collapse(
                        id="discount_group_component",
                        children=[
                            html.H4(
                                "Discount group",
                                className="Card-title",
                                style={
                                    "color": config.app.colors.heading,
                                    "marginTop": 10,
                                    "marginLeft": 10,
                                },
                            ),
                            dbc.Card(
                                dcc.Dropdown(
                                    id="discount_group_dropdown",
                                    options=[],
                                    value=0,
                                    placeholder="Select a discount group",
                                    disabled=False,
                                ),
                                style={
                                    "marginTop": 5,
                                    "marginLeft": 15,
                                    "marginRight": 15,
                                    "padding": 0,
                                },
                            ),
                        ],
                        is_open=True,
                    ),
                    dbc.Collapse(
                        id="simulated_cm_component",
                        children=[
                            html.H4(
                                "Simulated KPIs",
                                className="Card-title",
                                style={
                                    "color": config.app.colors.heading,
                                    "marginTop": 15,
                                    "marginLeft": 10,
                                },
                            ),
                            self.simulated_cm_component,
                        ],
                        is_open=True,
                    ),
                    html.Div(id="nlp_llp_storage", style={"display": "none"}),
                    html.Div(id="currency_storage", style={"display": "none"}),
                ]
            ),
            width={"size": config.app.sizes.left_nav_component, "padding": 10},
        )

    def create(self):
        """
        Assembled the navbar (market + TNR input + KPIs + NLP and price input)
        """
        self.create_price_slider()
        self.create_volume_slider()
        self.create_simulated_cm_component()
        self.assemble_middle_slider_component()

        return self.middle_slider_component
