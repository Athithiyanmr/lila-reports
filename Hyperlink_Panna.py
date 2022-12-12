# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import folium
from osgeo import gdal
from folium import plugins,Vega
from folium import raster_layers
#from matplotlib import cm
import numpy as np
import branca.colormap as cm
#import branca
import matplotlib
from matplotlib import colors
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster,FloatImage, Draw, MeasureControl
# import osmnx as ox
# import geopandas
# import vincent
# from vincent import Bar,AxisProperties, PropertySet, ValueRef
import geopandas as gpd
import os
# import plotly.graph_objects as go
# import branca
# import plotly.io as pio
# from plotly.subplots import make_subplots
from matplotlib import colors
from matplotlib.colors import ListedColormap, LinearSegmentedColormap


# %%
def get_rooted(stem):
    return "D:\\Panna\\" + stem
def read_df_UT(stem):
    return gpd.read_file(get_rooted(stem)).to_crs(epsg = 4326)


# %% [markdown]
# ## Hyperlink - Panna District

# %% [markdown]
# ### Features

# %%

# %%
_shp_district = read_df_UT("forest\\Panna\\panna_dst.shp")
_shp_district.to_file('_shp_district.json', driver='GeoJSON')
_shp_district = os.path.join('', '_shp_district.json') 

roads_prim_sec_ter = gpd.read_file("D:\\Panna\\roads_prim_sec_ter.shp")
def regioncolors(roads_prim_sec_ter):
    if roads_prim_sec_ter['highway'] == 'primary':
        return '#df2a29'
    elif roads_prim_sec_ter['highway']  == 'secondary':
        return '#E97C78'
    elif roads_prim_sec_ter['highway']  == 'tertiary':
        return '#f0b8b3'    
    
roads_prim_sec_ter["color"] = roads_prim_sec_ter.apply(regioncolors, axis=1)
roads_prim_sec_ter.to_file('roads_prim_sec_ter.json', driver='GeoJSON')
roads_prim_sec_ter = os.path.join('', 'roads_prim_sec_ter.json')



substations =gpd.read_file("D:\\Hasten Ventures\\Features\\Substations\\Substations.shp")
substations.to_file('substations.json', driver='GeoJSON')
substations = os.path.join('', 'substations.json')


Forest_reserve =gpd.read_file("D:\Hasten Ventures\Features\Forest_reserve\\Forest_reserve.shp")
Forest_reserve = Forest_reserve.round({"area_hect":0})
Forest_reserve["area_hect"] = Forest_reserve["area_hect"].replace([0],["< 1"])
Forest_reserve.to_file('Forest_reserve.json', driver='GeoJSON')
Forest_reserve = os.path.join('', 'Forest_reserve.json')



outfile = 'D:\\Panna\\workdir\\slope.tif'
#Open raster file
driver=gdal.GetDriverByName('GTiff')
driver.Register() 
ds1 = gdal.Open(outfile)
if ds1 is None:
    print('Could not open')

band=ds1.GetRasterBand(1)

data= band.ReadAsArray()


#Get coordinates, cols and rows
geotransform = ds1.GetGeoTransform()
cols2 = ds1.RasterXSize
rows2 = ds1.RasterYSize

#Get extent
xmin2=geotransform[0]
ymax2=geotransform[3]
xmax2=xmin2+cols2*geotransform[1]
ymin2=ymax2+rows2*geotransform[5]

#Get Central point
centerx=(xmin2+xmax2)/2
centery=(ymin2+ymax2)/2


a = np.nanmax(data)
b = np.nanmin(data)

print(a,b)     
def get_color_slope(x):
   
    if 0<= x <= 45:
        return (240,240,240,1)
    elif 45 < x <= 90 :
        return (195,195,195,1)
    elif 90 < x <=135 :
        return (150,150,150,1)
    elif 135 < x <= 180:
        return (104,104,104,0.7)
    elif 180 < x <=225 :
        return (104,104,104,1)
    else:
        return (255,0,0,0)


# AVC_grey = LinearSegmentedColormap.from_list('testcmap1', colors=['#686868', '#969696', '#c3c3c3', '#F0F0F0'], N=256)






m= folium.Map(location=[24.436933515, 80.20336914], zoom_start=8)
 

g2 = folium.plugins.FeatureGroupSubGroup(m, 'Slope',show=False)
g3 = folium.plugins.FeatureGroupSubGroup(m, 'Substations',show=False)
g4 = folium.plugins.FeatureGroupSubGroup(m, 'Roads',show=False)
g5 = folium.plugins.FeatureGroupSubGroup(m, 'Forest reserve',show=False)


m.add_child(g2)
m.add_child(g3)
m.add_child(g4)
m.add_child(g5)




tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(m)




loc = 'District features'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)   


m.get_root().html.add_child(folium.Element(title_html))


cm2 = cm.LinearColormap(['#F0F0F0','#c3c3c3','#969696','#686868'], vmin=0, vmax=225, caption='Elevation in meters')
m.add_child(cm2)

folium.GeoJson(
    _shp_district,
     name='dist_boundary',
    show = True,
    control = False,
        style_function=lambda feature: {
        'fillColor': "none",
        'color' : "black",
        'weight' : 1,
        'fillOpacity' : 0.5,
        },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['AREA'],labels=False, toLocaleString=True)
      #smooth_factor=2.0           
).add_to(m)




g2.add_child(raster_layers.ImageOverlay(
    image=data,
    show=False,
    name = 'Slope',
    bounds=[[ymin2, xmin2], [ymax2, xmax2]],
    colormap=lambda x: get_color_slope(x),
    interactive=True,
    mercator_project = True,
    opacity=1
))#.add_to(m)

# ###Reference

folium.GeoJson(
    substations,
     name='Substations',
    show = False,
#         style_function=lambda feature: {
#         'fillColor': "#FBB034",
#         'color' : "#FBB034",
#         'weight' : 3,
#         'fillOpacity' : 0.5,
#         },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['name'],aliases=["Name:"],labels=True, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(g3)


folium.GeoJson(
    roads_prim_sec_ter,
     name='Roads',
    show = False,
        style_function=lambda feature: {
        'fillColor': feature['properties']['color'],
        'color' :  feature['properties']['color'],
        'weight' : 3,
        'fillOpacity' : 0.5,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['highway'],aliases=["Type :"] ,labels=True, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(g4)


folium.GeoJson(
    Forest_reserve,
     name='Forest Reserve',
    show = False,
        style_function=lambda feature: {
        'fillColor': "#048160",
        'color' :  "#048160",
        'weight' : 3,
        'fillOpacity' : 0.5,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(g5)


plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(m)

minimap = plugins.MiniMap()
m.add_child(minimap)



# Add drawinf controls
draw = Draw()
draw.add_to(m)
m.add_child(MeasureControl())


folium.LayerControl().add_to(m)
#plugins.Geocoder().add_to(m)
m.save('D:\\Panna\\workdir\\Features.html')


# %% [markdown]
# ### Land Cover

# %%
_shp_district = read_df_UT("forest\\Panna\\panna_dst.shp")
_shp_district.to_file('_shp_district.json', driver='GeoJSON')
_shp_district = os.path.join('', '_shp_district.json')


filename = 'D:\\Panna\\workdir\\tempo.tif'


#Open raster file
driver=gdal.GetDriverByName('GTiff')
driver.Register() 
ds = gdal.Open(filename) 
if ds is None:
    print('Could not open')

#Get coordinates, cols and rows
geotransform = ds.GetGeoTransform()
cols = ds.RasterXSize 
rows = ds.RasterYSize 

#Get extent
xmin=geotransform[0]
ymax=geotransform[3]
xmax=xmin+cols*geotransform[1]
ymin=ymax+rows*geotransform[5]

#Get Central point
centerx=(xmin+xmax)/2
centery=(ymin+ymax)/2

#Raster convert to array in numpy
bands = ds.RasterCount
band=ds.GetRasterBand(1)
dataset= band.ReadAsArray(0,0,cols,rows)
dataimage=dataset

color_labels = np.unique(dataset)
print(color_labels)

#dataimage1=np.where(dataset==100, 7, dataimage1) 

# extract clouds
#dataimage1=np.where(dataset==100, 1, 0)
# extract unclassified
dataimage2=np.where(dataset==0, 100, 0) 
#extract Barren
dataimage3=np.where(dataset==1, 1, 0) 
#extract Sparse Vegetation
dataimage4=np.where(dataset==2, 2, 0)
#extract CropLand
dataimage5=np.where(dataset==3, 3, 0)
#extract Forests
dataimage6=np.where(dataset==4, 4, 0)
#extract Water
dataimage7=np.where(dataset==5, 5, 0)  
#extract Urban
dataimage8=np.where(dataset==6, 6, 0) 






m= folium.Map(location=[24.436933515, 80.20336914], zoom_start=8)
 

g2 = folium.plugins.FeatureGroupSubGroup(m, 'Unused',show=False)
g3 = folium.plugins.FeatureGroupSubGroup(m, 'Sparse vegetation',show=False)
g4 = folium.plugins.FeatureGroupSubGroup(m, 'Cropland',show=False)
g5 = folium.plugins.FeatureGroupSubGroup(m, 'Forest',show=False)
g6 = folium.plugins.FeatureGroupSubGroup(m, 'Water',show=False)
g7 = folium.plugins.FeatureGroupSubGroup(m, 'Built-up',show=False)


m.add_child(g2)
m.add_child(g3)
m.add_child(g4)
m.add_child(g5)
m.add_child(g6)
m.add_child(g7)

tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(m)




loc = 'Land cover map'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)   


m.get_root().html.add_child(folium.Element(title_html))



folium.GeoJson(
    _shp_district,
     name='dist_boundary',
    show = True,
    control = False,
        style_function=lambda feature: {
        'fillColor': "none",
        'color' : "black",
        'weight' : 1,
        'fillOpacity' : 0.5,
        },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['AREA'],labels=False, toLocaleString=True)
      #smooth_factor=2.0           
).add_to(m)



g2.add_child(raster_layers.ImageOverlay(
    image=dataimage3,
    show=False,
    name = 'Unused',
    bounds=[[ymin, xmin], [ymax, xmax]],
    colormap=lambda x: (1-x,1-x, 1-x,0+x*255),#R,G,B,red: (255,0,0)
    interactive=True,
    mercator_project = True,
    opacity=1
))#.add_to(m)

g3.add_child(raster_layers.ImageOverlay(
    image=dataimage4,
    show=False,
    name = 'Sparse Vegetation',
    bounds=[[ymin, xmin], [ymax, xmax]],
    colormap=lambda x: (253+x,0,253+x,0+x*127),#R,G,B,alpha Yellow: (255,255,0) (255,0,255)
    interactive=True,
    mercator_project = True,
    opacity=1
))#.add_to(m)

g4.add_child(raster_layers.ImageOverlay(
    image=dataimage5,
    show=False,
    name = 'CropLand',
    bounds=[[ymin, xmin], [ymax, xmax]],
    colormap=lambda x: (3-x,13-x, 3-x,0+x*85),#R,G,B,alpha Lime Green (0,255,0)(0,10,0)
    interactive=True,
    mercator_project = True,
    opacity=1
))#.add_to(m)

g5.add_child(raster_layers.ImageOverlay(
    image=dataimage6,
    show=False,
    name = 'Forest',
    bounds=[[ymin, xmin], [ymax, xmax]],
    colormap=lambda x: (4-x,251+x,4-x,0+x*63),#R,G,B,alpha Dark Green (0,10,0)(0,255,0)
    interactive=True,
    mercator_project = True,
    opacity=1
))#.add_to(m)

g6.add_child(raster_layers.ImageOverlay(
    image=dataimage7,
    show=False,
    name = 'Water',
    bounds=[[ymin, xmin], [ymax, xmax]],
    colormap=lambda x: (5-x,250+x, 250+x,0+x*51),#R,G,B,alpha Blue (0, 255, 255)
    interactive=True,
    mercator_project = True,
    opacity=1
))#.add_to(m)

g7.add_child(raster_layers.ImageOverlay(
    image=dataimage8,
    show=False,
    name = 'Urban',
    bounds=[[ymin, xmin], [ymax, xmax]],
    colormap=lambda x: (249+x,6-x,6-x,0+x*42),#R,G,B,alpha Fuchsia (255,0,255)(255,0,0)
    interactive=True,
    mercator_project = True,
    opacity=1
))#.add_to(m)



plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(m)

minimap = plugins.MiniMap()
m.add_child(minimap)



# Add drawinf controls
draw = Draw()
draw.add_to(m)
m.add_child(MeasureControl())


folium.LayerControl().add_to(m)
#plugins.Geocoder().add_to(m)
m.save('D:\\Panna\\workdir\\Landcover.html')

# %% [markdown]
# ### Competing use

# %%
_shp_merge_tech_water = gpd.read_file("D:\\Hasten Ventures\\Competing Use\\CompetingUse_w_Water\\CompetingUse_w_Water.shp")
_shp_merge_tech_water = _shp_merge_tech_water.round({"area_hect":0})
_shp_merge_tech_water.to_file('_shp_merge_tech_water.json', driver='GeoJSON')
_shp_merge_tech_water = os.path.join('', '_shp_merge_tech_water.json')

lc_tech = gpd.read_file("D:\\Hasten Ventures\\Technical Suitability\\Technical_Potential\\Technical_Potential.shp")

lc_tech = lc_tech.to_crs(4326)

def regioncolors(lc_tech):
    if lc_tech['area_class'] == 'A':
        return '#455555'
    elif lc_tech['area_class']  == 'B':
        return '#157e5c'
    elif lc_tech['area_class']  == 'C':
        return '#54ad64'
    elif lc_tech['area_class']  == 'D':
        return '#99cc66'
    
    
lc_tech["color"] = lc_tech.apply(regioncolors, axis=1)
lc_tech = lc_tech.round({"area_hect":0})
lc_tech["area_class"] = lc_tech["area_class"].replace(['A','B','C','D'],['Small area','Medium area','Large area','Very Large Area'])
lc_tech.to_file('lc_tech.json', driver='GeoJSON')
lc_tech = os.path.join('', 'lc_tech.json')


_shp_district = read_df_UT("forest\\Panna\\panna_dst.shp")
_shp_district.to_file('_shp_district.json', driver='GeoJSON')
_shp_district = os.path.join('', '_shp_district.json')


m= folium.Map(location=[24.436933515, 80.20336914], zoom_start=8)

    


loc = 'Competing land-use for climate action'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)   


m.get_root().html.add_child(folium.Element(title_html))




tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(m)




folium.GeoJson(
    lc_tech,
     name='Forest Technical Potential',
    show = False,
        style_function=lambda feature: {
        'fillColor': feature['properties']['color'],
        'color' : feature['properties']['color'],
        'weight' : 3,
        'fillOpacity' : 0.5,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect','area_class'],aliases =["Area (hect) :","Class :"],labels=True, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(m)





folium.GeoJson(
    _shp_merge_tech_water,
     name='Water Harvesting Potential',
    show = False,
        style_function=lambda feature: {
        'fillColor': "#00B9F2",
        'color' : "#00B9F2",
        'weight' : 3,
        'fillOpacity' : 0.5,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases=["Overlap Area (hect) :"],labels=True, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(m)



folium.GeoJson(
    _shp_district,
     name='dist_boundary',
    show = False,
    control = False,
        style_function=lambda feature: {
        'fillColor': "none",
        'color' : "black",
        'weight' : 1,
        'fillOpacity' : 0.5,
        },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['AREA'],labels=False, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(m)

plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(m)

minimap = plugins.MiniMap()
m.add_child(minimap)



# Add drawinf controls
draw = Draw()
draw.add_to(m)
m.add_child(MeasureControl())


folium.LayerControl().add_to(m)

m.save('D:\\Panna\\workdir\\Competinguse.html')

# %% [markdown]
# ## Land Suitability

# %% [markdown]
# ### No potential File

# %%
# _shp_district = read_df_UT("forest\\Panna\\panna_dst.shp")
# _shp_district.to_file('_shp_district.json', driver='GeoJSON')
# _shp_district = os.path.join('', '_shp_district.json') 

# lc_tech = gpd.read_file("D:\\Hasten Ventures\\Technical Suitability\\Technical_Potential\\Technical_Potential.shp")

# lc_tech = lc_tech.to_crs(4326)

# def regioncolors(lc_tech):
#     if lc_tech['area_class'] == 'A':
#         return '#455555'
#     elif lc_tech['area_class']  == 'B':
#         return '#157e5c'
#     elif lc_tech['area_class']  == 'C':
#         return '#54ad64'
#     elif lc_tech['area_class']  == 'D':
#         return '#99cc66'
    
    
# lc_tech["color"] = lc_tech.apply(regioncolors, axis=1)
# lc_tech = lc_tech.round({"area_hect":0})
# lc_tech["area_class"] = lc_tech["area_class"].replace(['A','B','C','D'],['Small area','Medium area','Large area','Very Large Area'])
# lc_tech.to_file('lc_tech.json', driver='GeoJSON')
# lc_tech = os.path.join('', 'lc_tech.json')




# # filename = 'D:\\Panna\\workdir\\tempo.tif'


# # #Open raster file
# # driver=gdal.GetDriverByName('GTiff')
# # driver.Register() 
# # ds = gdal.Open(filename) 
# # if ds is None:
# #     print('Could not open')

# # #Get coordinates, cols and rows
# # geotransform = ds.GetGeoTransform()
# # cols = ds.RasterXSize 
# # rows = ds.RasterYSize 

# # #Get extent
# # xmin=geotransform[0]
# # ymax=geotransform[3]
# # xmax=xmin+cols*geotransform[1]
# # ymin=ymax+rows*geotransform[5]

# # #Get Central point
# # centerx=(xmin+xmax)/2
# # centery=(ymin+ymax)/2

# # #Raster convert to array in numpy
# # bands = ds.RasterCount
# # band=ds.GetRasterBand(1)
# # dataset= band.ReadAsArray(0,0,cols,rows)
# # dataimage=dataset

# # color_labels = np.unique(dataset)
# # print(color_labels)

# # #dataimage1=np.where(dataset==100, 7, dataimage1) 

# # # extract clouds
# # #dataimage1=np.where(dataset==100, 1, 0)
# # # extract unclassified
# # # dataimage2=np.where(dataset==0, 100, 0) 
# # #extract Barren
# # dataimage3=np.where(dataset==1, 1, 0) 




# No_potential = gpd.read_file("D:\\Hasten Ventures\\Technical Suitability\\No_Potential\\test_no_potential.shp")
# No_potential = No_potential.to_crs(4326)
# # No_potential = No_potential.round({"area_hect":0})
# # No_potential["area_hect"] = No_potential["area_hect"].replace([0],['< 1'])
# No_potential.to_file('No_potential.json', driver='GeoJSON')
# No_potential = os.path.join('', 'No_potential.json')



# theo_only = gpd.read_file("D:\\Hasten Ventures\\Technical Suitability\\\Only_theoretical\\\Only_theoretical.shp")
# theo_only = theo_only.round({"area_hect":0})
# theo_only["area_hect"] = theo_only["area_hect"].replace([0],["< 1"])
# theo_only.to_file('theo_only.json', driver='GeoJSON')
# theo_only = os.path.join('', 'theo_only.json')


# med =  gpd.read_file("D:\\Hasten Ventures\\High Potential\\Medium_Potential\\Medium_Potential.shp")
# med = gpd.GeoDataFrame(med)
# med = med.to_crs(4326)
# med = med.round({"area_hect":0})
# med.to_file('med.json', driver='GeoJSON')
# med = os.path.join('', 'med.json')



# low =  gpd.read_file("D:\\Hasten Ventures\\High Potential\\Low_Potential\\Low_Potential.shp")
# low = low.to_crs(4326)
# low = low.round({"area_hect":0})
# low.to_file('low.json', driver='GeoJSON')
# low = os.path.join('', 'low.json')



# # high =  gpd.read_file("D:\\Hasten Ventures\\High Potential\\High_Potential\\High_Potential.shp")
# # high = high[["geometry","area_hect"]]
# # high = gpd.GeoDataFrame(high)
# # high = high.to_crs(4326)
# # high = high.round({"area_hect":0})
# # high.to_file('high.json', driver='GeoJSON')
# # high = os.path.join('', 'high.json')


# m= folium.Map(location=[24.436933515, 80.20336914], zoom_start=8)


# tile = folium.TileLayer(
#         tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
#         attr = 'Esri',
#         name = 'Esri Satellite',
#         overlay = False,
#         control = True
#        ).add_to(m)




# loc = 'Land potential and distribution by size'
# title_html = '''
#              <h3 align="center" style="font-size:16px"><b>{}</b></h3>
#              '''.format(loc)   


# m.get_root().html.add_child(folium.Element(title_html))



# folium.GeoJson(
#     _shp_district,
#     name='dist_boundary',
#     show = False,
#     control = False,
#         style_function=lambda feature: {
#         'fillColor': "none",
#         'color' : "black",
#         'weight' : 1,
#         'fillOpacity' : 0.5,
#         },
# #          highlight_function=lambda x: {'weight':5,'color':'yellow'},
# #          tooltip=folium.features.GeoJsonTooltip(fields=['AREA'],labels=False, toLocaleString=True)
#       #smooth_factor=2.0
           
#     ).add_to(m)


# folium.GeoJson(
#     No_potential,
#     name='No potential',
#     show = False,
#         style_function=lambda feature: {
#         'fillColor': "#424242",
#         'color' : "#424242",
#         'weight' : 3,
#         'fillOpacity' : 0.5,
#         },
# #          highlight_function=lambda x: {'weight':5,'color':'yellow'},
# #          tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
#       smooth_factor=1000
           
#     ).add_to(m)




# # m.add_child(raster_layers.ImageOverlay(
# #     image=dataimage3,
# #     show=False,
# #     name = 'No Potential',
# #     bounds=[[ymin, xmin], [ymax, xmax]],
# #     colormap=lambda x: (1-x,1-x, 1-x,0+x*255),#R,G,B,red: (255,0,0)
# #     interactive=True,
# #     mercator_project = True,
# #     opacity=1
# # ))#.add_to(m)


# folium.GeoJson(
#     theo_only,
#     name='Theoritical potential',
#     show = False,
#         style_function=lambda feature: {
#         'fillColor':"#15915C",
#         'color' : "#15915C",
#         'weight' : 3,
#         'fillOpacity' : 0.5,
#         },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
#       smooth_factor=2.0
           
#     ).add_to(m)



# folium.GeoJson(
#     lc_tech,
#     name='Technical potential',
#     show = False,
#         style_function=lambda feature: {
#         'fillColor':feature['properties']['color'],
#         'color' : feature['properties']['color'],
#         'weight' : 3,
#         'fillOpacity' : 0.5,
#         },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['area_hect','area_class'],aliases =["Area (hect) :","Class :"],labels=True, toLocaleString=True),
#       smooth_factor=2.0
           
#     ).add_to(m)



# folium.GeoJson(
#     low,
#     name='Low technical potential',
#     show = False,
#         style_function=lambda feature: {
#         'fillColor': "#21583B",
#         'color' : "#21583B",
#         'weight' : 3,
#         'fillOpacity' : 0.5,
#         },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
#       smooth_factor=2.0
           
#     ).add_to(m)


# folium.GeoJson(
#      med,
#      name='Medium technical potential',
#      show = False,
#          style_function=lambda feature: {
#          'fillColor': "#009541",
#          'color' : "#009541",
#          'weight' : 3,
#          'fillOpacity' : 0.5,
#          },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
#       smooth_factor=2.0
           
#     ).add_to(m)
 


# # folium.GeoJson(
# #     high,
# #     name='High technical potential',
# #     show = False,
# #         style_function=lambda feature: {
# #         'fillColor': "#99CC66",
# #         'color' : "#99CC66",
# #         'weight' : 3,
# #         'fillOpacity' : 0.5,
# #         },
# #          highlight_function=lambda x: {'weight':5,'color':'yellow'},
# #          tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
# #       smooth_factor=2.0
           
# #     ).add_to(m)



# # m.add_child(folium.ClickForMarker(popup='point added'))
# # #m.add_child(folium.LatLngPopup())

# # folium.LatLngPopup().add_to(m)
# # folium.LayerControl(collapsed = False).add_to(m)




# plugins.Fullscreen(
#     position="topright",
#     title="Expand me",
#     title_cancel="Exit me",
#     force_separate_button=True,
# ).add_to(m)

# minimap = plugins.MiniMap()
# m.add_child(minimap)



# # Add drawinf controls
# draw = Draw()
# draw.add_to(m)
# m.add_child(MeasureControl())


# folium.LayerControl().add_to(m)

# # plugins.Geocoder().add_to(m)


# m.save('D:\\Panna\\workdir\\Landsuitability.html')

# %% [markdown]
# ### Un Used Lands 

# %%
_shp_district = read_df_UT("forest\\Panna\\panna_dst.shp")
_shp_district.to_file('_shp_district.json', driver='GeoJSON')
_shp_district = os.path.join('', '_shp_district.json') 

lc_tech = gpd.read_file("D:\\Hasten Ventures\\Technical Suitability\\Technical_Potential\\Technical_Potential.shp")

lc_tech = lc_tech.to_crs(4326)

def regioncolors(lc_tech):
    if lc_tech['area_class'] == 'A':
        return '#455555'
    elif lc_tech['area_class']  == 'B':
        return '#157e5c'
    elif lc_tech['area_class']  == 'C':
        return '#54ad64'
    elif lc_tech['area_class']  == 'D':
        return '#99cc66'
    
    
lc_tech["color"] = lc_tech.apply(regioncolors, axis=1)
lc_tech = lc_tech.round({"area_hect":0})
lc_tech["area_hect"] = lc_tech["area_hect"].replace([0],["< 1"])
lc_tech["area_class"] = lc_tech["area_class"].replace(['A','B','C','D'],['Small area','Medium area','Large area','Very Large Area'])
lc_tech.to_file('lc_tech.json', driver='GeoJSON')
lc_tech = os.path.join('', 'lc_tech.json')




filename = 'D:\\Panna\\workdir\\tempo.tif'


#Open raster file
driver=gdal.GetDriverByName('GTiff')
driver.Register() 
ds = gdal.Open(filename) 
if ds is None:
    print('Could not open')

#Get coordinates, cols and rows
geotransform = ds.GetGeoTransform()
cols = ds.RasterXSize 
rows = ds.RasterYSize 

#Get extent
xmin=geotransform[0]
ymax=geotransform[3]
xmax=xmin+cols*geotransform[1]
ymin=ymax+rows*geotransform[5]

#Get Central point
centerx=(xmin+xmax)/2
centery=(ymin+ymax)/2

#Raster convert to array in numpy
bands = ds.RasterCount
band=ds.GetRasterBand(1)
dataset= band.ReadAsArray(0,0,cols,rows)
dataimage=dataset

color_labels = np.unique(dataset)
print(color_labels)

#dataimage1=np.where(dataset==100, 7, dataimage1) 

# extract clouds
#dataimage1=np.where(dataset==100, 1, 0)
# extract unclassified
# dataimage2=np.where(dataset==0, 100, 0) 
#extract Barren
dataimage3=np.where(dataset==1, 1, 0) 




# No_potential = gpd.read_file("D:\\Hasten Ventures\\Technical Suitability\\No_Potential\\test_no_potential.shp")
# No_potential = No_potential.to_crs(4326)
# # No_potential = No_potential.round({"area_hect":0})
# # No_potential["area_hect"] = No_potential["area_hect"].replace([0],['< 1'])
# No_potential.to_file('No_potential.json', driver='GeoJSON')
# No_potential = os.path.join('', 'No_potential.json')



theo_only = gpd.read_file("D:\\Hasten Ventures\\Technical Suitability\\\Only_theoretical\\\Only_theoretical.shp")
theo_only = theo_only.round({"area_hect":0})
theo_only["area_hect"] = theo_only["area_hect"].replace([0],["< 1"])
theo_only.to_file('theo_only.json', driver='GeoJSON')
theo_only = os.path.join('', 'theo_only.json')


med =  gpd.read_file("D:\\Hasten Ventures\\High Potential\\Medium_Potential\\Medium_Potential.shp")
med = gpd.GeoDataFrame(med)
med = med.to_crs(4326)
med = med.round({"area_hect":0})
med["area_hect"] = med["area_hect"].replace([0],["< 1"])
med.to_file('med.json', driver='GeoJSON')
med = os.path.join('', 'med.json')



low =  gpd.read_file("D:\\Hasten Ventures\\High Potential\\Low_Potential\\Low_Potential.shp")
low = low.to_crs(4326)
low = low.round({"area_hect":0})
low["area_hect"] = low["area_hect"].replace([0],["< 1"])
low.to_file('low.json', driver='GeoJSON')
low = os.path.join('', 'low.json')



high =  gpd.read_file("D:\\Hasten Ventures\\High Potential\\High_Potential\\High_Potential.shp")
high = high[["geometry","area_hect"]]
high = gpd.GeoDataFrame(high)
high = high.round({"area_hect":0})
high["area_hect"] = high["area_hect"].replace([0],["< 1"])
high.to_file('high.json', driver='GeoJSON')
high = os.path.join('', 'high.json')


m= folium.Map(location=[24.436933515, 80.20336914], zoom_start=8)


tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(m)




loc = 'Land potential and distribution by size'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)   


m.get_root().html.add_child(folium.Element(title_html))



folium.GeoJson(
    _shp_district,
    name='dist_boundary',
    show = False,
    control = False,
        style_function=lambda feature: {
        'fillColor': "none",
        'color' : "black",
        'weight' : 1,
        'fillOpacity' : 0.5,
        },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['AREA'],labels=False, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(m)


# folium.GeoJson(
#     No_potential,
#     name='No potential',
#     show = False,
#         style_function=lambda feature: {
#         'fillColor': "#424242",
#         'color' : "#424242",
#         'weight' : 3,
#         'fillOpacity' : 0.5,
#         },
# #          highlight_function=lambda x: {'weight':5,'color':'yellow'},
# #          tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
#       smooth_factor=2.0
           
#     ).add_to(m)




m.add_child(raster_layers.ImageOverlay(
    image=dataimage3,
    show=False,
    name = 'Unused',
    bounds=[[ymin, xmin], [ymax, xmax]],
    colormap=lambda x: (1-x,1-x, 1-x,0+x*255),#R,G,B,red: (255,0,0)
    interactive=True,
    mercator_project = True,
    opacity=1
))#.add_to(m)


folium.GeoJson(
    theo_only,
    name='Theoritical potential',
    show = False,
        style_function=lambda feature: {
        'fillColor':"#15915C",
        'color' : "#15915C",
        'weight' : 3,
        'fillOpacity' : 1,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
      smooth_factor=2.0
           
    ).add_to(m)



folium.GeoJson(
    lc_tech,
    name='Technical potential',
    show = False,
        style_function=lambda feature: {
        'fillColor':feature['properties']['color'],
        'color' : feature['properties']['color'],
        'weight' : 3,
        'fillOpacity' : 0.5,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect','area_class'],aliases =["Area (hect) :","Class :"],labels=True, toLocaleString=True),
      smooth_factor=2.0
           
    ).add_to(m)



folium.GeoJson(
    low,
    name='Low technical potential',
    show = False,
        style_function=lambda feature: {
        'fillColor': "#21583B",
        'color' : "#21583B",
        'weight' : 3,
        'fillOpacity' : 0.5,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
      smooth_factor=2.0
           
    ).add_to(m)


folium.GeoJson(
     med,
     name='Medium technical potential',
     show = False,
         style_function=lambda feature: {
         'fillColor': "#009541",
         'color' : "#009541",
         'weight' : 3,
         'fillOpacity' : 0.5,
         },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
      smooth_factor=2.0
           
    ).add_to(m)
 


folium.GeoJson(
    high,
    name='High technical potential',
    show = False,
        style_function=lambda feature: {
        'fillColor': "#99CC66",
        'color' : "#99CC66",
        'weight' : 3,
        'fillOpacity' : 0.5,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True),
      smooth_factor=2.0
           
    ).add_to(m)



# m.add_child(folium.ClickForMarker(popup='point added'))
# #m.add_child(folium.LatLngPopup())

# folium.LatLngPopup().add_to(m)
# folium.LayerControl(collapsed = False).add_to(m)




plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(m)

minimap = plugins.MiniMap()
m.add_child(minimap)



# Add drawinf controls
draw = Draw()
draw.add_to(m)
m.add_child(MeasureControl())


folium.LayerControl().add_to(m)

# plugins.Geocoder().add_to(m)


m.save('D:\\Panna\\workdir\\Landsuitability.html')

# %% [markdown]
# ### Top 15 Lands

# %%
top15 = read_df_UT("workdir\\slope_top15.shp")

# %%
top15 = top15.reset_index()

# %%
cluster_dst = read_df_UT("forest\\cluster_dst.shp")

# %%
cluster_dst = cluster_dst.to_crs(32644)

# %%
cluster_dst["area_hect"] = (cluster_dst.geometry.area)/10**4

# %%
cluster_dst = cluster_dst.to_crs(4326)

# %%
top15

# %%
top15.columns

# %%
_shp_district = read_df_UT("forest\\Panna\\panna_dst.shp")
_shp_district.to_file('_shp_district.json', driver='GeoJSON')
_shp_district = os.path.join('', '_shp_district.json')


cluster_dst= cluster_dst.round({"area_hect": 0})
cluster_dst["area_hect"] = cluster_dst["area_hect"].replace([0],["< 1"])
cluster_dst.to_file('cluster_dst.json', driver='GeoJSON')
cluster_dst = os.path.join('', 'cluster_dst.json')


water = gpd.read_file("D:\\Hasten Ventures\\Features\\Water_district\\Water_district.shp")

water= water.round({"area_hect": 0})
water["area_hect"] = water["area_hect"].replace([0],["< 1"])
water.to_file('builtup.json', driver='GeoJSON')
water = os.path.join('', 'builtup.json')



top15.level_0 = top15.level_0 + 1
top15= top15.round({"area_hect": 0,"min": 0,"max":0})
top15["area_hect"] = top15["area_hect"].replace([0],["< 1"])
top15.to_file('top15.json', driver='GeoJSON')
top15 = os.path.join('', 'top15.json')

m= folium.Map(location=[24.436933515, 80.20336914], zoom_start=8)


loc = 'Top 15 lands'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)   


m.get_root().html.add_child(folium.Element(title_html))










tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(m)

folium.GeoJson(
    top15,
     name='Top-15',
    show = False,
        style_function=lambda feature: {
        'fillColor':"#99CC66",
        'color' : "#99CC66",
        'weight' : 3,
        'fillOpacity' : 1,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['level_0','area_hect','min','max','rdmintype','wtmindist','urmindist'],aliases =["Rank :","Area (hect) : ","Slope (Min) : ","Slope (Max) : ","Roadtype : ","Nearest water Bodies (m) : ","Nearest Settlement (m) : "],labels=True, toLocaleString=True)
#       smooth_factor=2.0
           
    ).add_to(m)






folium.GeoJson(
    water,
     name='Water Bodies',
    show = False,
        style_function=lambda feature: {
        'fillColor':"#00B9F2",
        'color' : "#00B9F2",
        'weight' : 3,
        'fillOpacity' : 1,
        },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True)
# #       smooth_factor=2.0
           
    ).add_to(m)

folium.GeoJson(
    cluster_dst,
     name='Settlements',
    show = False,
#     control =False,
        style_function=lambda feature: {
        'fillColor': "#e73429",
        'color' : "#e73429",
        'weight' : 1,
        'fillOpacity' : 1,
        },
         highlight_function=lambda x: {'weight':5,'color':'yellow'},
         tooltip=folium.features.GeoJsonTooltip(fields=['area_hect'],aliases =["Area (hect) :"],labels=True, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(m)


folium.GeoJson(
    _shp_district,
     name='dist_boundary',
    show = False,
    control =False,
        style_function=lambda feature: {
        'fillColor': "none",
        'color' : "black",
        'weight' : 1,
        'fillOpacity' : 0.5,
        },
#          highlight_function=lambda x: {'weight':5,'color':'yellow'},
#          tooltip=folium.features.GeoJsonTooltip(fields=['AREA'],labels=False, toLocaleString=True)
      #smooth_factor=2.0
           
    ).add_to(m)



plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(m)

minimap = plugins.MiniMap()
m.add_child(minimap)



# Add drawinf controls
draw = Draw()
draw.add_to(m)
m.add_child(MeasureControl())


folium.LayerControl().add_to(m)

# plugins.Geocoder().add_to(m)
m.save('D:\\Panna\\workdir\\top15panna.html')

# %%

# %%
