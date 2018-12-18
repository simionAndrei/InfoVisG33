from bokeh.models import ColumnDataSource, CategoricalColorMapper, Panel, HoverTool, Circle, LassoSelectTool
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.models.widgets import Slider, Select
from bokeh.plotting import figure

from .tabs_utils import format_data, style

import pandas as pd
import numpy as np
import os


def create_factors_tab(happ_dfs_dict, name_mapping_dict, world_df):

  def make_dataset(year, factor, continent):

    happ_df = pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),
     "data", happ_dfs_dict[year]))

    final_df = format_data(happ_df, name_mapping_dict)
    final_df = final_df.merge(world_df, on='name')
    final_df['formatted_score'] = ["{:.2f}".format(s) for s in final_df['score'].values]
    final_df['factor'] = final_df[factor]
    final_df = final_df.drop(['geometry'], axis = 1)
    
    if continent.lower() != "all":
      final_df['selected_continent'] = [c if c == continent else "Other" for c in final_df['continent']]
    else:
      final_df['selected_continent'] = final_df['continent']

    return ColumnDataSource(final_df)


  def make_plot(src):

    p = figure(plot_width = 700, plot_height = 600, title="Factor contribution to the happiness score",
      x_axis_label = 'Happiness Score', y_axis_label = 'Factor influence')

    regions = np.unique(src.data['selected_continent'])
    print(regions)
    
    colors = ['orange', 'blue', 'red', 'yellow', 'navy', 'maroon']
    color_map = CategoricalColorMapper(factors=regions, palette=colors[:regions.shape[0]])

    p.circle(x = 'score', y = 'factor', size = 10, 
      color = {'field': 'selected_continent', 'transform': color_map},
      legend='selected_continent', source = src)

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    hover = HoverTool(
        tooltips=[
            ("Country", "@name"),
            ("Continent", "@continent"),
            ("Score", "@score")
        ]
    )

    p.add_tools(hover)
    p.add_tools(LassoSelectTool())

    p = style(p, size = "small")

    return p


  def update(attr, old, new):

    year = year_select.value
    factor = factor_select.value
    continent = continent_select.value

    new_src = make_dataset(year = year, factor = factor, continent = continent)
    src.data = new_src.data


  year_select = Slider(start = 2015, end = 2017, step = 1, value = 2015,
    title ='Report Year')
  factor_select = Select(title="Factor:", value="economy", 
    options=["economy", "trust", "family", "health", "freedom", "generosity", "dystopia"])
  continent_select = Select(title="Continent", value="All", 
    options=["All", "Europe", "North America", "Oceania", "Asia", "South America", "Africa"])

  year_select.on_change('value', update)
  factor_select.on_change('value', update)
  continent_select.on_change('value', update)

  src = make_dataset(year_select.value, factor_select.value, continent_select.value)
  scatter_p = make_plot(src)

  controls = WidgetBox(year_select, factor_select, continent_select)
  my_layout = layout([[row(controls, scatter_p)]], sizing_mode='fixed')

  return Panel(child=my_layout, title = 'Factors Influence')