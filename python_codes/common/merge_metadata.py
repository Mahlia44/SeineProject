# Get a df that contains only stations related to EPT

import pandas as pd
import numpy as np
import os

# Get the current directory of the notebook
current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))

# Import biological stations
biol_file = os.path.join(parent_dir, "biol_data", "stations", "metadata_biolstat.xlsx")
biol_df = pd.read_excel(biol_file, sheet_name=1)

# Import phychem stations
phychem_file = os.path.join(parent_dir, "phychem_data", "stations", "metadata_phychemstat.xlsx")
phychem_df = pd.read_excel(biol_file, sheet_name=1)


def add_HS(type, left_df, left_id:str, right_id="station_ID"):
    """ add HS column """

    if type=="Biological":
        right_df = biol_df
    else:
        right_df = phychem_df

    # converting both to str so its the same type
    left_df[left_id] = left_df[left_id].astype(str)
    right_df[right_id] = right_df[right_id].astype(str)
    # merging
    left_df = pd.merge(left_df, right_df[right_df[right_id].isin(left_df[left_id])][[right_id, 'ORD_STRA']], left_on=left_id, right_on = right_id, how='left')
    # rearranging col
    # left_df = left_df.drop(right_id, axis=1)
    left_df.insert(1, 'ORD_STRA', left_df.pop('ORD_STRA'))

    return left_df


def add_coord(type, left_df, left_id, right_id="station_ID"):
    """ add coord columns """

    if type=="Biological":
        right_df = biol_df
    else:
        right_df = phychem_df

    # converting both to str so its the same type
    left_df[left_id] = left_df[left_id].astype(str)
    right_df[right_id] = right_df[right_id].astype(str)
    # merging
    left_df = pd.merge(left_df, right_df[right_df[right_id].isin(left_df[left_id])][[right_id, 'coordonnee_x', 'coordonnee_y']], left_on=left_id, right_on = right_id, how='left')
    # rearranging col
    left_df = left_df.drop(right_id, axis=1)

    return left_df