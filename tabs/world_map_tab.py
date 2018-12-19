from bokeh.models import GeoJSONDataSource, Panel, ColumnDataSource, HoverTool
from bokeh.models import LinearColorMapper, ColorBar, FixedTicker, FuncTickFormatter
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.plotting import figure
from bokeh.models.widgets import Slider
from bokeh.palettes import Viridis256

from .tabs_utils import format_data, style

import geopandas as gpd
import pandas as pd
import numpy as np
import os


def create_world_map_tab(happ_dfs_dict, world_df, name_mapping_dict):


  '''
  
  Read happiness data from the provided year
  Format and merge with geopandas world map dataset
  Add formatted_score column for the custom HTML hover tool score display
  Add status column for the happiness emoji on ohvertool
  Prepare data for bokeh p.patches
  
  '''
  def make_map_dataset(year):
    happ_df = pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), 
      "data", happ_dfs_dict[year]))

    happ_df = format_data(happ_df, name_mapping_dict)
    final_df = happ_df.merge(world_df, on='name')
    final_df['formatted_score'] = ["{:.2f}".format(s) for s in final_df['score'].values]

    # 0 ..... Sad ..... mean - std ..... Neutral .... mean ......  Neutral .... mean + std ... Happy...
    countries_status = []
    scores = final_df['score'].values
    mean, std = scores.mean(), scores.std()
    for score in scores:
      if score < (mean - std):
        countries_status.append("sad")
      elif score < mean or score < (mean + std):
        countries_status.append("neutral")
      else:
        countries_status.append("happy")

    final_df['status'] = countries_status

    tmp_geo = final_df['geometry']
    final_df = final_df.drop(['geometry'], axis = 1)
    crs = {'init': 'epsg:4326'}
    custom_src = GeoJSONDataSource(geojson = gpd.GeoDataFrame(final_df, crs=crs, 
      geometry=tmp_geo).to_json())

    return custom_src


  '''
  
  Read happiness data from the provided year
  Format data
  Compute histogram counts and intervals

  '''
  def make_hist_dataset(year, bin_width):
    happ_df = pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), 
      "data", happ_dfs_dict[year]))

    happ_df = format_data(happ_df, name_mapping_dict)

    hist, edges = np.histogram(happ_df['score'], bins = bin_width)

    final_df = pd.DataFrame({'top': hist, 'left': edges[:-1], 'right': edges[1:]})

    return ColumnDataSource(final_df)


  '''
  Create world map with lighter to darker color filling pallete and customize
  HTML hovertool for displaying happiness status as emoji
  '''
  def make_map(src):

    p = figure(plot_width = 900, plot_height = 600, title="Happiness Map")
    p.axis.visible = False

    collor_filler = {'field': 'score', 'transform': LinearColorMapper(palette=Viridis256)}
    p.patches('xs', 'ys', fill_alpha=0.9, fill_color=collor_filler, line_color='black', 
      line_width=0.5, hover_fill_color = collor_filler, hover_fill_alpha = 1.0, source=src)

    hover = HoverTool(
        tooltips="""
          <div>
            <div>
              <img
                  src="infovis_app/static/@status.jpg" height="35" alt="@status" width="35"
                  style="float: left; margin: 0px 10px 10px 0px;"
                  border="0"
              ></img>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;"> @name</span>
            </div>
            <div>
                <span style="font-size: 15px; color: #966;"><font color="#CEACE6">Rank:</font> @rank</span>
            </div>
            <div>
                <span style="font-size: 15px; color: #966;"><font color="#CEACE6">Score:</font> @formatted_score</span>
            </div>
          </div>
        """
      )

    p.add_tools(hover)

    # lowest happiness score around 2.4 and highest around 7.6
    color_mapper = LinearColorMapper(palette=Viridis256, low=2.3, high=7.7)
    ticker = FixedTicker(ticks=[3, 4, 5, 6, 7])
    # labels for the colorbar in intervals
    formatter = FuncTickFormatter(code="""
      data = {3: '<3', 4: '3-4', 5: '4-5', 6: '5-6', 7: '>7'}
      return data[tick]
    """)

    color_bar = ColorBar(color_mapper=color_mapper, ticker=ticker, formatter = formatter,
                        major_tick_out=0, major_tick_in=0, major_label_text_align='left',
                      major_label_text_font_size='12pt', label_standoff=4)

    p.add_layout(color_bar, 'right')

    p = style(p, size = "large")

    return p

  
  '''
  Create histogram for happiness score distribution

  '''
  def make_hist(src):

    p = figure(plot_width = 400, plot_height = 500, title = 'Histogram of Happiness Score',
                x_axis_label = 'Score (0-10)', y_axis_label = 'Count', tools = "save")

    p.quad(source = src, bottom=0, top='top', left='left', right='right', 
            fill_color='orange', line_color='black', fill_alpha = 0.7, 
            hover_fill_color = 'orange', hover_fill_alpha = 1.0)

    hover = HoverTool(
        tooltips=[
            ("Count", "@top"),
            ("Interval", "@left{(0.00)} - @right{(0.00)}")
        ], mode='vline'
    )

    p.add_tools(hover)
    p = style(p, size = "small")

    return p


  '''
  Update the bokeh data sources used for plotting based on dynamic widget interaction
  '''
  def update(attr, old, new):

    year = year_select.value
    bin_width = bin_select.value

    new_map_src = make_map_dataset(year = year)
    new_hist_src = make_hist_dataset(year = year, bin_width = bin_width)

    map_src.geojson = new_map_src.geojson
    hist_src.data = new_hist_src.data



  '''
  Create all the elements: widgets, data sources, figures and layout
  '''

  year_select = Slider(start = 2015, end = 2017, step = 1, value = 2015,
    title ='Report Year')
  bin_select = Slider(start = 5, end = 20, step = 1, value = 10,
    title ='Histogram Bins')

  year_select.on_change('value', update)
  bin_select.on_change('value', update)

  map_src = make_map_dataset(year = year_select.value)
  hist_src = make_hist_dataset(year = year_select.value, bin_width = bin_select.value)

  map_p = make_map(map_src)
  hist_p = make_hist(hist_src)

  controls = WidgetBox(year_select, bin_select)
  my_layout = layout([[column(controls, hist_p), map_p]], sizing_mode='fixed')

  return Panel(child=my_layout, title = 'World Map')