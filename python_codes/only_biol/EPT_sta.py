# Get a df that contains only stations related to EPT

import pandas as pd
import numpy as np


# EPT codes in order E, P, T
EPT_codes_sorted = [[390, 394, 421, 491, 387, 384, 358, 452, 473, 366, 439, 468, 3207, 459, 31679, 506, 502, 461, 391, 457, 503, 370, 357, 448, 32271, 32269, 30823, 404, 509, 481, 31231, 496, 478, 348, 2391, 501, 383, 449, 467, 380, 450, 5110, 399, 497, 456, 393, 474, 3181, 476, 510, 368, 388, 5152, 400, 25676, 443, 420, 29153, 9794, 494, 5151, 376, 389, 364, 350, 3198, 463, 32270, 377, 363, 485, 451]
, [68, 116, 156, 140, 70, 118, 17, 33830, 13, 132, 66, 21, 3, 67, 168, 117, 121, 14, 152, 12, 44, 4, 10, 20, 172, 164, 163, 1, 133, 165, 19, 174, 46, 85, 2, 155, 131, 150, 178, 169, 126, 159, 161, 69, 170, 173, 127, 16, 26]
, [5219, 254, 324, 292, 305, 199, 3120, 5144, 3194, 288, 194, 333, 224, 24007, 329, 3190, 313, 306, 249, 321, 198, 274, 206, 232, 263, 193, 212, 211, 262, 340, 202, 318, 295, 265, 5218, 328, 3121, 2351, 280, 2335, 319, 3163, 291, 322, 228, 2307, 251, 345, 287, 248, 3186, 238, 5237, 197, 276, 320, 236, 282, 2279, 191, 235, 182, 260, 252, 20556, 266, 185, 209, 311, 309, 207, 286, 289, 338, 268, 221, 3214, 240, 200, 346, 339, 308, 326, 220, 183, 312, 31750, 244, 246, 325, 299, 2361, 3203, 195, 307, 181, 210, 237, 24008, 317, 184, 5147, 25058, 315, 227, 5085, 3162, 255, 298, 2379, 2328, 344, 304, 281, 208, 233, 5148, 5140, 201, 245, 2324, 203, 218, 3146, 190, 264, 9812, 323, 223, 2346, 250, 241, 192, 231, 2347, 222, 314, 239, 327, 189, 310, 31677]
]


def determine_type(code):
    """determine type of species according to taxon code"""
    if code in EPT_codes_sorted[0]:
        return "E"
    elif code in EPT_codes_sorted[1]:
        return "P"
    else:
        return "T"
    

def add_HS(left_df, right_df, left_id:str, right_id:str):
    """ add HS column """

    # converting both to str so its the same type
    left_df[left_id] = left_df[left_id].astype(str)
    right_df[right_id] = right_df[right_id].astype(str)
    # merging
    left_df = pd.merge(left_df, right_df[right_df[right_id].isin(left_df[left_id])][[right_id, 'ORD_STRA']], left_on=left_id, right_on = right_id, how='left')
    # rearranging col
    left_df = left_df.drop(right_id, axis=1)
    left_df.insert(1, 'ORD_STRA', left_df.pop('ORD_STRA'))

    return left_df


def only_taxons(tax_df, meta_df):
    """ process taxons to only keep stations that measured EPT """

    # get only stations with EPT
    # flatten EPT list of codes
    flattened_EPT_codes = [code for sublist in EPT_codes_sorted for code in sublist]
    # parsing taxons that contain EPT
    tax_df = tax_df[tax_df['code_appel_taxon'].isin(flattened_EPT_codes)]

    # if same station, same date and some code, keep only one
    tax_df = tax_df.drop_duplicates(subset=["code_station_hydrobio", "date_prelevement", "code_appel_taxon"])
    # Apply the function to create the type_EPT column
    tax_df['type_EPT'] = tax_df['code_appel_taxon'].apply(determine_type)
    # Group by the subset of columns and aggregate code_appel_taxon into a list
    
    tax_df = tax_df[["code_station_hydrobio", "date_prelevement", "code_appel_taxon", "type_EPT", "coordonnee_x", "coordonnee_y"]].reset_index(drop=True)

    # add HS in a new col
    tax_df = add_HS(tax_df, meta_df, "code_station_hydrobio", "station_ID")

    return tax_df
