import pandas as pd
import numpy as np
import geopandas as gpd

#--------------------------------------------------------------

file_path = '/Users/paulmazas/Desktop/SNU/LAB/Landscape/Landscape_Subc_Table.csv'
# Read the CSV file into a geopanda DataFrame
df = gpd.read_file(file_path)

#--------------------------------------------------------------

file_population_path = '/Users/paulmazas/Desktop/SNU/LAB/Population/population_subc_table.csv'
# Read the CSV file into a geopanda DataFrame
pop_df = gpd.read_file(file_population_path)

#--------------------------------------------------------------

def landscape_population_subc(df, pop_df):

    # Obtain the number of rows in the DataFrame
    size = df['Area_Ratio'].size
    # List all the values of the 'OBJECTID' column
    hybas_ids = df['_HYBAS_ID'].unique()
    # List all the values of the 'type' column
    types = df['type'].unique()
    # Convert 'Area_Ratio' column to float
    df['Area_Ratio'] = df['Area_Ratio'].astype(float)

    # Create a matrix of zeros with the dimensions of the unique values of the 'OBJECTID' and 'type' columns
    matrix = np.zeros((len(hybas_ids), len(types)))

    #--------------------------------------------------------------

    # Group by '_HYBAS_ID' and 'type', then sum 'Area_Ratio'
    grouped = df.groupby(['_HYBAS_ID', 'type'])['Area_Ratio'].sum()
    for i, obj_id in enumerate(hybas_ids):
        for j, t in enumerate(types):
            try:
                matrix[i, j] = grouped[obj_id, t]
            except KeyError:
                # If the combination of 'OBJECTID' and 'type' doesn't exist, leave the matrix value as 0
                pass

    df_matrix = pd.DataFrame(matrix, index=hybas_ids, columns=types)

    #--------------------------------------------------------------

    # Obtain the column _sum of the DataFrame and convert it to float
    pop_df['_sum'] = pop_df['_sum'].astype(float)

    # Add the column '_sum' from pop_df to the DataFrame df_matrix by grouping by '_HYBAS_ID'
    df_matrix['population'] = pop_df.groupby('_HYBAS_ID')['_sum'].sum()
    
    return df_matrix



    
    





