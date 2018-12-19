from bokeh.models import ColumnDataSource, Panel, HoverTool, Circle, LassoSelectTool
from bokeh.models import CategoricalColorMapper, LinearColorMapper, ColorBar, BasicTicker
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.models.widgets import Slider, Select
from bokeh.plotting import figure

from .tabs_utils import format_data, style
from bokeh.transform import transform
from bokeh.palettes import RdGy

import pandas as pd
import numpy as np
import math
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


  def make_corr_dataset(year):

    happ_df = pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),
      "data", happ_dfs_dict[year]))

    final_df = format_data(happ_df, name_mapping_dict) 
    final_df = final_df.drop("rank", axis = 1)
    corr_df = final_df.corr()
    corr_df.index.name = 'Idx'
    corr_df.columns.name = 'Cols'
    corr_df = corr_df.stack().rename("value").reset_index()

    return ColumnDataSource(corr_df)


  def make_plot(src):

    p = figure(plot_width = 700, plot_height = 600, 
      title="Factor contribution to the happiness score",
      x_axis_label = 'Factor influence', y_axis_label = 'Happiness Score')

    regions = np.unique(src.data['selected_continent'])
    
    colors = ['orange', 'blue', 'red', 'yellow', 'navy', 'maroon']
    color_map = CategoricalColorMapper(factors=regions, palette=colors[:regions.shape[0]])

    p.circle(x = 'factor', y = 'score', size = 10, 
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

    p = style(p, size = "large")

    return p

  def make_corr_plot(src):

    p = figure(plot_width = 400, plot_height = 400, title = "Factors correlation matrix",
      x_range=list(np.unique(src.data['Idx'])),
      y_range=list(np.unique(src.data['Cols'])),
      tools="save")
    p.xaxis.major_label_orientation = math.pi/2

    color_map = LinearColorMapper(palette=RdGy[9], low=-1, high=1)

    p.rect('Idx', 'Cols', width=1, height=1, line_color=None, 
      fill_color = {'field': 'value', 'transform': color_map}, source=src)

    hover = HoverTool(
        tooltips=[
            ("Pair", "(@Idx, @Cols)"),
            ("Correlation", "@value{(0.00)}")
        ]
    )

    p.add_tools(hover)
    
    color_bar = ColorBar(color_mapper=color_map, ticker=BasicTicker(desired_num_ticks=9), 
      major_tick_out=0, major_tick_in=0, major_label_text_align='left',
      major_label_text_font_size='10pt', label_standoff=2, location=(0,0))

    p.add_layout(color_bar, 'right')
    p = style(p, "small")

    return p

  def update(attr, old, new):

    year = year_select.value
    factor = factor_select.value
    continent = continent_select.value

    new_src = make_dataset(year = year, factor = factor, continent = continent)
    new_corr_src = make_corr_dataset(year = year)
    src.data = new_src.data
    corr_src.data = new_corr_src.data


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
  corr_src = make_corr_dataset(year_select.value)

  scatter_p = make_plot(src)
  corr_p = make_corr_plot(corr_src)

  controls = WidgetBox(year_select, factor_select, continent_select)
  my_layout = layout([[column(controls, corr_p), scatter_p]], sizing_mode='fixed')

  return Panel(child=my_layout, title = 'Factors Influence')