import os.path

import pandas

hp_df = pandas.read_excel(os.path.join(os.getcwd(), 'hp.xlsx'), sheet_name='Sheet1',index_col=0)
uf_df = pandas.read_excel(os.path.join(os.getcwd(), 'uf.xlsx'), sheet_name='Sheet1',index_col=0)

merged_df = pandas.concat([hp_df, uf_df])

merged_df.drop_duplicates(subset=['song_name', 'release_name', 'artist_name'], inplace=True)
merged_df.reset_index(drop=True, inplace=True)

merged_df.to_excel('merged.xlsx')
