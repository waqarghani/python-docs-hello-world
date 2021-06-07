from dash.dependencies import Input, Output, State
from dash.dash import no_update
import math
import json
import numbers
import os

from src.utils.sql_reader import SqlReader
from src.simulation.plots import Plots
from src.simulation.calculations import Calculations
from src.simulation.helper import *

# set the environment variable depending on the os (nt = DSVM)
# this is used to run the app on the DSVM and deployed on Azure Web Apps
if os.name == "nt":
    ENVIRONMENT = "vm"
else:
    ENVIRONMENT = "azure_web_app"


class Callbacks:
    """
    This class defines all interactions in the app. All of those are defined as Dash callbacks
    """
    def __init__(self, app):
        """
        During the initialization of the callbacks all datasources are read that only
        need to be read once. Those are mainly to fill the dropdown menus with data.
        In addition lookup tables:
        - currency
        - market code mappings
        - 12 months rolling min and max months
        - ...
        """
        # getting possible options for the left_nav_component dropdowns
        # read the aggregation dimensions from the market cube to fill the dropdowns
        sql_reader = SqlReader(environment=ENVIRONMENT)
        df = sql_reader.read_query(
            "SELECT [market], [part_id],[rg_id_fixed],[rg_id_fixed_desc], [mc_id], [rg_m_id], [rg_s_id], [mc_desc]"
            + " FROM "
            + config.app.sql_data_sources.market_cube
        )

        # Get market factor from dB
        # self.market_factor = sql_reader.read_query(
        #     "SELECT [market], [mc_id], [market_factor_standard]"
        #     + " FROM "
        #     + config.app.sql_data_sources.market_factor
        # )

        # we want to save the existing market mapping.
        # Some tables have market ids (200, 559, ...) some have letters (DE, FR, ...)
        # with the market_mapping and reversed_market_mapping we are able to use any notation
        market_mapping = config.data_mapping.mra_logistic_market_mapping
        self.reversed_market_mapping = {v: k for k, v in market_mapping.items()}
        df["market_id"] = df["market"].map(self.reversed_market_mapping)

        # for the MRA table (last 12 months rolling) we need to get the last month
        # last month from the mra_monthly:
        mra_monthly_last_month = (
            sql_reader.read_query(
                "SELECT "
                + "max([month]) "
                + "FROM "
                + config.app.sql_data_sources.mra_monthly
                + ""
            )
            .iloc[0][0]
            .astype("str")
        )
        # get the last 12 months as a list that can be used as an index for the mra table
        self.mra_last_12_months, self.mra_previous_12_months = get_12_months_rolling(
            mra_monthly_last_month
        )

        # read the currency conversion table
        self.currency_conversion = sql_reader.read_query(
            "SELECT [market], [original_currency], [pep_currency_rate] FROM "
            + config.app.sql_data_sources.currency_table
            + " WHERE [year] = '"
            + CURRENT_YEAR
            + "'"
        )

        # read the dealer discount table with all available discount groups and rates for the discount dropdown
        self.pep_dealer_discount = sql_reader.read_query(
            "SELECT [market], [discount_group], [discount_rate] FROM "
            + config.app.sql_data_sources.discount_table
            + " WHERE [year] = '"
            + CURRENT_YEAR
            + "'"
        ).sort_values(by=["market", "discount_rate"])
        self.pep_dealer_discount["market"] = self.pep_dealer_discount[
            "market"
        ].str.lower()

        # read the elasticity table
        self.elasticity = sql_reader.read_query(
            "SELECT * FROM " + config.app.sql_data_sources.elasticity
        ).sort_values(by=["run_date", "market_id", "part_id"], ascending=False)
        self.elasticity.drop_duplicates(subset=["market_id", "part_id"], inplace=True)
        market_mapping = config.data_mapping.mra_logistic_market_mapping
        self.elasticity["market"] = self.elasticity["market_id"].map(market_mapping)

        # we want to always save the current level of aggregation in the data table
        # when the app starts it is initialized on part_id level

        df["agg_dim"] = "part_id"

        self.market_df = df

        self.plots = Plots()
        self.app = app
        self.calc = Calculations(self.pep_dealer_discount)

    def callback_part_ids(self, agg_level, market, search_entry):
        """
        Set the listed options in the level dropdown.
        :returns: List of options for the level dropdown
        """

        # set part_id as standard aggregation if nothing is selected yet
        if agg_level is None:
            agg_level = "part_id"



        # set the part_desc blank as this is not available in the aggregated views
        if agg_level != "part_id":
            self.market_df["part_desc"] = None


        # special case for mc_id: add description to options for the dropdown
        if agg_level == "mc_id":


            self.market_df["mc_desc"] = self.market_df["mc_desc"].fillna("?")
            self.market_df["dropdown_values"] = (
                self.market_df[agg_level] + " - " + self.market_df["mc_desc"]
            )

        else:
            self.market_df["dropdown_values"] = self.market_df[agg_level]
            # store the aggregation dimension in the data table. we need it in the load data callback
        self.market_df["agg_dim"] = agg_level

        #rg_id fixed
        if agg_level == "rg_id_fixed":
            agg_level = "rg_id_fixed"

            self.market_df["rg_id_fixed_desc"] = self.market_df["rg_id_fixed_desc"].fillna("?")
            self.market_df["dropdown_values"] = (
                # self.market_df[agg_level] + " - " +
                self.market_df["rg_id_fixed_desc"]
            )

        else:
            self.market_df["dropdown_values"] = self.market_df[agg_level]
            # store the aggregation dimension in the data table. we need it in the load data callback
        self.market_df["agg_dim"] = agg_level


        # list the first x ids if the market is not set
        if market is None:
            market_level_ids = list(set(self.market_df["dropdown_values"].unique()))

            market_level_ids = sorted(market_level_ids)

            return get_options_from_list(level_ids=market_level_ids)[:1000]

        # if the market is set, only show ids that exist in the market
        else:
            mask = self.market_df["market"] == market

            market_level_ids = list(
                set(self.market_df["dropdown_values"][mask].unique())
            )

            market_level_ids = sorted(market_level_ids)

            options = get_options_from_list(level_ids=market_level_ids)
            if search_entry is not None and len(search_entry) > 2:
                return [
                    o
                    for o in options
                    if o["label"].lower().startswith(search_entry.lower())
                ]
            else:
                return options[:1000]

    def callback_discount_dropdown(self, market):
        """
        Set the listed options in the discount dropdown.
        :returns: List of options for the discount dropdown
        """
        if market is None:
            return None
        else:
            discounts = self.pep_dealer_discount[
                self.pep_dealer_discount["market"].str.lower() == market
            ]

            available_discounts = discounts[["discount_group", "discount_rate"]]

            return get_discount_options(available_discounts)

    def callback_load_data(self, market, level_id, currency, agg_dim):
        """
        Load the data from the sources once the user has made a selection:
        - Market selected or changed
        - agg_level granularity level selected by the user
        - level_id selected or changed (part id, mc id, rg, ... depending on granularity level)
        :param agg_level: Granularity level selected by the user
        :return: dataframe base for all other calculations
        """

        # create the info text that shows the 12 months rolling timeframe
        simulation_timeframe_info = (
            "The simulation is based on the last 12 months rolling CP NR, CP CM and CP Qty ("
            + self.mra_last_12_months[0][4:]
            + "."
            + self.mra_last_12_months[0][:4]
            + " - "
            + self.mra_last_12_months[-1][4:]
            + "."
            + self.mra_last_12_months[-1][:4]
            + ")."
        )

        # return an empty dataframe if there is no market or part_id selected
        if (market is None) or (level_id is None) or (agg_dim is None):
            df_temp = pd.DataFrame()
            return df_temp.to_json(orient="split"), simulation_timeframe_info
        else:
            # the sql reader is initialized over and over again to prevent an idle timeout
            sql_reader = SqlReader(environment=ENVIRONMENT)

            # the level_id for the mc_id needs to have the description removed
            if agg_dim == "mc_id":
                level_id = level_id[:6]

            if agg_dim == "rg_id_fixed":
                level_id = level_id[:6]

            # read data from market cube depending on the users selection
            data = sql_reader.read_query(
                "SELECT"
                + "["
                + "], [".join(
                    cols
                )  # specific list of columns to be read from market cube
                + "]"
                + "FROM "
                + config.app.sql_data_sources.market_cube
                + "WHERE ["
                + agg_dim  # here is the aggregation dimension stored (e.g. Part id, MCID,...)
                + "] = '"
                + level_id  # selected part id or mc id or RG depending on aggregation level
                + "'"
                + " AND "
                + "[market] = '"
                + market
                + "'"
            )

            # stop here and return an empty dataframe if there is no data from the SQL DB
            if data.shape[0] == 0:
                df_temp = pd.DataFrame()
                return df_temp.to_json(orient="split"), simulation_timeframe_info

            # read the mra_monthly table for the 12 month rolling kpis
            mra_monthly_data = sql_reader.read_query(
                "SELECT "
                + "["
                + "], [".join(
                    mra_key_columns + mra_columns + ["month"]
                )  # specific list of columns to be read from market cube
                + "]"
                + "FROM "
                + config.app.sql_data_sources.mra_monthly
                + " WHERE ["
                + agg_dim  # here is the aggregation dimension stored (e.g. Part id, MCID,...)
                + "] = '"
                + level_id  # selected part id or mc id or RG depending on aggregation level
                + "'"
                + " AND "
                + "[market_code] = '"
                + self.reversed_market_mapping[market]
                + "'"
            )

            # fix the datatypes and fill NA values with zeros
            for c in mra_columns:
                mra_monthly_data[c] = mra_monthly_data[c].astype("float")
            mra_monthly_data = mra_monthly_data.fillna(0)

            # aggregate the values to the last 12 months
            last_12_months_df = aggregate_12_months(
                mra_monthly_data, self.mra_last_12_months
            )

            # merge the 12 months rolling with the market cube data
            # if there is no data (no data in the SQL table for the last 12 months)
            # create all columns with zeros
            if last_12_months_df.shape[0] > 0:
                data = data.merge(last_12_months_df, on=mra_key_columns, validate="1:1")
            else:
                for c in mra_columns:
                    data[c] = 0

            # aggregate the values to the previous 12 months
            previous_12_months_df = aggregate_12_months(
                mra_monthly_data, self.mra_previous_12_months
            )

            # merge the previous 12 months rolling with the market cube data
            # if there is no data (no data in the SQL table for the last 12 months)
            # create all columns with zeros
            if previous_12_months_df.shape[0] > 0:
                data = data.merge(
                    previous_12_months_df,
                    on=mra_key_columns,
                    suffixes=["", config.app.PREVIOUS_SUFFIX],
                    validate="1:1",
                )
            else:
                for c in mra_columns:
                    data[c + config.app.PREVIOUS_SUFFIX] = 0

            # fill remaining NAs with zeros
            data = data.fillna(0)

            # remove the CV from the prices
            data[NLP_KEY] = data[NLP_KEY] - data[CV_NET_KEY]
            data[LLP_KEY] = data[LLP_KEY] - data[CV_GROSS_KEY]

            # currency conversion if radio button is set to local currency
            if currency == "local_currency":
                currency_info = self.currency_conversion[
                    self.currency_conversion["market"] == market
                ].reset_index(drop=True)

                data["currency"] = currency_info["original_currency"]

                for column in currency_columns:
                    data[column] = data[column] * currency_info["currency_rate"][0]

                data[MRA_CM_KEY] = (
                    data[config.app.MRA_MONTHLY_CM_LOCAL_KEY]
                    - data[config.app.MRA_MONTHLY_WG_NR_LOCAL_KEY]
                )
                data[MRA_CM_KEY_PREVIOUS] = (
                    data[
                        config.app.MRA_MONTHLY_CM_LOCAL_KEY + config.app.PREVIOUS_SUFFIX
                    ]
                    - data[
                        config.app.MRA_MONTHLY_WG_NR_LOCAL_KEY
                        + config.app.PREVIOUS_SUFFIX
                    ]
                )
                data[MRA_NR_KEY] = data[config.app.MRA_MONTHLY_NR_LOCAL_KEY]
                data[MRA_NR_KEY_PREVIOUS] = data[
                    config.app.MRA_MONTHLY_NR_LOCAL_KEY + config.app.PREVIOUS_SUFFIX
                ]
            else:
                data["currency"] = "€"

                data[MRA_CM_KEY] = (
                    data[config.app.MRA_MONTHLY_CM_KEY]
                    - data[config.app.MRA_MONTHLY_WG_NR_KEY]
                )
                data[MRA_CM_KEY_PREVIOUS] = (
                    data[config.app.MRA_MONTHLY_CM_KEY + config.app.PREVIOUS_SUFFIX]
                    - data[
                        config.app.MRA_MONTHLY_WG_NR_KEY + config.app.PREVIOUS_SUFFIX
                    ]
                )
                data[MRA_NR_KEY] = data[config.app.MRA_MONTHLY_NR_KEY]
                data[MRA_NR_KEY_PREVIOUS] = data[
                    config.app.MRA_MONTHLY_NR_KEY + config.app.PREVIOUS_SUFFIX
                ]

            # add the elasticity to the datafroma
            data = data.merge(
                self.elasticity, on=["market", "part_id"], how="left", validate="1:1"
            )

            # if the there is no elasticity data available:
            data["elasticity"] = data["elasticity"].fillna(0)
            data["elasticity_std"] = data["elasticity_std"].fillna(0)
            data["ela_category"] = data["ela_category"].fillna("Not available")

            # the selected aggregaton is also stored in the table so it can be used later
            data["agg_dim"] = agg_dim

            # convert the dataframe to jsonm to it can be saved as a html component in the frontend
            return data.to_json(orient="split"), simulation_timeframe_info

    def callback_left_nav(self, df):
        """
        Set the KPIs of the left navigation component in line with chosen market and level.
        :param df: main dataframe
        :param market: selected market
        :param part_id: selected level id
        :return: values used to initialize the left navigation component
        """
        n_outputs = len(self.outputs_callback_left_nav)
        if df is None:
            return no_update
        df = pd.read_json(df, orient="split")

        if df.empty:
            return [None] * (n_outputs - 1) + [{}]
        else:
            part_series = df.iloc[0]
            part_id = part_series["part_id"]
            part_desc = part_series["part_desc"]
            mc_desc = part_series["mc_desc"]
            mc_id = part_series["mc_id"]
            rg_id_fixed = part_series["rg_id_fixed"]
            rg_id_fixed_desc = part_series["rg_id_fixed_desc"]
            cur_sign = part_series["currency"]

            volume = f"{df[VOL_KEY].sum():,.{config.app.decimals}f}"
            volume = int(float(volume))

            nlp_wo_cv = f"{part_series[NLP_KEY]:,.{config.app.decimals}f} "
            pre, post = nlp_wo_cv.split('.')
            pre = pre.replace(',', '.')
            nlp_wo_cv = pre + ',' + post + cur_sign

            nlp_cv = (
                f"{part_series[NLP_KEY] + part_series[CV_NET_KEY]:,.{config.app.decimals}f} "
            )
            pre, post = nlp_cv.split('.')
            pre = pre.replace(',', '.')
            nlp_cv = pre + ',' + post + cur_sign

            llp_wo_cv = f"{part_series[LLP_KEY]:,.{config.app.decimals}f} "
            pre, post = llp_wo_cv.split('.')
            pre = pre.replace(',', '.')
            llp_wo_cv = pre + ',' + post + cur_sign

            llp_cv = (
                f"{part_series[LLP_KEY] + part_series[CV_GROSS_KEY]:,.{config.app.decimals}f} "
            )
            pre, post = llp_cv.split('.')
            pre = pre.replace(',', '.')
            llp_cv = pre + ',' + post + cur_sign

            cost_var = (
                f"{df[VARIABLE_COST_KEY].sum():,.{config.app.decimals}f} "
            )
            pre, post = cost_var.split('.')
            pre = pre.replace(',', '.')
            cost_var = pre + ',' + post + cur_sign

            cost_proc = (
                f"{df[PROCUREMENT_COST_KEY].sum():,.{config.app.decimals}f} "
            )
            pre, post = cost_proc.split('.')
            pre = pre.replace(',', '.')
            cost_proc = pre + ',' + post + cur_sign

            mra_nr_actual = (
                f"{df[MRA_NR_KEY].sum():,.{config.app.decimals}f} "
            )
            pre, post = mra_nr_actual.split('.')
            pre = pre.replace(',', '.')
            mra_nr_actual = pre + ',' + post + cur_sign

            mra_cm_actual = (
                f"{df[MRA_CM_KEY].sum():,.{config.app.decimals}f} "
            )
            pre, post = mra_cm_actual.split('.')
            pre = pre.replace(',', '.')
            mra_cm_actual = pre + ',' + post + cur_sign
            # if len(mra_cm_actual) > 7:
            #     pre, post = mra_cm_actual.split('.')
            #     pre = pre.replace(',', '.')
            #     mra_cm_actual = pre + ',' + post + cur_sign
            # else:
            #     mra_cm_actual = mra_cm_actual + cur_sign
            #     mra_cm_actual = mra_cm_actual.replace('.', ',')

            kpi_discount_rate = f"{part_series[MARKET_DISCOUNT_RATE_KEY] * 100:,.{config.app.decimals}f} "
            pre, post = kpi_discount_rate.split('.')
            pre = pre.replace(',', '.')
            kpi_discount_rate = pre + ',' + post + '%'

            if part_series["agg_dim"] == "part_id":
                kpi_discount_group_dropdown = str(
                    part_series[MARKET_DISCOUNT_GROUP_KEY]
                )
            # elif part_series["agg_dim"] != "part_id":
            #     part_id = None
            else:
                kpi_discount_group_dropdown = None
                part_id = None
                part_desc = None

            kpi_wg_share_id = (
                f"{part_series[WG_SHARE_KEY] * 100:,.{config.app.decimals}f} "
            )
            pre, post = kpi_wg_share_id.split('.')
            pre = pre.replace(',', '.')
            kpi_wg_share_id = pre + ',' + post + '%'

            kpi_elasticity_cat_id = f"{part_series[ELASTICITY_CAT_KEY]}"

            market_discount_group = f"{part_series[MARKET_DISCOUNT_GROUP_KEY]}"

            # development KPIs

            # TODO check what should happen when the previous 12 months are 0
            nr_development = 0
            if df[MRA_NR_KEY_PREVIOUS].sum() > 0:
                nr_development = f"{math.floor((df[MRA_NR_KEY].sum() / df[MRA_NR_KEY_PREVIOUS].sum() - 1) * 100):,.{config.app.decimals}f} %"
            elif df[MRA_NR_KEY_PREVIOUS].sum() == 0:
                nr_development = "NA"

            # nr_development =  f"{df[MRA_NR_KEY].sum() / df[MRA_NR_KEY_PREVIOUS].sum():,.{config.app.decimals}f} %"

            cm_development = 0

            if df[MRA_CM_KEY_PREVIOUS].sum() > 0:

                cm_development = f"{math.floor((df[MRA_CM_KEY].sum() / df[MRA_CM_KEY_PREVIOUS].sum() - 1) * 100):,.{config.app.decimals}f} %"
            elif df[MRA_CM_KEY_PREVIOUS].sum() == 0:
                cm_development = "NA"

            vol_prev_development_id = (
                f"{df[VOL_KEY_PREVIOUS].sum():,.{config.app.decimals}f}"
            )
            vol_prev_development_id = int(float(vol_prev_development_id))

            mra_nr_prev_development_id = (
                f"{df[MRA_NR_KEY_PREVIOUS].sum():,.{config.app.decimals}f}"
            )
            pre, post = mra_nr_prev_development_id.split('.')
            pre = pre.replace(',', '.')
            mra_nr_prev_development_id = pre + ',' + post + ' ' + cur_sign

            mra_cm_prev_development_id = (
                f"{df[MRA_CM_KEY_PREVIOUS].sum():,.{config.app.decimals}f}"
            )
            pre, post = mra_cm_prev_development_id.split('.')
            pre = pre.replace(',', '.')
            mra_cm_prev_development_id = pre + ',' + post + ' ' + cur_sign

            # # MC VIEW
            # mc_id = mc_id.strip()
            # # print('***mc_id: ', mc_id)
            # current_market = df["market"].iloc[0].strip()
            # # print('***current_market: ', current_market)
            #
            # # print('***current_market filter:')
            # # a = self.market_factor[self.market_factor['market'] == current_market]
            # # print(a.values)
            # #
            # # print('***mc_id filter:')
            # # b = a[a['mc_id'] == mc_id].values
            # # print(b)
            #
            # mc_factor = self.market_factor[
            #     (self.market_factor['market'] == current_market)
            #     & (self.market_factor['mc_id'] == mc_id)
            # ]
            #
            # if mc_factor.shape[0] > 0:
            #     mc_factor = mc_factor['market_factor_standard'].values[0]
            #     mc_factor = str(mc_factor)
            #     pre, post = mc_factor.split('.')
            #     pre = pre.replace(',', '.')
            #     mc_factor = pre + ',' + post
            # else:
            #     mc_factor = 'Sticker'
            #
            # # TODO: Define logic to identify when to add PCI >> If the pci is active then show (how to check if PCI is active, katharina will tell later once the data is ready for this)
            # # mc_factor = str(mc_factor) + ' (PCI)'

            # print('***mc_factor: ', mc_factor)

            mc_factor = 'Data NA'

            # for name, value in zip(
            #         ['part_id', 'part_desc', 'mc_desc', 'mc_id', 'rg_id_fixed', 'rg_id_fixed_desc', 'volume',
            #          'mra_nr_actual', 'llp_wo_cv', 'nlp_wo_cv', 'llp_cv', 'nlp_cv', 'cost_var', 'cost_proc',
            #          'mra_cm_actual', 'kpi_discount_rate', 'kpi_discount_group_dropdown', 'kpi_wg_share_id',
            #          'kpi_elasticity_cat_id', 'market_discount_group', 'nr_development', 'cm_development',
            #          'vol_prev_development_id', 'mra_nr_prev_development_id', 'mra_cm_prev_development_id'],
            #         [part_id, part_desc, mc_desc, mc_id, rg_id_fixed, rg_id_fixed_desc, volume, mra_nr_actual,
            #          llp_wo_cv, nlp_wo_cv, llp_cv, nlp_cv, cost_var, cost_proc, mra_cm_actual, kpi_discount_rate,
            #          kpi_discount_group_dropdown, kpi_wg_share_id, kpi_elasticity_cat_id, market_discount_group,
            #          nr_development, cm_development, vol_prev_development_id, mra_nr_prev_development_id,
            #          mra_cm_prev_development_id]):
            #     print('- ', name, ' : ', value)

            return (
                part_id,
                part_desc,
                mc_desc,
                mc_id,
                rg_id_fixed,
                rg_id_fixed_desc,
                volume,
                mra_nr_actual,
                llp_wo_cv,
                nlp_wo_cv,
                llp_cv,
                nlp_cv,
                cost_var,
                cost_proc,
                mra_cm_actual,
                kpi_discount_rate,
                kpi_discount_group_dropdown,
                kpi_wg_share_id,
                kpi_elasticity_cat_id,
                market_discount_group,
                nr_development,
                cm_development,
                vol_prev_development_id,
                mra_nr_prev_development_id,
                mra_cm_prev_development_id,
                mc_factor,
                # sticker,
                # pci
            )

    def callback_simulation_data(self, df, price_input, volume_input, nlp_llp, discount_group, abs_rel_mode):
        """
        Calculate and save output dictionary for all simulation values
        :param df: main dataframe
        :param market: selected market
        :param part_id: selected level id
        :param nlp_new: selected price change
        :param volume_change_perc: selected volume change
        :return: dictionary containing all used values
        """
        if df is None:
            return {}
        df = pd.read_json(df, orient="split")
        if df.empty:
            return {}
        else:
            if abs_rel_mode == "rel_mode":
                if price_input is None:
                    price_input = 0
                if volume_input is None:
                    volume_input = 0
                price_change_perc = price_input / 100
                volume_change_perc = volume_input / 100

            # case handling for the absolute price mode (radio button user selection)
            elif abs_rel_mode == "abs_mode":
                if price_input is None:
                    price_change_perc = 0
                else:
                    if nlp_llp == "nlp_mode":
                        price_change_perc = price_input / df[NLP_KEY][0] - 1
                    elif nlp_llp == "llp_mode":
                        price_change_perc = price_input / df[LLP_KEY][0] - 1

                if volume_input is None:
                    volume_change_perc = 0
                else:
                    if df[VOL_KEY][0] > 0:
                        volume_change_perc = volume_input / df[VOL_KEY][0] - 1
                    else:
                        volume_change_perc = volume_input
            else:
                price_change_perc = 0
                volume_change_perc = 0

            # get market to get discount rates
            current_market = df["market"].iloc[0]

            # call the actual simulation function to get all simulation values
            cost_var = float(df[VARIABLE_COST_KEY].sum())
            # print('***** cost_var: >>> ', cost_var)
            output_dict = self.calc.get_sim_data(
                df,
                price_change_perc,
                volume_change_perc,
                nlp_llp,
                discount_group,
                current_market,
                cost_var,
            )

            output_dict = fix_dtypes_for_json(output_dict)

            return json.dumps(output_dict)

    def callback_sim_table(self, output_dict):
        """
        Set simulation table values (simulated, delta, delta relative)
        :param output_dict: main output dictionary
        :return:
        """
        output_dict = json.loads(str(output_dict))
        output_list = []
        # for key, val in output_dict.items():
        #     print(f'*** {key:<50}: {val}')
        # print('\n\n')
        if output_dict == {}:
            for _ in config.app.KPI_TABLE:
                output_list.append(None)  # simulated
                output_list.append(None)  # delta
                output_list.append(None)  # delta relative
            return output_list

        for kpi in config.app.KPI_TABLE:
            c = config.app.KPI_TABLE[kpi]

            if c.unit == None:
                unit = ""
            else:
                unit = output_dict[c.unit]

            output_list = get_table_kpis(
                output_list,
                output_dict[c.actual_value],
                output_dict[c.sim_value],
                unit=unit,
            )

        return output_list

    def callback_cm_component(self, output_dict):
        """
        Set simulated cm component values
        :param output_dict: main output dictionary
        :return: absolute cm per unit and relative cm
        """
        output_dict = json.loads(str(output_dict))
        if output_dict == {}:
            return [None for _ in self.outputs_sim_cm]
        else:
            # calculate and format all KPIs for the simulated KPI table
            cur_sign = output_dict["cur_sign"]

            sim_llp = f"{output_dict['sim_llp']:,.{config.app.decimals}f} "
            pre, post = sim_llp.split('.')
            pre = pre.replace(',', '.')
            sim_llp = pre + ',' + post + cur_sign

            sim_nlp = f"{output_dict['sim_nlp']:,.{config.app.decimals}f} "
            pre, post = sim_nlp.split('.')
            pre = pre.replace(',', '.')
            sim_nlp = pre + ',' + post + cur_sign

            llp_cv_new = (
                f"{output_dict['sim_llp'] + output_dict['cv_gross_new']:,.{config.app.decimals}f} "
            )
            pre, post = llp_cv_new.split('.')
            pre = pre.replace(',', '.')
            llp_cv_new = pre + ',' + post + cur_sign
            nlp_cv_new = (
                f"{output_dict['sim_nlp'] + output_dict['cv_net_new']:,.{config.app.decimals}f} "
            )
            pre, post = nlp_cv_new.split('.')
            pre = pre.replace(',', '.')
            nlp_cv_new = pre + ',' + post + cur_sign

            pep_cm_unit_sim = (
                f"{output_dict['pep_cm_unit_sim']:,.{config.app.decimals}f} "
            )
            pre, post = pep_cm_unit_sim.split('.')
            pre = pre.replace(',', '.')
            pep_cm_unit_sim = pre + ',' + post + cur_sign

            pep_cm_sim_relative = (
                f"{output_dict['pep_cm_sim_relative'] * 100:,.{config.app.decimals}f} "
            )
            pre, post = pep_cm_sim_relative.split('.')
            pre = pre.replace(',', '.')
            pep_cm_sim_relative = pre + ',' + post + '%'

            discount_rate = (
                f"{output_dict['discount_rate'] * 100:,.{config.app.decimals}f} "
            )
            pre, post = discount_rate.split('.')
            pre = pre.replace(',', '.')
            discount_rate = pre + ',' + post + '%'

            llp_actual = (
                    f"{output_dict['llp_actual']:,.{config.app.decimals}f} " + cur_sign
            )
            pre, post = llp_actual.split('.')
            pre = pre.replace(',', '.')
            llp_actual = pre + ',' + post + cur_sign

            llp_cv_actual = (
                f"{output_dict['llp_actual'] + output_dict['cv_gross_actual']:,.{config.app.decimals}f} "
            )
            pre, post = llp_cv_actual.split('.')
            pre = pre.replace(',', '.')
            llp_cv_actual = pre + ',' + post + cur_sign

            nlp_actual = (
                f"{output_dict['nlp_actual']:,.{config.app.decimals}f} "
            )
            pre, post = nlp_actual.split('.')
            pre = pre.replace(',', '.')
            nlp_actual = pre + ',' + post + cur_sign

            nlp_cv_actual = (
                f"{output_dict['nlp_actual'] + output_dict['cv_net_actual']:,.{config.app.decimals}f} "
            )
            pre, post = nlp_cv_actual.split('.')
            pre = pre.replace(',', '.')
            nlp_cv_actual = pre + ',' + post + cur_sign

            pep_cm_unit_actual = (
                f"{output_dict['pep_cm_unit_actual']:,.{config.app.decimals}f} "
            )
            pre, post = pep_cm_unit_actual.split('.')
            pre = pre.replace(',', '.')
            pep_cm_unit_actual = pre + ',' + post + cur_sign

            pep_cm_actual_relative = f"{output_dict['pep_cm_actual_relative'] * 100:,.{config.app.decimals}f} "
            pre, post = pep_cm_actual_relative.split('.')
            pre = pre.replace(',', '.')
            pep_cm_actual_relative = pre + ',' + post + '%'

            discount_rate_actual = (
                f"{output_dict['discount_rate_actual'] * 100:,.{config.app.decimals}f} "
            )
            pre, post = discount_rate_actual.split('.')
            pre = pre.replace(',', '.')
            discount_rate_actual = pre + ',' + post + '%'

            cv_net_actual = (
                f"{output_dict['cv_net_actual']:,.{config.app.decimals}f} "
            )
            pre, post = cv_net_actual.split('.')
            pre = pre.replace(',', '.')
            cv_net_actual = pre + ',' + post + cur_sign

            cv_net_new = (
                f"{output_dict['cv_net_new']:,.{config.app.decimals}f} "
            )
            pre, post = cv_net_new.split('.')
            pre = pre.replace(',', '.')
            cv_net_new = pre + ',' + post + cur_sign

            cv_gross_actual = (
                f"{output_dict['cv_gross_actual']:,.{config.app.decimals}f} "
            )
            pre, post = cv_gross_actual.split('.')
            pre = pre.replace(',', '.')
            cv_gross_actual = pre + ',' + post + cur_sign

            cv_gross_new = (
                f"{output_dict['cv_gross_new']:,.{config.app.decimals}f} "
            )
            pre, post = cv_gross_new.split('.')
            pre = pre.replace(',', '.')
            cv_gross_new = pre + ',' + post + cur_sign

            # for name, value in zip(
            #         ['sim_llp', 'sim_nlp', 'pep_cm_unit_sim', 'pep_cm_sim_relative', 'discount_rate', 'llp_actual',
            #          'nlp_actual', 'pep_cm_unit_actual', 'pep_cm_actual_relative', 'discount_rate_actual',
            #          'cv_net_actual', 'cv_net_new', 'cv_gross_actual', 'cv_gross_new', 'llp_cv_actual', 'nlp_cv_actual',
            #          'llp_cv_new', 'nlp_cv_new'],
            #         [sim_llp, sim_nlp, pep_cm_unit_sim, pep_cm_sim_relative, discount_rate, llp_actual, nlp_actual,
            #          pep_cm_unit_actual, pep_cm_actual_relative, discount_rate_actual, cv_net_actual, cv_net_new,
            #          cv_gross_actual, cv_gross_new, llp_cv_actual, nlp_cv_actual, llp_cv_new, nlp_cv_new]):
            #     print('- ', name, ' : ', value)

            return (
                sim_llp,
                sim_nlp,
                pep_cm_unit_sim,
                pep_cm_sim_relative,
                discount_rate,
                llp_actual,
                nlp_actual,
                pep_cm_unit_actual,
                pep_cm_actual_relative,
                discount_rate_actual,
                cv_net_actual,
                cv_net_new,
                cv_gross_actual,
                cv_gross_new,
                llp_cv_actual,
                nlp_cv_actual,
                llp_cv_new,
                nlp_cv_new,
            )

    def callback_waterfall(self, output_dict):
        """
        Update values in waterfall simulation
        :param output_dict: main output dictionary
        :return: output values for the waterfall simulation
        """
        output_dict = json.loads(str(output_dict))
        if not output_dict:
            _simulation_waterfall = self.plots.create_waterfall()
            return _simulation_waterfall
        else:
            cur_sign = output_dict["cur_sign"]
            _simulation_waterfall = self.plots.create_waterfall(
                nr_baseline=output_dict["mra_nr_actual"],
                constant_sim_nr=output_dict["nr_cp_delta_price"],
                sim_nr=output_dict["nr_cp_delta_price_delta_volume"],
                elasticity_nr_new=output_dict["elasticity_nr_new"],
                cm_baseline=output_dict["mra_cm_actual"],
                constant_sim_cm=output_dict["cm_cp_delta_price"],
                sim_cm=output_dict["cm_cp_delta_price_delta_volume"],
                elasticity_cm_new=output_dict["elasticity_cm_new"],
                curr_sign=cur_sign,
                elasticity_nr_err_abs=output_dict["elasticity_nr_err_abs"],
                elasticity_cm_err_abs=output_dict["elasticity_cm_err_abs"],
            )

            return _simulation_waterfall

    def callback_breakeven(self, output_dict):
        """
        Update values in break even simulation
        :param output_dict: main output dictionary
        :param args: current states of the waterfall in case output dictionary is empty
        :return: output values for the break even simulation
        """
        output_dict = json.loads(str(output_dict))
        if not bool(output_dict):
            fig = self.plots.create_line_graph()
            return [fig] + (len(self.outputs_sim_breakeven) - 1) * [None]
        else:
            fig = self.plots.create_line_graph(
                output_dict["mra_cm_actual"],
                output_dict["cm_cp_delta_price_delta_volume"],
                output_dict["cur_sign"],
            )

            # for key, val in output_dict.items():
            #     print(f'- {key}: {val}')

            cur_sign = output_dict["cur_sign"]

            output_dict = {
                key: f"{val:,.{config.app.decimals}f}"
                if isinstance(val, numbers.Number)
                else val
                for key, val in output_dict.items()
            }

            # print('@@@output_dict:')
            # for key, val in output_dict.items():
            #     print(f'- {key: <30}: {repr(val)}')

            if '.' in output_dict['perc_vol_change_break_even']:
                pre, post = output_dict['perc_vol_change_break_even'].split('.')
                pre = pre.replace(',', '.')
                output_dict['perc_vol_change_break_even'] = pre + ',' + post
            else:
                output_dict['perc_vol_change_break_even'] = '0,00'

            output_breakeven = (
                [fig]
                + [f"{output_dict['perc_vol_change_break_even']} %"]
                + [f"{output_dict['abs_vol_change_break_even']} "]
                + [f"{output_dict['sim_delta_cm']} " + cur_sign]
            )


            return output_breakeven

    def callback_disable_breakeven(self, tab, value_state):
        """
        Disable volume slider when break even view is shown
        :param tab: indicates what tab is shown
        :param value_state: is the current value the volume slider is set to
        :return: disabled status and value for volume slider
        """
        if tab == "tab-2":
            return True, 0
        else:
            return False, value_state

    def callback_kpi_view(self, df, output_dict):
        """
        Update the KPI view simulation.
        :param df: main dataframe
        :param market: selected market
        :param part_id: selected level id
        :param nlp_new: selected price change
        :param volume_change_perc: selected volume change
        :param output_dict: main output dictionary
        :return: KPI view figure
        """
        if df is None:
            return self.plots.create_kpi_view(init=True)
        df = pd.read_json(df, orient="split")
        if df.empty:
            return self.plots.create_kpi_view(init=True)
        output_dict = json.loads(str(output_dict))
        historic_data = self.calc.historic_data(df,)
        fig = self.plots.create_kpi_view(historic_data, output_dict)
        return fig

    def callback_disable_inputs(self, agg_level, nlp_llp, abs_rel_radio_button_value):
        """
        Disables user inputs that are only available in part_id mode.
        :param agg_level: selected aggregation level (part id, mc id, ...)
        :param nlp_llp: selected price mode (NLP or NLP mode)
        :param abs_rel_radio_button_value: selected price input mode (relative or absolute)
        :return: list change the html component values
        """
        if agg_level == "rg_id_fixed":
            mc_id_id_info = True
            mc_desc_id_info = True
            # mc_view_info = True
        else:
            mc_id_id_info = False
            mc_desc_id_info = False
            # mc_view_info = True

        if agg_level == "mc_id":
            ms_id_info = True  # in mc_id
            rg_id_fixed_info = True
            rg_id_fixed_desc_info = True
            # mc_view_info = False

        else:
            ms_id_info = False  # not mc id
            rg_id_fixed_info = False
            rg_id_fixed_desc_info = False
            # mc_view_info = False

        if agg_level == "part_id":
            # mc_view_info = False
            simulated_cm_component = True
            part_pricing_card = True
            mc_pricing_card = False
            discount_group_dropdown = False
            discount_group_component = True
            abs_rel_button = abs_rel_radio_button_value
            abs_rel_component = True
            part_id_info = False  # not mc id
            part_desc_info = False  # not mc id
            Pricing = False  # not part id
            #CM table hide
            brid = False
            Break_Even_Ratios = False
            Value_Info = False
            Relative_volume_change_to_break_even = False
            volume_change_break_even = False
            Absolute_volume_change_to_break_even = False
            abs_volume_change_break_even = False
            CM_change_if_constant_volume = False
            cm_change_break_even = False
        else:
            # mc_view_info = False
            simulated_cm_component = False  # disable
            part_pricing_card = False  # disable
            mc_pricing_card = True  # hide card
            discount_group_dropdown = True  # hide dropdown
            discount_group_component = False  # disable
            abs_rel_button = "rel_mode"  # force relative mode
            abs_rel_component = False  # disable
            part_id_info = True  # in mc_id
            part_desc_info = True  # mc_id
            Pricing = True  # in part_id
            #cm tabe hide
            brid = True
            Break_Even_Ratios = True
            Value_Info = True
            Relative_volume_change_to_break_even = True
            volume_change_break_even = True
            Absolute_volume_change_to_break_even = True
            abs_volume_change_break_even = True
            CM_change_if_constant_volume = True
            cm_change_break_even = True

        if nlp_llp == "nlp_mode":
            discount_group_dropdown = (
                True  # disable discount group dropdown in nlp mode
            )

        return (
            simulated_cm_component,
            part_pricing_card,
            mc_pricing_card,
            discount_group_dropdown,
            discount_group_component,
            abs_rel_button,
            abs_rel_component,
            part_id_info,
            part_desc_info,
            ms_id_info,
            Pricing,
            mc_id_id_info,
            mc_desc_id_info,
            rg_id_fixed_info,
            rg_id_fixed_desc_info,
            #cm table hide
            brid,
            Break_Even_Ratios,
            Value_Info,
            Relative_volume_change_to_break_even,
            volume_change_break_even,
            Absolute_volume_change_to_break_even,
            abs_volume_change_break_even,
            CM_change_if_constant_volume,
            cm_change_break_even,
            # mc_view_info
        )

    def callback_abs_rel_buttons(self, abs_rel_button_value,):
        """
        Changes the labels of the price inputs depending on the pricing mode
        :param df:
        :return:
        """
        if abs_rel_button_value == "abs_mode":
            price_test = "New price"
            volume_test = "New volume"

        else:
            price_test = "Price change (%)"
            volume_test = "Volume change (%)"

        return price_test, volume_test

    def set_inputs(self):
        """
        Set inputs for all callbacks
        :return: initialized inputs for all callbacks
        """
        self.inputs_data = [
            Input(component_id="market_dropdown", component_property="value"),
            Input(component_id="part_dropdown", component_property="value"),
            Input(component_id="currency_radio_buttons", component_property="value"),
            Input(component_id="aggregation_dropdown", component_property="value"),
        ]

        self.inputs_callback_part_id = [
            Input(component_id="aggregation_dropdown", component_property="value"),
            Input(component_id="market_dropdown", component_property="value"),
            Input(component_id="part_dropdown", component_property="search_value"),
        ]

        self.inputs_callback_discount_dropdown = [Input(component_id="market_dropdown", component_property="value")]

        self.inputs_callback_left_nav = [Input(component_id="input_data_storage", component_property="children")]

        self.inputs_sim_data = [
            Input(component_id="input_data_storage", component_property="children"),
            Input(component_id="new_nlp", component_property="value"),
            Input(component_id="volume_change_perc", component_property="value"),
            Input(component_id="price_radio_buttons", component_property="value"),
            Input(component_id="discount_group_dropdown", component_property="value"),
            Input(component_id="abs_rel_radio_buttons", component_property="value"),
        ]

        self.inputs_sim = [Input(component_id="simulation_data_storage", component_property="children"),]

        self.inputs_kpi_view = [
            Input(component_id="input_data_storage", component_property="children"),
            Input(component_id="simulation_data_storage", component_property="children"),
        ]

        self.inputs_disable_breakeven = [Input(component_id="tabs-example", component_property="value")]

        self.inputs_disable_inputs = [
            Input(component_id="aggregation_dropdown", component_property="value"),
            Input(component_id="price_radio_buttons", component_property="value"),
        ]

        self.inputs_abs_rel_buttons = Input(component_id="abs_rel_radio_buttons", component_property="value")

        self.inputs_sim_table = [Input(component_id="simulation_data_storage", component_property="children")]

    def set_states(self):
        """
        Set states for callbacks in which current properties need to be passed on to the callback
        :returns: Initialized states
        """
        self.states_disable_breakeven = State(component_id="volume_change_perc", component_property="value")
        self.states_disable_inputs = State(component_id="abs_rel_radio_buttons", component_property="value")

    def set_outputs(self):
        """
        Set outputs for all Dash callbacks
        :returns: Initialized outputs for all callbacks
        """
        self.outputs_data = [
            Output(component_id="input_data_storage", component_property="children"),
            Output(component_id="simulation_basis_info_id", component_property="children"),
        ]

        self.outputs_callback_part_id = Output(component_id="part_dropdown", component_property="options")

        self.outputs_callback_discount_dropdown = Output(component_id="discount_group_dropdown", component_property="options")

        self.outputs_callback_left_nav = [
            Output(component_id="part_id", component_property="children"),
            Output(component_id="part_desc_id", component_property="children"),
            Output(component_id="mc_desc_id", component_property="children"),
            Output(component_id="mc_id_id", component_property="children"),
            Output(component_id="rg_id_fixed", component_property="children"),
            Output(component_id="rg_id_fixed_desc", component_property="children"),
            Output(component_id="volume_id", component_property="children"),
            Output(component_id="mra_nr_id", component_property="children"),
            Output(component_id="kpi_llp_wo_cv_id", component_property="children"),
            Output(component_id="kpi_nlp_wo_cv_id", component_property="children"),
            Output(component_id="kpi_llp_cv_id", component_property="children"),
            Output(component_id="kpi_nlp_cv_id", component_property="children"),
            Output(component_id="kpi_cost_var_id", component_property="children"),
            Output(component_id="kpi_cost_proc_id", component_property="children"),
            Output(component_id="mra_cm_id", component_property="children"),
            Output(component_id="kpi_discount_rate_id", component_property="children"),
            Output(component_id="discount_group_dropdown", component_property="value"),
            Output(component_id="kpi_wg_share_id", component_property="children"),
            Output(component_id="kpi_elasticity_cat_id", component_property="children"),
            Output(component_id="kpi_discount_group_id", component_property="children"),
            Output(component_id="nr_development_id", component_property="children"),
            Output(component_id="cm_development_id", component_property="children"),
            Output(component_id="vol_prev_development_id", component_property="children"),
            Output(component_id="mra_nr_prev_development_id", component_property="children"),
            Output(component_id="mra_cm_prev_development_id", component_property="children"),
            Output(component_id="cm_mc_factor", component_property="children"),
            # Output(component_id="cm_sticker", component_property="children"),
            # Output(component_id="cm_pci", component_property="children"),
        ]

        self.outputs_sim_data = Output(component_id="simulation_data_storage", component_property="children")

        self.outputs_sim_cm = [
            Output(component_id="sim_new_llp_id", component_property="children"),
            Output(component_id="sim_new_nlp_id", component_property="children"),
            Output(component_id="sim_new_abs_pep_cm_id", component_property="children"),
            Output(component_id="sim_new_rel_pep_cm_id", component_property="children"),
            Output(component_id="sim_new_discount_id", component_property="children"),
            Output(component_id="sim_llp_id", component_property="children"),
            Output(component_id="sim_nlp_id", component_property="children"),
            Output(component_id="sim_abs_pep_cm_id", component_property="children"),
            Output(component_id="sim_rel_pep_cm_id", component_property="children"),
            Output(component_id="sim_discount_id", component_property="children"),
            Output(component_id="sim_cv_net_actual_id", component_property="children"),
            Output(component_id="sim_cv_net_new_id", component_property="children"),
            Output(component_id="sim_cv_gross_actual_id", component_property="children"),
            Output(component_id="sim_cv_gross_new_id", component_property="children"),
            Output(component_id="sim_llp_cv_id", component_property="children"),
            Output(component_id="sim_nlp_cv_id", component_property="children"),
            Output(component_id="sim_new_llp_cv_id", component_property="children"),
            Output(component_id="sim_new_nlp_cv_id", component_property="children"),
        ]

        self.outputs_sim_waterfall = Output(component_id="simulation_waterfall", component_property="figure")

        self.outputs_disable_breakeven = [
            Output(component_id="volume_change_perc", component_property="disabled"),
            Output(component_id="volume_change_perc", component_property="value"),
        ]

        # self.outputs_sim_breakeven = (
        #     [Output(component_id="line_graph_breakdown", component_property="figure")]
        #     + [Output(component_id="volume_change_break_even", component_property="children")]
        #     + [Output(component_id="abs_volume_change_break_even", component_property="children")]
        #     + [Output(component_id="cm_change_break_even", component_property="children")]
        # )

        self.outputs_sim_breakeven = [
                Output(component_id="line_graph_breakdown", component_property="figure"),
                Output(component_id="volume_change_break_even", component_property="children"),
                Output(component_id="abs_volume_change_break_even", component_property="children"),
                Output(component_id="cm_change_break_even", component_property="children")
        ]

        self.outputs_kpi_view = Output(component_id="kpi_view", component_property="figure")

        self.outputs_disable_inputs = [
            Output(component_id="simulated_cm_component", component_property="is_open"),
            Output(component_id="part_pricing_card", component_property="is_open"),
            Output(component_id="mc_pricing_card", component_property="is_open"),
            Output(component_id="discount_group_dropdown", component_property="disabled"),
            Output(component_id="discount_group_component", component_property="is_open"),
            Output(component_id="abs_rel_radio_buttons", component_property="value"),
            Output(component_id="abs_rel_component", component_property="is_open"),
            Output(component_id="part_id_info", component_property="hidden"),
            Output(component_id="part_desc_info", component_property="hidden"),
            Output(component_id="ms_id_info", component_property="hidden"),
            Output(component_id="Pricing", component_property="hidden"),
            Output(component_id="mc_id_id_info", component_property="hidden"),
            Output(component_id="mc_desc_id_info", component_property="hidden"),
            Output(component_id="rg_id_fixed_info", component_property="hidden"),
            Output(component_id="rg_id_fixed_desc_info", component_property="hidden"),
            # CM Table hid
            Output(component_id="brid", component_property="hidden"),
            Output(component_id="Break_Even_Ratios", component_property="hidden"),
            Output(component_id="Value_Info", component_property="hidden"),
            Output(component_id="Relative_volume_change_to_break_even", component_property="hidden"),
            Output(component_id="volume_change_break_even", component_property="hidden"),
            Output(component_id="Absolute_volume_change_to_break_even", component_property="hidden"),
            Output(component_id="abs_volume_change_break_even", component_property="hidden"),
            Output(component_id="CM_change_if_constant_volume", component_property="hidden"),
            Output(component_id="cm_change_break_even", component_property="hidden"),
            # MC View
            # Output(component_id="mc_view_info", component_property="hidden"),
        ]

        self.outputs_abs_rel_buttons = [
            Output(component_id="title_price_input", component_property="children"),
            Output(component_id="title_volume_input", component_property="children"),
        ]

        self.outputs_sim_table = []
        for kpi in config.app.KPI_TABLE:
            self.outputs_sim_table.append(Output(component_id=kpi + "_sim", component_property="children"))
            self.outputs_sim_table.append(Output(component_id=kpi + "_delta", component_property="children"))
            self.outputs_sim_table.append(Output(component_id=kpi + "_delta_rel", component_property="children"))

    def create_callbacks(self):
        """
        Define all callback functions (equivalent to the Dash callback decorators).
        :returns: Initialized callback functions
        """

        self.app.callback(self.outputs_callback_part_id, self.inputs_callback_part_id,)(
            self.callback_part_ids
        )

        self.app.callback(
            self.outputs_callback_discount_dropdown,
            self.inputs_callback_discount_dropdown,
            prevent_initial_call=True,
        )(self.callback_discount_dropdown)

        self.app.callback(
            self.outputs_data, self.inputs_data, prevent_initial_call=True
        )(self.callback_load_data)

        self.app.callback(
            self.outputs_callback_left_nav,
            self.inputs_callback_left_nav,
            # prevent_initial_call=True,
        )(self.callback_left_nav)

        self.app.callback(
            self.outputs_sim_data, self.inputs_sim_data, prevent_initial_call=True
        )(self.callback_simulation_data)

        self.app.callback(
            self.outputs_sim_cm, self.inputs_sim, prevent_initial_call=True
        )(self.callback_cm_component)

        self.app.callback(
            self.outputs_sim_waterfall, self.inputs_sim, prevent_initial_call=True,
        )(self.callback_waterfall)

        self.app.callback(
            self.outputs_disable_breakeven,
            self.inputs_disable_breakeven,
            self.states_disable_breakeven,
            prevent_initial_call=True,
        )(self.callback_disable_breakeven)

        self.app.callback(
            self.outputs_sim_breakeven, self.inputs_sim, prevent_initial_call=True,
        )(self.callback_breakeven)

        self.app.callback(
            self.outputs_kpi_view, self.inputs_kpi_view, prevent_initial_call=True
        )(self.callback_kpi_view)

        self.app.callback(
            self.outputs_disable_inputs,
            self.inputs_disable_inputs,
            self.states_disable_inputs,
            prevent_initial_call=True,
        )(self.callback_disable_inputs)

        self.app.callback(
            self.outputs_sim_table, self.inputs_sim_table, prevent_initial_call=True
        )(self.callback_sim_table)

        self.app.callback(
            self.outputs_abs_rel_buttons,
            self.inputs_abs_rel_buttons,
            prevent_initial_call=True,
        )(self.callback_abs_rel_buttons)