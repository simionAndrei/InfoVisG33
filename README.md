# InfoVisG33

Code for Group 33 [Bokeh](https://bokeh.pydata.org/en/latest/) python implementation of InfoVis Project IN4086-14

Team members:
 * [Simion-Constantinescu Andrei](https://www.linkedin.com/in/andrei-simion-constantinescu/)
 * [Marie Kegeleers](https://www.tudelft.nl/ewi/)
 * [Natasha Kabra](https://www.tudelft.nl/ewi/)

## Data

The happiness report data is available on [Kaggle](https://www.kaggle.com/unsdsn/world-happiness).

## Project structure

The project tree is displayed bellow:
```
infovis_app
│   
│   main.py    
│
└───data
│   │   2015.csv
│   │   2016.csv
│   │   2017.csv
│   │   country_mapping.csv
│   └───
└───static
│   │   happy.jpg
│   │   sad.jpg
│   │   neutral.jpg
│   └───
└───tabs
    │   factors_tab.py
    │   world_map_tab.py
    │   tabs_utils.py
    └───     
```

## Environment
The application can be run in [Anaconda](https://www.anaconda.com/) Windows environment.
After installing anaconda, an enviroment needs to be created:
```
conda create -n datavis_prj python=3.5 numpy pandas scipy
```
After creating `datavis_prj` enviroment, we activate it and install the following additional packages:
```
activate datavis_prj
conda install -c conda-forge geopandas
conda install -c bokeh bokeh 
conda install requests
```

If you encounter problems with [`fiona`](https://anaconda.org/conda-forge/fiona) package, you should uninstall it and install *1.6 version*:
```
conda install fiona=1.6
```

## Run
To run the application, inside `datavis_prj` enviroment from the parent directory of `infovis_app` folder type the following command:
```
bokeh serve infovis_app -- show
```
