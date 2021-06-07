import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from src.simulation.plots import Plots
from src.utils.config import config


class Right_tabs:
    def create_break_even_kpis_component(self):
        """
        Create KPI table for the break even
        :return: KPI table wrapped in dbc.Col
        """
        table_header = [html.Thead(html.Tr([html.Th(""), html.Th("Value")]))]

        row1 = html.Tr(
            [
                html.Td("Relative volume change to break even"),
                # html.Td(id="volume_change_break_even", children=None),
            ]
        )
        row2 = html.Tr(
            [
                html.Td("Absolute volume change to break even"),
                # html.Td(id="abs_volume_change_break_even", children=None),
            ]
        )
        row3 = html.Tr(
            [
                html.Td("CM change if constant volume"),
                # html.Td(id="cm_change_break_even", children=None),
            ]
        )

        # table_body = [html.Tbody([row1, row2, row3])]

        break_even_kpis_component = dbc.Col(
            # dbc.Table(table_header + table_body, bordered=True), width=6
        )

        return break_even_kpis_component

    def create_simulation_table(self):
        """
        Create the simulation table based on config
        :return: simulation table in dbc.Table format
        """

        header = [html.Th("Key Performance Indicator")]
        row1_content = [html.Th("Simulation")]
        row2_content = [html.Td("Change")]
        row3_content = [html.Td("% Change")]

        html.Td("% Change"),

        for kpi in config.app.KPI_TABLE:
            c = config.app.KPI_TABLE[kpi]

            header.append(html.Th(c.label))
            row1_content.append(html.Td(id=kpi + "_sim", children=""))
            row2_content.append(html.Td(id=kpi + "_delta", children=""))
            row3_content.append(html.Td(id=kpi + "_delta_rel", children=""))

        table_header = [html.Thead(html.Tr(header))]

        row1 = html.Tr(row1_content)
        row2 = html.Tr(row2_content)
        row3 = html.Tr(row3_content)

        rowbr = html.Tr(html.Br(id='brid', hidden=False))
        cell_break_even_1 = [html.Th("Break Even (Contribution Margin)", id="Break_Even_Ratios", hidden=False)]
        cell_break_even_2 = [html.Td("Relative volume change to break even",
                                     id="Relative_volume_change_to_break_even", hidden=False)]
        cell_break_even_3 = [html.Td("Absolute volume change to break even",
                                     id="Absolute_volume_change_to_break_even", hidden=False)]
        cell_break_even_4 = [html.Td("CM change if constant volume",
                                     id="CM_change_if_constant_volume", hidden=False)]

        cell_break_even_1.append(html.Th("Value", id="Value_Info", hidden=False))
        cell_break_even_2.append(html.Td(id="volume_change_break_even", hidden=False))
        cell_break_even_3.append(html.Td(id="abs_volume_change_break_even", hidden=False))
        cell_break_even_4.append(html.Td(id="cm_change_break_even", hidden=False))

        row4 = html.Tr(cell_break_even_1)
        row5 = html.Tr(cell_break_even_2)
        row6 = html.Tr(cell_break_even_3)
        row7 = html.Tr(cell_break_even_4)

        table_body = [html.Tbody([row1, row2, row3, rowbr, row4, row5, row6, row7])]

        simulation_table = dbc.Table(table_header + table_body, bordered=True)

        return simulation_table

    def init_waterfall(self):
        # TODO resolve this function
        """
        Initialize waterfall with placeholder values.
        :return: empty waterfall simulation wrapped in html.Div
        """

        init_waterfall = Plots().create_waterfall()

        simulation_waterfall = html.Div(dcc.Graph(id="simulation_waterfall", figure=init_waterfall))

        return simulation_waterfall

    def create_tab_1(self, simulation_waterfall, simulation_table):
        """
        Create the tab 1 with the waterfall and table
        :param simulation_waterfall: waterfall simulation graph
        :param simulation_table: simulation table underneath waterfall
        :return: assembled tab_1
        """
        tab_1 = dbc.Row(
            dbc.Col(
                [
                    html.Div(
                        id="simulation_basis_info_id",
                        children="The simulation is based on the last 12 months rolling."
                    ),
                    simulation_waterfall,
                    simulation_table,
                ]
            ),
        )

        return tab_1

    def create_tab_2(self, figure, break_even_kpis):
        """
        Create tab 2 with break even view

        :param figure: break even graph
        :param break_even_kpis: KPI table underneath the graph
        :return: assembled tab_2
        """

        line_graph = html.Div(dcc.Graph(id="line_graph_breakdown", figure=figure))

        tab_2 = dbc.Row(dbc.Col([line_graph, break_even_kpis]),)

        return tab_2

    def create_tab_3(self, figure):
        """
        Create tab 3 with KPI view
        :param figure: KPI graph
        :return: assembled tab_3
        """
        tab_3 = html.Div(dcc.Graph(id="kpi_view", figure=figure,))

        return tab_3

    def create_tab1(self):
        # create tab 1 (waterfall + table)
        simulation_table = self.create_simulation_table()
        waterfall = self.init_waterfall()
        tab_1 = self.create_tab_1(waterfall, simulation_table)

        return tab_1

    def create_tab2(self):
        # create tab 2 (break even view)
        fig = Plots().create_line_graph()
        break_even_kpis = self.create_break_even_kpis_component()
        tab_2 = self.create_tab_2(fig, break_even_kpis)

        return tab_2

    def create_tab3(self):
        # create tab 3 (scenario comparison)
        kpi_fig = Plots().create_kpi_view(init=True)
        tab_3 = self.create_tab_3(kpi_fig)

        return tab_3
