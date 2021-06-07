import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import logging

from src.utils.config import config


class Left_nav:
    def __init__(
        self,
        # market_df: pd.DataFrame
    ):
        self._log = logging.getLogger(__name__)
        # self.market_df = market_df

    def create_aggregation_dropdown(self):
        """
        Creates the market selection dropdown in the nav bar
        """
        self.aggregation_dropdown = dcc.Dropdown(
            id="aggregation_dropdown",
            options=[
                {"label": "Part ID", "value": "part_id"},
                {"label": "MC ID", "value": "mc_id"},
                {"label": "Revenue Group", "value": "rg_id_fixed"},
                {"label": "Revenue Group M", "value": "rg_m_id"},
                {"label": "Revenue Group S", "value": "rg_s_id"},
            ],
            placeholder="Select an aggregation",
            value='part_id'
        )

        # todo remove country hardcoding

    def create_market_dropdown(self):
        """
        Creates the market selection dropdown in the nav bar
        """
        self.market_dropdown = dcc.Dropdown(
            id="market_dropdown",
            options=[
                {"label": "Austria", "value": "at"},
                {"label": "Belgium", "value": "be"},
                {"label": "Czech Republic", "value": "cz"},
                {"label": "Denmark", "value": "dk"},
                {"label": "France", "value": "fr"},
                {"label": "Germany", "value": "de"},
                {"label": "Great Britain", "value": "gb"},
                {"label": "Greece", "value": "gr"},
                {"label": "Italy", "value": "it"},
                {"label": "Netherlands", "value": "nl"},
                {"label": "Poland", "value": "pl"},
                {"label": "Portugal", "value": "pt"},
                {"label": "Romania", "value": "ro"},
                {"label": "Spain", "value": "es"},
                {"label": "Sweden", "value": "se"},
                {"label": "Switzerland", "value": "ch"},
            ],
            placeholder="Select a market",
        )

        # todo remove country hardcoding

    def create_part_dropdown(self):
        """
        Creates the part (TNR) selection dropdown in the nav bar
        """
        self.part_dropdown = dcc.Dropdown(
            id="part_dropdown", placeholder="Please select an ID",
        )

    def create_part_desc(self):
        """
        Creates the field to display the part description in the navbar
        """
        self.part_desc = dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="Part ID", style={"float": "left"}),
                            html.Div(
                                id="part_id",
                                children=None,
                                style={"float": "right"},
                            ),

                        ],
                     hidden = False, id ='part_id_info',
                    ),
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="Part ID desc.", style={"float": "left"}),
                            html.Div(
                                id="part_desc_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ],
                     hidden = False, id = 'part_desc_info',
                    ),
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="MC ID", style={"float": "left"}),
                            html.Div(
                                id="mc_id_id", children=None, style={"float": "right"}
                            ),
                        ],
                        hidden=False, id='mc_id_id_info',
                    ),
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="MC ID desc.", style={"float": "left"}),
                            html.Div(
                                id="mc_desc_id", children=None, style={"float": "right"}
                            ),
                        ],
                        hidden=False, id='mc_desc_id_info',
                    ),
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="RG ID.", style={"float": "left"}),
                            html.Div(
                                id="rg_id_fixed", children=None, style={"float": "right"}
                            ),
                        ],

                        hidden=False, id='rg_id_fixed_info',

                    ),
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="RG ID Desc.", style={"float": "left"}),
                            html.Div(
                                id="rg_id_fixed_desc", children=None, style={"float": "right"}
                            ),
                        ],
                        hidden=False, id='rg_id_fixed_desc_info',
                    ),
                ),
            ]
        )

    def create_kpis(self):
        """
        Creates the fields to show a selection of KPIs of a selected TNR
        """
        self.kpis = dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(
                                children="Sales Volume CP", style={"float": "left"}
                            ),
                            html.Div(
                                id="volume_id", children=None, style={"float": "right"},
                            ),
                        ]
                    )
                ),
                # dbc.ListGroupItem(
                #     html.Div(
                #         [
                #             html.Div(children="NR CP (PEP)", style={"float": "left"}),
                #             html.Div(
                #                 id="pep_nr_id", children=None, style={"float": "right"}
                #             ),
                #         ]
                #     )
                # ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="NR CP (MRA)", style={"float": "left"}),
                            html.Div(
                                id="mra_nr_id", children=None, style={"float": "right"}
                            ),
                        ]
                    )
                ),
                # dbc.ListGroupItem(
                #     html.Div(
                #         [
                #             html.Div(children="CM CP (PEP)", style={"float": "left"}),
                #             html.Div(
                #                 id="pep_cm_id", children=None, style={"float": "right"}
                #             ),
                #         ]
                #     )
                # ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="CM CP (MRA)", style={"float": "left"}),
                            html.Div(
                                id="mra_cm_id", children=None, style={"float": "right"}
                            ),
                        ]
                    )
                ),
                # dbc.ListGroupItem(
                #     html.Div(
                #         [
                #             html.Div(children="MRA Factor", style={"float": "left"}),
                #             html.Div(
                #                 id="mra_factor_id",
                #                 children=None,
                #                 style={"float": "right"},
                #             ),
                #         ]
                #     )
                # ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="VOLUME CP (PREV)", style={"float": "left"}),
                            html.Div(
                                id="vol_prev_development_id", children=None, style={"float": "right"}
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="NR CP (MRA)(PREV)", style={"float": "left"}),
                            html.Div(
                                id="mra_nr_prev_development_id", children=None, style={"float": "right"}
                            ),
                        ]
                    )
                ),

                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="CM CP (MRA)(PREV)", style={"float": "left"}),
                            html.Div(
                                id="mra_cm_prev_development_id", children=None, style={"float": "right"}
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="Market Share", style={"float": "left"}),
                            html.Div(
                                id="ms_id", children="TBD", style={"float": "right"}
                            ),
                        ],
                        hidden=False, id='ms_id_info',
                    ),
                    color="dark",
                ),
            ]
        )

    def create_pricing_kpis(self):
        """
        Creates fields to display the Cost and NLP of a selected TNR
        """
        self.pricing_kpis = dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="Cost (Var.)", style={"float": "left"}),
                            html.Div(
                                id="kpi_cost_var_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="Cost (Proc.)", style={"float": "left"}),
                            html.Div(
                                id="kpi_cost_proc_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ]
                    )
                ),
                # dbc.ListGroupItem(
                #     html.Div(
                #         [
                #             html.Div(children="CM (MRA) MRA FACTOR", style={"float": "left"}),
                #             html.Div(
                #                 id="kpi_mra_cm_unit_id",
                #                 children=None,
                #                 style={"float": "right"},
                #             ),
                #         ]
                #     )
                # ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="LLP wo/ CV", style={"float": "left"}),
                            html.Div(
                                id="kpi_llp_wo_cv_id", children=None, style={"float": "right"}
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="LLP", style={"float": "left"}),
                            html.Div(
                                id="kpi_llp_cv_id", children=None, style={"float": "right"}
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="MC Factor", style={"float": "left"}),
                            html.Div(
                                id="cm_mc_factor", children=None, style={"float": "right"}
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="NLP wo/ CV", style={"float": "left"}),
                            html.Div(
                                id="kpi_nlp_wo_cv_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="NLP", style={"float": "left"}),
                            html.Div(
                                id="kpi_nlp_cv_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="Discount rate", style={"float": "left"}),
                            html.Div(
                                id="kpi_discount_rate_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(
                                children="Discount group", style={"float": "left"}
                            ),
                            html.Div(
                                id="kpi_discount_group_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="W&G share", style={"float": "left"}),
                            html.Div(
                                id="kpi_wg_share_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(children="Elasticity", style={"float": "left"}),
                            html.Div(
                                id="kpi_elasticity_cat_id",
                                children=None,
                                style={"float": "right"},
                            ),
                        ]
                    )
                ),
            ]
        )

    def create_aggregated_kpis(self):
        """
        Creates fields to display the Cost and NLP of a selected TNR
        """
        self.mc_pricing = dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(
                                children="CM development", style={"float": "left"}
                            ),
                            html.Div(
                                id="cm_development_id", children="TBD", style={"float": "right"},
                            ),
                        ]
                    ),
                    # color="dark",
                ),
                dbc.ListGroupItem(
                    html.Div(
                        [
                            html.Div(
                                children="NR development", style={"float": "left"}
                            ),
                            html.Div(
                                id="nr_development_id",
                                children="TBD",
                                style={"float": "right"},
                            ),
                        ]
                    ),
                    # color="dark",
                ),
            ]
        )

    # def create_mc_view(self):
    #     """
    #     Creates fields to display the Cost and NLP of a selected TNR
    #     """
    #     self.mc_view = dbc.ListGroup(
    #         [
    #             dbc.ListGroupItem(
    #                 html.Div(
    #                     [
    #                         html.Div(
    #                             children="MC Factor", style={"float": "left"}
    #                         ),
    #                         html.Div(
    #                             id="cm_mc_factor", children=None, style={"float": "right"},
    #                         ),
    #                     ]
    #                 ),
    #                 # color="dark",
    #             ),
    #             dbc.ListGroupItem(
    #                 html.Div(
    #                     [
    #                         html.Div(
    #                             children="Sticker", style={"float": "left"}
    #                         ),
    #                         html.Div(
    #                             id="cm_sticker", children=None, style={"float": "right"},
    #                         ),
    #                     ]
    #                 ),
    #                 # color="dark",
    #             ),
    #             dbc.ListGroupItem(
    #                 html.Div(
    #                     [
    #                         html.Div(
    #                             children="PCI", style={"float": "left"}
    #                         ),
    #                         html.Div(
    #                             id="cm_pci", children=None, style={"float": "right"},
    #                         ),
    #                     ]
    #                 ),
    #                 # color="dark",
    #             ),
    #         ], id='mc_view_info'
    #     )

    def assemble_left_nav_component(self):
        """
        Takes the simulation of the nav bar and assembles it to one Dash card
        """
        self.left_nav_component = dbc.Col(
            dbc.Card(
                [
                    html.H4(
                        "Data Selection",
                        className="Card-title",
                        style={"color": config.app.colors.heading, "marginTop": 0},
                    ),
                    self.aggregation_dropdown,
                    self.market_dropdown,
                    self.part_dropdown,
                    self.part_desc,

                    html.H4(
                        "KPI",
                        className="Card-title",
                        style={"color": config.app.colors.heading, "marginTop": 10},
                    ),
                    self.kpis,

                    html.H4(
                        "Pricing",
                        className="Card-title",
                        style={"color": config.app.colors.heading, "marginTop": 10},
                        id='Pricing'
                    ),
                    dbc.Collapse(
                        id="part_pricing_card",
                        children=self.pricing_kpis,
                        is_open=True,
                    ),

                    # html.H4(
                    #     "MC View",
                    #     className="Card-title",
                    #     style={"color": config.app.colors.heading, "marginTop": 10},
                    # ),
                    # self.mc_view,
                    dbc.Collapse(
                        id="mc_pricing_card", children=self.mc_pricing, is_open=False
                    ),
                ],
                body=True,
                style={"height": config.app.sizes.nav_height, "padding": 10},
            ),
            width={"size": config.app.sizes.left_nav_component},
        )

    def create(self):
        """
        creates all parts of the left nav component

        Returns: dbc object
        """
        # TODO change part naming to something generic for the granularity change
        self.create_aggregation_dropdown()
        self.create_market_dropdown()
        self.create_part_dropdown()
        self.create_part_desc()
        self.create_kpis()
        self.create_pricing_kpis()
        # self.create_mc_view()
        self.create_aggregated_kpis()
        self.assemble_left_nav_component()

        return self.left_nav_component
