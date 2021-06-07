from src.simulation.helper import *

import math


class Calculations:
    """
    Holds all calculations that are used for the simulation
    """

    def __init__(self, pep_dealer_discount):
        self.pep_dealer_discount = pep_dealer_discount

    def get_sim_data(
            self,
            df,
            price_change_perc,
            volume_change_perc,
            nlp_llp,
            discount_group,
            current_market,
            cost_var, ):
        """
        Does the KPI calculation for all simulated values (price / volume change)
        as well as the elasticity
        Args:
            df: dataframe with the data filtered by the current user dropdown selection
                - This df has 1 row in part id mode in all other modes it can have more!!
            price_change_perc: the relative price change (for both absolute and relative mode)
            volume_change_perc: the relative volume change (for both absolute and relative mode)
            nlp_llp: a flag is the app is in NLP or LLP mode
            discount_group: the current selected discount group
            current_market: the current selected market to get the discount rate with
                               the discount group
        Returns: dictionary with KPIs
        """

        # columns with actual values before the simulation
        pep_nlp = df[NLP_KEY]  # NLP prices
        pep_nlp = pep_nlp.sum()
        pep_llp = df[LLP_KEY]  # LLP prices
        pep_llp = pep_llp.sum()

        discount_rate_actual = df[MARKET_DISCOUNT_RATE_KEY]  # actual discount rate
        cv_net_actual = df[CV_NET_KEY]  # core value net
        cv_gross_actual = df[CV_GROSS_KEY]  # core value gross
        volume_cp_actual = df[VOL_KEY]  # sales volume last 12 month
        mra_nr_actual = df[MRA_NR_KEY]  # net revenue last 12 months
        mra_cm_actual = df[MRA_CM_KEY]  # contribution margin last 12 months
        # PEP contribution margin per unit
        pep_cm_unit_actual = df[NLP_KEY] - df[VARIABLE_COST_KEY] - df[PROCUREMENT_COST_KEY]
        # elasticity column
        elasticity = df[ELASTICITY_KEY]
        # cost per unit
        pep_cost_unit = df[VARIABLE_COST_KEY] + df[PROCUREMENT_COST_KEY]

        # get discount rate by the discount group selected by the user
        # print('discount_group: ', discount_group, ' -- ', repr(discount_group), ' -- ', type(discount_group))
        # print('market: ', current_market)
        discount_group_filter = '00' if discount_group == '0' else discount_group
        # print('*** discount_group_filter: ', discount_group_filter)

        if discount_group is not None:
            discount_rate = (
                    self.pep_dealer_discount[
                        (self.pep_dealer_discount["discount_group"] == discount_group_filter)
                        & (self.pep_dealer_discount["market"] == current_market)
                        ]["discount_rate"].iloc[0]
                    / 100
            )
        else:
            discount_rate = discount_rate_actual

        # new simulated CV values based on the price change
        cv_net_new = cv_net_actual * (1 + price_change_perc)
        cv_gross_new = cv_gross_actual * (1 + price_change_perc)

        # handling the case when nlp_llp is not set (nlp mode is the standard)
        if nlp_llp is None:
            nlp_llp = "nlp_mode"

        # NLP and LLP mode handling
        if nlp_llp == "nlp_mode":
            new_pep_nlp = pep_nlp * (1 + price_change_perc)
            new_pep_llp = (new_pep_nlp + cv_net_new) / (1 - discount_rate) - cv_gross_new

            # the rest of the formulas are independent of NLP/LLP. we just need the
            # nlp relative price change (nlp_change_perc)
            nlp_change_perc = price_change_perc

        # LLP mode
        elif nlp_llp == "llp_mode":
            new_pep_llp = pep_llp * (1 + price_change_perc)
            new_pep_nlp = (new_pep_llp + cv_gross_new) * (1 - discount_rate) - cv_net_new

            # in the source the NLP is cut to two digits we apply the same here
            new_pep_nlp = math.floor(new_pep_nlp * 10 ** 2) / 10 ** 2

            # the rest of the formulas are independent of NLP/LLP. we just need the
            # nlp relative price change (nlp_change_perc)
            nlp_change_perc = new_pep_nlp / pep_nlp - 1

        # workaround to handle actual volumes of zero. In this case there is no relative change
        # possible. In this case we assume the new entered absolute volume as the new volume
        if volume_cp_actual.sum() == 0:
            new_volume_cp = volume_change_perc
        else:
            # new_volume_cp = volume_cp_actual * (1 + volume_change_perc)
            new_volume_cp = volume_cp_actual.sum() * (1 + volume_change_perc)

        # delta prices from actual to simulated
        delta_price = new_pep_nlp - pep_nlp
        delta_volume = new_volume_cp - volume_cp_actual

        # calculate PEP CM
        pep_cm_unit_sim = new_pep_nlp - pep_cost_unit

        # simulated NR values
        nr_cp_baseline = mra_nr_actual
        nr_cp_delta_price = nr_cp_baseline + volume_cp_actual * delta_price
        nr_cp_delta_price_delta_volume = (
                nr_cp_baseline + delta_volume * new_pep_nlp + volume_cp_actual * delta_price
        )

        # simulated CM values
        cm_cp_baseline = mra_cm_actual
        cm_cp_delta_price = cm_cp_baseline + volume_cp_actual * delta_price
        cm_cp_delta_price_delta_volume = (
                cm_cp_baseline + delta_volume * (new_pep_nlp - pep_cost_unit) + volume_cp_actual * delta_price
        )
        sim_delta_cm = cm_cp_delta_price_delta_volume - cm_cp_baseline

        # actual PEP CM relative values
        pep_cm_actual_relative = (
            (pep_cm_unit_actual.sum() / (pep_cm_unit_actual + pep_cost_unit).sum())
            if ((pep_cm_unit_actual + pep_cost_unit).sum() != 0)
            else 0.0
        )
        # simulated PEP CM relative values
        pep_cm_sim_relative = (
            (pep_cm_unit_sim.sum() / (pep_cm_unit_sim + pep_cost_unit).sum())
            if ((pep_cm_unit_sim + pep_cost_unit).sum() != 0)
            else 0.0
        )

        # simulated elasticity KPIs
        if df.shape[0] == 1:
            # without error
            elasticity_vol_relative = nlp_change_perc * elasticity
            elasticity_vol_new = volume_cp_actual * (1 + elasticity_vol_relative)

            elasticity_delta_volume = elasticity_vol_new - volume_cp_actual
            elasticity_nr_new = (
                    nr_cp_baseline
                    + elasticity_delta_volume * new_pep_nlp
                    + volume_cp_actual * delta_price
            )

            elasticity_cm_new = (
                    cm_cp_baseline
                    + elasticity_delta_volume * new_pep_nlp
                    + volume_cp_actual * delta_price
            )

            # with error
            elasticity_error = df[ELASTICITY_ERROR_KEY]

            elasticity_vol_relative_err = nlp_change_perc * (
                    elasticity + elasticity_error * 2
            )
            elasticity_vol_new_err = volume_cp_actual * (
                    1 + elasticity_vol_relative_err
            )

            elasticity_delta_volume_err = elasticity_vol_new_err - volume_cp_actual
            elasticity_nr_new_err = (
                    nr_cp_baseline
                    + elasticity_delta_volume_err * new_pep_nlp
                    + volume_cp_actual * delta_price
            )

            elasticity_cm_new_err = (
                    cm_cp_baseline
                    + elasticity_delta_volume_err * new_pep_nlp
                    + volume_cp_actual * delta_price
            )

            elasticity_nr_err_abs = elasticity_nr_new_err - elasticity_nr_new
            elasticity_cm_err_abs = elasticity_cm_new_err - elasticity_cm_new

        else:
            elasticity_vol_new = 0
            elasticity_nr_new = 0
            elasticity_cm_new = 0
            elasticity_nr_err_abs = 0
            elasticity_cm_err_abs = 0

        
        # additional break even KPIs
        margin = pep_nlp -  cost_var

        total_cm = margin * new_volume_cp

        new_nlp = pep_nlp * (1 + price_change_perc)

        new_margin = (new_nlp - cost_var) * new_volume_cp

        if total_cm == 0 and new_margin == 0:
            break_even = 0
        elif new_margin == 0:
            break_even = 0
        else:
            break_even = (total_cm / new_margin) - 1

        perc_vol_change_break_even = break_even

        abs_vol_change_break_even = (
                volume_cp_actual.sum() * perc_vol_change_break_even / 100
        )

        perc_vol_change_break_even = str(perc_vol_change_break_even)[:4]

        # pep_cm_unit_actual
        # print('pep_cm_unit_actual: ', pep_cm_unit_actual, ' --- ', type(pep_cm_unit_actual))
        # pre, post = str(pep_cm_unit_actual.sum()).split('.')
        # pre = pre.replace(',', '.')
        # pep_cm_unit_actual = pre + ',' + post
        # print('pep_cm_unit_actual: ', pep_cm_unit_actual, ' --- ', type(pep_cm_unit_actual))

        # pep_cm_actual_relative
        # print('pep_cm_actual_relative: ', pep_cm_actual_relative, ' --- ', type(pep_cm_actual_relative))
        # pre, post = str(pep_cm_actual_relative.sum()).split('.')
        # pre = pre.replace(',', '.')
        # pep_cm_actual_relative = pre + ',' + post
        # print('pep_cm_actual_relative: ', pep_cm_actual_relative, ' --- ', type(pep_cm_actual_relative))

        output_dict = {
            "mra_nr_actual": mra_nr_actual,
            "nr_cp_delta_price": nr_cp_delta_price,
            "nr_cp_delta_price_delta_volume": nr_cp_delta_price_delta_volume,
            "mra_cm_actual": mra_cm_actual,
            "cm_cp_delta_price": cm_cp_delta_price,
            "cm_cp_delta_price_delta_volume": cm_cp_delta_price_delta_volume,
            "volume_cp_actual": volume_cp_actual,
            "new_volume_cp": new_volume_cp,
            "sim_delta_cm": sim_delta_cm,
            "perc_vol_change_break_even": perc_vol_change_break_even,
            "abs_vol_change_break_even": abs_vol_change_break_even,
            "sim_nlp": new_pep_nlp,
            "sim_llp": new_pep_llp,
            "elasticity_nr_new": elasticity_nr_new,
            "elasticity_cm_new": elasticity_cm_new,
            "elasticity_vol_new": elasticity_vol_new,
            "pep_cm_unit_sim": pep_cm_unit_sim,
            "pep_cm_sim_relative": pep_cm_sim_relative,
            "discount_rate": discount_rate,
            "cur_sign": df.iloc[0]["currency"],
            "nlp_actual": pep_nlp,
            "llp_actual": pep_llp,
            "pep_cm_unit_actual": pep_cm_unit_actual,
            "pep_cm_actual_relative": pep_cm_actual_relative,
            "discount_rate_actual": discount_rate_actual,
            "elasticity_nr_err_abs": elasticity_nr_err_abs,
            "elasticity_cm_err_abs": elasticity_cm_err_abs,
            "cv_net_actual": cv_net_actual,
            "cv_gross_actual": cv_gross_actual,
            "cv_net_new": cv_net_new,
            "cv_gross_new": cv_gross_new,
        }

        return output_dict

    def historic_data(self, df=None, init=False):
        if init:
            return 4 * [0], 4 * [0], 4 * [0]
        vol = [df[historic_vol].sum() for historic_vol in HISTORIC_VOL]
        nr = [df[historic_nr].sum() for historic_nr in HISTORIC_NR]
        cm = [df[historic_cm].sum() for historic_cm in HISTORIC_CM]

        return nr, cm, vol