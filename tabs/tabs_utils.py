import pandas as pd

'''
Data formatting: 

- cols names
  - to lowercase
  - replace space and point to '_'
- drop columns that are not in the name mapping
- use the name mapping to rename the countries
- rename columns in a easy and uniform way

'''
def format_data(happ_df, name_mapping_dict):
  happ_df.columns = map(str.lower, happ_df.columns)
  happ_df.columns = happ_df.columns.str.replace(' ', '_')
  happ_df.columns = happ_df.columns.str.replace('.', '_')

  countries_to_drop =  set(happ_df['country'].values) - set(name_mapping_dict.keys())
  happ_df = happ_df[~happ_df['country'].isin(countries_to_drop)]
    
  orig_names = happ_df['country'].values
  new_names = [name_mapping_dict[e] for e in orig_names]
  happ_df['country'] = new_names

  # last 7 columns are the factors common to all of 3 years
  happ_df = pd.concat([happ_df[['country', 'happiness_rank', 'happiness_score']], 
    happ_df.iloc[:, -7:]], axis = 1)
  happ_df.columns = ['name', 'rank', 'score'] + [e.split('_')[0] for e in happ_df.columns[-7:]]

  return happ_df

def style(p, size): 
  p.title.align = 'center'
  p.title.text_font_size = '18pt' if size == "large" else '14pt'
  p.title.text_font = 'serif'

  p.xaxis.axis_label_text_font_size = '14pt' if size == "large" else '12pt'
  p.xaxis.axis_label_text_font_style = 'bold'
  p.yaxis.axis_label_text_font_size = '14pt' if size == "large" else '12pt'
  p.yaxis.axis_label_text_font_style = 'bold'

  p.xaxis.major_label_text_font_size = '12pt' if size == "large" else '10pt'
  p.yaxis.major_label_text_font_size = '12pt' if size == "large" else '10pt'

  return p