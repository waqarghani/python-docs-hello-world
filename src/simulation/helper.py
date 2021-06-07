from typing import List, Dict
import pandas as pd
import numpy as np
from datetime import datetime

from src.utils.config import config

CURRENT_YEAR = str(config.year)

CV_NET_KEY = config.app.CV_NET_KEY
CV_GROSS_KEY = config.app.CV_GROSS_KEY
VARIABLE_COST_KEY = CURRENT_YEAR + config.app.VARIABLE_COST_KEY
PROCUREMENT_COST_KEY = CURRENT_YEAR + config.app.PROCUREMENT_COST_KEY

MC_ID = config.app.MC_ID
MC_DESC = config.app.MC_DESC
PART_ID = config.app.PART_ID
PART_DESC = config.app.PART_DESC
MARKET_ID = config.app.MARKET_ID
years = [int(CURRENT_YEAR) - i for i in range(config.app.years, -1, -1)]
HISTORIC_VOL = [str(year) + config.app.VOL_KEY for year in years]
HISTORIC_NR = [str(year) + config.app.MRA_NR_KEY for year in years]
HISTORIC_CM = [str(year) + config.app.MRA_CM_KEY for year in years]

# RG_KEY = config.app.RG_KEY
RG_ID_FIXED = config.app.RG_ID_FIXED
RG_ID_FIXED_DESC = config.app.RG_ID_FIXED_DESC
RG_M_KEY = config.app.RG_M_KEY
RG_S_KEY = config.app.RG_S_KEY

# STICKER_PRICE_FLAG_KEY = CURRENT_YEAR + "_sticker_price_flag"
NLP_KEY = config.app.NLP_KEY
LLP_KEY = config.app.LLP_KEY
MARKET_DISCOUNT_RATE_KEY = config.app.MARKET_DISCOUNT_RATE_KEY
MARKET_DISCOUNT_GROUP_KEY = config.app.MARKET_DISCOUNT_GROUP_KEY

ELASTICITY_KEY = "elasticity"
ELASTICITY_CAT_KEY = "ela_category"
ELASTICITY_ERROR_KEY = "elasticity_std"
WG_SHARE_KEY = CURRENT_YEAR + config.app.WG_SHARE_KEY


# Variable names for calculated variables
PEP_CM_KEY = "pep_cm_CALC"
PEP_NR_KEY = CURRENT_YEAR + "_pep_cp_net_amount_CALC"

MRA_CM_KEY = "mra_cm_CALC"
MRA_CM_KEY_PREVIOUS = "mra_cm_CALC" + config.app.PREVIOUS_SUFFIX
MRA_NR_KEY = "mra_nr_CALC" + config.app.MRA_MONTHLY_NR_LOCAL_KEY
MRA_NR_KEY_PREVIOUS = "mra_nr_CALC" + config.app.PREVIOUS_SUFFIX

VOL_KEY = config.app.MRA_MONTHLY_VOL_KEY
VOL_KEY_PREVIOUS = config.app.MRA_MONTHLY_VOL_KEY + config.app.PREVIOUS_SUFFIX

currency_columns = set(
    [NLP_KEY, CV_NET_KEY, CV_GROSS_KEY, LLP_KEY, VARIABLE_COST_KEY, PROCUREMENT_COST_KEY,]
    + HISTORIC_NR
    + HISTORIC_CM
)

cols = set(
    [
        MC_ID,
        MC_DESC,
        PART_ID,
        PART_DESC,
        MARKET_ID,
        NLP_KEY,
        LLP_KEY,
        CV_NET_KEY,
        CV_GROSS_KEY,
        VARIABLE_COST_KEY,
        PROCUREMENT_COST_KEY,
        # RG_KEY,
        RG_ID_FIXED,
        RG_ID_FIXED_DESC,
        MARKET_DISCOUNT_RATE_KEY,
        WG_SHARE_KEY,
        MARKET_DISCOUNT_GROUP_KEY,
        RG_M_KEY,
        RG_S_KEY,
    ]
    + HISTORIC_VOL
    + HISTORIC_NR
    + HISTORIC_CM
)

mra_key_columns = ["part_id", "mc_id", "rg_id_fixed", "rg_m_id", "rg_s_id"]

mra_columns = [
    config.app.MRA_MONTHLY_VOL_KEY,
    config.app.MRA_MONTHLY_CM_KEY,
    config.app.MRA_MONTHLY_NR_KEY,
    config.app.MRA_MONTHLY_WG_NR_KEY,
    config.app.MRA_MONTHLY_CM_LOCAL_KEY,
    config.app.MRA_MONTHLY_NR_LOCAL_KEY,
    config.app.MRA_MONTHLY_WG_NR_LOCAL_KEY,
]

# helper function to create a list of TNRs for the part dropdown
def get_options_from_list(level_ids: List[str]) -> List[Dict[str, str]]:
    """Convert a list of string into a list of options."""
    return [{"label": level_id, "value": level_id} for level_id in level_ids]


# helper function to create a list of TNRs for the part dropdown
def get_discount_options(discounts: pd.DataFrame) -> List[Dict[str, str]]:
    """Convert the discount df of discount groups and rates into a list of options."""
    return [
        {
            "label": row.discount_group + " (" + f"{row.discount_rate:,.{config.app.decimals}f} %" + ")",
            "value": row.discount_group,
        }
        for _, row in discounts.iterrows()
    ]


def get_table_kpis(output_list, actual, simulated, unit=""):
    # simulated:
    # output_list += [f"{simulated:,.{config.app.decimals}f} " + unit]
    sim = f"{simulated:,.{config.app.decimals}f} "
    pre, post = sim.split('.')
    pre = pre.replace(',', '.')
    sim = pre + ',' + post + unit
    output_list += [sim]

    # delta:
    simulated_delta = simulated - actual
    # output_list += [f"{simulated_delta:,.{config.app.decimals}f} " + unit]

    # relative:
    delta_rel = round((simulated_delta / actual) * 100, 2) if (actual != 0) else 0.0
    pre, post = str(delta_rel).split('.')
    pre = pre.replace(',', '.')
    delta_rel = pre + ',' + post + ' ' + unit
    output_list += [delta_rel]

    # output_list += [f"{delta_rel:,.{config.app.decimals}f} @@"]
    # output_list += [f"{delta_rel:,.{config.app.decimals}f} " + '']

    simulated_delta = f"{simulated_delta:,.{config.app.decimals}f} "
    pre, post = simulated_delta.split('.')
    pre = pre.replace(',', '.')
    simulated_delta = pre + ',' + post + '%'
    output_list += [simulated_delta]

    return output_list


def get_12_months_rolling(mra_monthly_last_month):

    last_12_months = pd.date_range(
        #Don't remove 129 line
        # end=datetime.strptime(mra_monthly_last_month, "%Y%m"),
        end=datetime.strptime(mra_monthly_last_month, "%Y%m") - pd.DateOffset(months=1),
        periods=12,
        freq=pd.offsets.MonthBegin(1),
    )
    previous_12_months = pd.date_range(
        end=last_12_months[0] - pd.DateOffset(months=1),
        periods=12,
        freq=pd.offsets.MonthBegin(1),
    )

    return (
        list(last_12_months.strftime("%Y%m")),
        list(previous_12_months.strftime("%Y%m")),
    )


def aggregate_12_months(mra_monthly_data, months_list):
    months_df = mra_monthly_data[mra_monthly_data["month"].isin(months_list)].drop(
        columns="month"
    )

    return months_df.groupby(mra_key_columns, as_index=False).sum()

def fix_dtypes_for_json(output_dict):
    for value in output_dict:
        if type(output_dict[value]) == int:
            output_dict[value] = float(output_dict[value])
        elif (
                type(output_dict[value]) == np.float64
                or type(output_dict[value]) == float
                or type(output_dict[value]) == str
        ):
            pass
        elif output_dict[value] is None:
            output_dict[value] = 'null'
        else:
            output_dict[value] = float(output_dict[value].sum())

    return output_dict
