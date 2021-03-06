from bokeh.models.widgets import Tabs
from bokeh.io import curdoc

from tabs.world_map_tab import create_world_map_tab
from tabs.factors_tab import create_factors_tab

import geopandas as gpd
import pandas as pd
import os


# map year keys to csv values for each year happiness report
happ_dfs_dict = {2015: "2015.csv", 2016: "2016.csv", 2017: "2017.csv"}

# read geopandas world map
world_df = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

#read countries name mapping file
mapping_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', "country_mapping.csv"), 
	delimiter = ";")
name_mapping_dict = dict(zip(mapping_df.orig, mapping_df.new))

# create tabs
map_tab = create_world_map_tab(happ_dfs_dict, world_df, name_mapping_dict)
factors_tab = create_factors_tab(happ_dfs_dict, name_mapping_dict, world_df)
tabs = Tabs(tabs=[map_tab, factors_tab])

# add them to the document for bokeh server running
curdoc().add_root(tabs)