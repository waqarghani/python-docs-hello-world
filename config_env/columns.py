"""This module contains the name columns in the cubes test."""

from src.utils.config import config

# current/last years
CURRENT_YEAR = config['year']
CURRENT_YEAR_TEXT = 'current_year'
LAST_PEP_YEAR = max(config['data_years']['pep'])
LAST_FULL_YEAR_MRA_LOGISTIC = config['data_years']['mra_logistic_last_full_year']
LAST_PRESTO_MASTER_FINAL_RUN_YEAR = max(config['data_years']['presto_final_run'])
LAST_MRA_RETAIL_YEAR = config['data_years']['mra_retail_last_full_year']

# global nlp amount in the last year:
GLOBAL_NET_AMOUNT_KEY = "mat_global_net_amount"
GLOBAL_QUANTITY_KEY = f"mat_cp_global_quantity"
FINAL_RUN_GLOBAL_QUANTITY = f"{LAST_PRESTO_MASTER_FINAL_RUN_YEAR}_final_run_global_quantity"

# market
MARKET_QUANTITY_KEY = "mat_market_quantity"
MARKET_NET_AMOUNT_KEY = 'mat_market_net_amount'
MARKET_CM_KEY = f'mat_market_daimler_cm_amount'
MARKET_CM_CP_KEY = f'mat_market_cp_cm_amount'
MARKET_CM_PER_UNIT_KEY = f'mat_market_cp_cm_per_unit'
MARKET_CM_PERC_KEY = 'mat_market_cm_perc'
MARKET_LAST_FULL_YEAR_CP_CM_PER_UNIT_KEY = f"{LAST_FULL_YEAR_MRA_LOGISTIC}_market_cp_cm_per_unit"

# current
# the fields with {CURRENT_YEAR_TEXT} can be used as columns in the Tableau dashboard as the name
# of the columns does not encode the current year
DEALER_AVG_CM_PRICE_KEY = 'dealer_avg_cm_price'
AVG_SELL_IN_PRICE_KEY = f"{LAST_FULL_YEAR_MRA_LOGISTIC}_avg_sell_in_price"
AVG_SELL_OUT_PRICE_KEY = f"{LAST_MRA_RETAIL_YEAR}_avg_sell_out_price"
OTC_SHARE_KEY = f"{LAST_MRA_RETAIL_YEAR}_market_otc_share"

# pricing LAST YEAR
LAST_YEAR_GLP_KEY = f"{LAST_PEP_YEAR}_glp_price"
GLP_KEY = f"{CURRENT_YEAR_TEXT}_glp_price"

LAST_YEAR_NLP_KEY = f"{LAST_PEP_YEAR}_nlp_price"
NLP_KEY = f"{CURRENT_YEAR_TEXT}_nlp_price"

LAST_YEAR_PEP_CM_PER_UNIT_KEY = f"{LAST_PEP_YEAR}_pep_cm_per_unit"
PEP_CM_PER_UNIT_KEY = f"{CURRENT_YEAR_TEXT}_pep_cm_per_unit"

LAST_YEAR_PEP_CM_PER_UNIT_PERC_KEY = f"{LAST_PEP_YEAR}_pep_cm_per_unit_perc"
PEP_CM_PER_UNIT_PERC_KEY = f"{CURRENT_YEAR_TEXT}_pep_cm_per_unit_perc"

# LAST_FULL_YEAR_CM_PER_UNIT_PERC_KEY = f"{LAST_FULL_YEAR_MRA_LOGISTIC}_cm_per_unit_perc"
LAST_FULL_YEAR_CM_PER_UNIT_PERC_KEY = f"{LAST_FULL_YEAR_MRA_LOGISTIC}_market_cm_perc"
LLP_KEY = f"{LAST_PEP_YEAR}_llp_price"
VARIABLE_COST_KEY = f"{LAST_PEP_YEAR}_variable_cost_price"
PROCUREMENT_COST_KEY = f"{LAST_PEP_YEAR}_procurement_cost_price"
MARKET_FACTOR_KEY = f'market_factor_standard'
DG_KEY = f'{LAST_PEP_YEAR}_market_discount_group_id'
DR_KEY = f'{LAST_PEP_YEAR}_market_discount_rate'
DE_DG_KEY = f'{LAST_PEP_YEAR}_de_discount_group_id'
STICKER_PRICE_FLAG_KEY = f"{LAST_PEP_YEAR}_sticker_price_flag"
PCI_FLAG_KEY = f'{LAST_PEP_YEAR}_pci_flag'

# hierarchy
COMPETITIVE_FLAG_KEY = f"competitive_flag"  # in presto, no year used there

# market SC share
SC_SHARE_KEY = f"{CURRENT_YEAR}_market_sc_share"
