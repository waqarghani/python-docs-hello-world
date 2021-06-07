import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.utils.config import config

# TODO move to config
graph_height = 600


class Plots:
    """
    Holds all plots for the simulation app
    """

    def create_line_graph(self, cm=1, sim_cm=1, cur_sign="€"):
        """
        Creates the break even plot
        """

        perc_change_vol = (cm / sim_cm) - 1 if (sim_cm != 0) else 0.0

        y_min = -1
        x_min = 0
        n = 50
        figure = go.Figure(
            data=go.Scatter(
                x=[sim_cm, cm],
                y=[perc_change_vol, 0],
                line=dict(color="#707070", width=2, dash="solid"),
                hovertemplate="This line shows the relation between CM and volume change <extra></extra>",
                mode="lines+markers",
            )
        )

        # original cm vertical reference line
        figure.add_trace(
            go.Scatter(
                # x=[cm, cm],
                # y=[0, y_min],
                x=(n + 1) * [cm],
                y=[(i / n) * y_min for i in range(n + 1)],
                mode="lines",
                line={"color": "#444444", "dash": "dash", "width": 0.5},
                hovertemplate="This line shows the actual CM <extra></extra>",
            )
        )

        # x axis annotation
        figure = self.add_annotation(figure, cm, y_min, cm, 0, "Actual CM:", cur_sign)

        # original volume horizontal reference line
        figure.add_trace(
            go.Scatter(
                x=[x_min + (i / n) * abs(cm - x_min) for i in range(n + 1)],
                y=(n + 1) * [0],
                mode="lines",
                line={"color": "#444444", "dash": "dash", "width": 0.5},
                hovertemplate="This is the baseline volume <extra></extra>",
                #              text=["Custom text {}".format(i + 1) for i in range(5)],
            )
        )

        # new cm vertical reference line
        figure.add_trace(
            go.Scatter(
                x=(n + 1) * [sim_cm],
                y=[
                    y_min + (i / n) * abs(perc_change_vol - y_min) for i in range(n + 1)
                ],
                mode="lines",
                line={"color": "#71180C", "dash": "dash", "width": 1},
                hovertemplate="This line shows the simulated CM <extra></extra>",
            )
        )
        # new volume horizontal reference line
        figure.add_trace(
            go.Scatter(
                x=[x_min + (i / n) * abs(sim_cm - x_min) for i in range(n + 1)],
                y=(n + 1) * [perc_change_vol],
                mode="lines",
                line={"color": "#71180C", "dash": "dash", "width": 1},
                hovertemplate="This line indicates the volume change needed <br> "
                "to obtain the same relative CM baseline <extra></extra>",
            )
        )

        # new valume y axis annotation
        figure = self.add_annotation(
            figure,
            x_min,
            perc_change_vol,
            perc_change_vol * 100,
            120,
            "Volume change to break-even: ",
            "%",
        )

        # new cm x axis annotation
        figure = self.add_annotation(
            figure, sim_cm, y_min, sim_cm, 0, "Simulated CM: ", cur_sign
        )

        figure.layout.yaxis.tickformat = ",.0%"
        # figure.layout.yaxis.tickformat = ".,0%"

        figure.update_traces(textposition="bottom right")

        figure.layout.template = "plotly_white"
        figure.update_layout(
            # title="Simulation",
            xaxis_title="CM Simulation (" + cur_sign + ")",
            yaxis_title="Volume change",
            showlegend=False,
            height=graph_height,
            margin=dict(l=0, r=0, t=0, b=0),
        )

        return figure

    def create_waterfall(
        self,
        nr_baseline=0,
        constant_sim_nr=0,
        sim_nr=0,
        elasticity_nr_new=0,
        cm_baseline=0,
        constant_sim_cm=0,
        sim_cm=0,
        elasticity_cm_new=0,
        curr_sign="€",
        elasticity_nr_err_abs=0,
        elasticity_cm_err_abs=0,
    ):
        """
        Creates the waterfall plot on tab 1
        :param nr_baseline:
        :param nr_change_delta_nlp:
        :param nr_change_delta_volume:
        :param cost_actual:
        :param cost_sim:
        :param cm_sim:
        :param cm_baseline:
        :return:
        """
        values = [
            nr_baseline,
            constant_sim_nr,
            sim_nr,
            elasticity_nr_new,
            0,
            cm_baseline,
            constant_sim_cm,
            sim_cm,
            elasticity_cm_new,
        ]
        text_values_nr = [nr_baseline, constant_sim_nr, sim_nr, elasticity_nr_new]
        text_value_nr_text = []
        for value in text_values_nr:
            val = f"{value:,.{config.app.decimals}f} "
            pre, post = val.split('.')
            pre = pre.replace(',', '.')
            val = pre + ',' + post + curr_sign
            text_value_nr_text.append(val)

        text_values_cm = [cm_baseline, constant_sim_cm, sim_cm, elasticity_cm_new]
        text_value_cm_text = []
        for value in text_values_cm:
            val = f"{value:,.{config.app.decimals}f} "
            pre, post = val.split('.')
            pre = pre.replace(',', '.')
            val = pre + ',' + post + curr_sign
            text_value_cm_text.append(val)

        colors = ["#007A93"] + 3 * ["#C8C8C8"]

        fig = go.Figure(
            go.Bar(
                orientation="v",
                x=[
                    "NR CP (MRA) baseline",
                    "NR CP (delta price, const. volume)",
                    "NR CP (delta price, delta volume)",
                    "NR CP (elasticity)",
                    " ",
                    "CM CP (MRA) baseline",
                    "CM CP (delta price, const. volume)",
                    "CM CP (delta price, delta volume)",
                    "CM CP (elasticity)",
                ],
                error_y=dict(
                    type="data",
                    array=[
                        0,
                        0,
                        0,
                        elasticity_nr_err_abs,
                        0,
                        0,
                        0,
                        0,
                        elasticity_cm_err_abs,
                    ],
                ),
                textposition="outside",
                text=text_value_cm_text + [""] + text_value_nr_text,
                y=values,
                showlegend=False,
                marker_color=colors + ["White"] + colors,
            )
        )

        fig.layout.template = "plotly_white"

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0), height=8000,
        )

        to_value = max(*values) * 1.2 + 5
        from_value = min(*values) * 1.2 - 5
        fig.update_layout(yaxis=dict(range=[from_value, to_value]), height=graph_height)
        # fig.update_layout(title="Simulation waterfall", showlegend=True)
        return fig

    def _create_historic_line(
        self,
        fig,
        years,
        years_sim,
        kpi,
        kpi_sim,
        unit,
        row,
        col=1,
        name="",
        color="#707070",
        dash="solid",
        mode="lines",
        showlegend=False,
    ):
        """
        Adds historic lines for a KPI plus simulated values as one step ahead to a subplot of the KPI view
        :param fig: KPI view figure with two subplots
        :param years: list - years considered for historic data
        :param years_sim: list - current year plus one year ahead for simulated value
        :param kpi: the kpi values to plot
        :param kpi_sim: the simulated kpi value to plot
        :param unit: what unit the kpi value has
        :param row: row indicating if it is the subplot above or below
        :param col: what column of the subplots, defaults to 1
        :param name: KPI name inserted to describe the line
        :param color: colors of the historic line defaults to Daimler grey
        :param dash: style of the historic line
        :param mode: what mode the lines are plotted, defaults to lines only
        :param showlegend: indicates if the legend for the subplot should be plotted
        :return: subfigure with plotted lines
        """
        colors = ["#F08080", "#00FA9A", "#004355"]
        names = ["constant", "input", "elasticity"]
        # names = [f"{name} - {modes[i]}" for i in range(len(modes))]

        fig.add_trace(
            go.Scatter(
                x=years,
                y=kpi,
                name=name,
                mode=mode,
                meta=[name, unit],
                line=dict(color=color, width=2, dash=dash),
                hovertemplate="%{y:.0f} %{meta[1]}",
                showlegend=False,
                legendgroup="group1",
            ),
            row=row,
            col=col,
        )
        for i in range(len(kpi_sim)):
            fig.add_trace(
                go.Scatter(
                    x=years_sim,
                    y=kpi_sim[i],
                    name=names[i],
                    mode=mode,
                    meta=[names[i], unit],
                    line=dict(color=colors[i], width=1, dash="dash"),
                    hovertemplate="%{y:.0f} %{meta[1]}",
                    showlegend=showlegend,
                    legendgroup="group2",
                ),
                row=row,
                col=col,
            )

        fig.update_xaxes(dtick=1, fixedrange=True)

        fig.add_vrect(
            x0=years_sim[0],
            x1=years_sim[1],
            row=row,
            col=col,
            fillcolor="#E6E6E6",
            opacity=1,
            layer="below",
            line_width=0,
        )
        fig.add_vline(
            x=years_sim[0],
            row=row,
            col=col,
            opacity=1,
            line=dict(color="#707070", width=2, dash="dashdot"),
            layer="above",
        )

        fig.layout.template = "simple_white"

        return

    def create_kpi_view(self, historic_data=None, output_dict=None, init=False):
        """
        Aggregates all values and lines for the KPI view
        :param historic_data: list of lists, combining the listed historic data for all KPIs
        :param output_dict: main output dictionary with calculated values
        :param init: indicates if figure is initialized with no data
        :return: plotly figure
        """
        # TODO make years flexible
        years = [2016, 2017, 2018, 2019]
        sim_years = [years[-1]] + [years[-1] + 1]
        if init:
            empty = len(years) * [0]
            sim_empty = [
                len(sim_years) * [0],
                len(sim_years) * [0],
                len(sim_years) * [0],
            ]
            fig = make_subplots(
                rows=2,
                cols=1,
                subplot_titles=("Revenue and Contribution Margin", "Volume"),
            )

            self._create_historic_line(
                fig, years, sim_years, empty, sim_empty, unit="€", row=1, name="NR"
            )
            self._create_historic_line(
                fig, years, sim_years, empty, sim_empty, unit="€", row=1, name="CM"
            )
            self._create_historic_line(
                fig, years, sim_years, empty, sim_empty, unit=" ", row=2, name="VOL",
            )

            fig.layout.template = "simple_white"
            return fig
        # TODO add real elasticity data
        else:
            nr, cm, vol = historic_data
            cur_sign = output_dict["cur_sign"]
            constant_sim_nr = [nr[-1], output_dict["nr_cp_delta_price"]]
            input_sim_nr = [nr[-1], output_dict["nr_cp_delta_price_delta_volume"]]
            elasticity_sim_nr = [nr[-1], output_dict["elasticity_nr_new"]]
            sim_nr = [constant_sim_nr, input_sim_nr, elasticity_sim_nr]

            constant_sim_cm = [cm[-1], output_dict["cm_cp_delta_price"]]
            input_sim_cm = [cm[-1], output_dict["cm_cp_delta_price_delta_volume"]]
            elasticity_sim_cm = [cm[-1], output_dict["elasticity_cm_new"]]
            sim_cm = [constant_sim_cm, input_sim_cm, elasticity_sim_cm]

            constant_sim_vol = [vol[-1], vol[-1]]
            input_sim_vol = [vol[-1], output_dict["new_volume_cp"]]
            elasticity_sim_vol = [vol[-1], output_dict["elasticity_vol_new"]]
            sim_vol = [constant_sim_vol, input_sim_vol, elasticity_sim_vol]

            fig = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
                subplot_titles=("Revenue and Contribution Margin", "Volume"),
            )
            self._create_historic_line(
                fig, years, sim_years, nr, sim_nr, unit=cur_sign, row=1, name="NR"
            )
            self._create_historic_line(
                fig, years, sim_years, cm, sim_cm, unit=cur_sign, row=1, name="CM"
            )
            self._create_historic_line(
                fig,
                years,
                sim_years,
                vol,
                sim_vol,
                unit=" ",
                row=2,
                name="VOL",
                showlegend=True,
            )

            fig.update_yaxes(title_text=cur_sign, row=1, col=1, fixedrange=True)
            fig.update_yaxes(title_text="Units", row=2, col=1, fixedrange=True)
            fig.update_xaxes(title_text="Years", row=2, col=1, dtick=1, fixedrange=True)
            fig.update_layout(
                showlegend=True,
                autosize=True,
                legend=dict(yanchor="middle", y=0.5, xanchor="right", x=0.9),
                height=graph_height,
                margin=dict(l=0, r=0, t=30, b=0),
            )

            return fig

    def add_annotation(self, figure, x, y, value, ax, desc="", unit=""):
        """
        Helper function to set annotations on the plots
        """
        # y axis annotation
        figure.add_annotation(
            x=x,
            y=y,
            xref="x",
            yref="y",
            text=desc + f"{value:,.{config.app.decimals}f}" + unit,
            showarrow=False,
            font=dict(size=12, color="#ffffff"),
            align="left",
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#636363",
            bordercolor="#00677F",
            borderwidth=2,
            borderpad=4,
            bgcolor="#5097AB",
            opacity=0.9,
            xshift=ax,
        )

        return figure
