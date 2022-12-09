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
import geopandas as gpd
import pandas as pd
import numpy as np
from osgeo import gdal


# %%
def get_rooted(stem):
    return "D:\\LiLa_Nagapattinam\\" + stem
def read_df_UT(stem):
    return gpd.read_file(get_rooted(stem)).to_crs(epsg = 4326)


# %% [markdown]
# ### define func for creating Area_acres and area_class

# %% [markdown]
# #### change the values of range according to the critreria

# %%
def area_acres(df):
    crs_utm = 32644 
    df = df.to_crs(crs_utm)
    df["area_acres"] = (((df.geometry.area)/10**6)*247.105)
    a = df["area_acres"].max()
    def area_class(df):
        if 5<= df["area_acres"] < 20:
            return "A"
        elif 20<= df["area_acres"] < 100:
            return "B"
        elif 100<= df["area_acres"] <= a:
            return "C"  
        else:
            return "D"
    df["area_class"] =df.apply(area_class, axis=1)
    df = df.to_crs(4326)
    print("Total area: ",df.area_acres.sum())
    return df[["area_acres","area_class","geometry"]]


# %% [markdown]
# ### define func for creating Area_hect and area_class

# %%
def area_hect(df):
    crs_utm = 32644 
    df = df.to_crs(crs_utm)
    df["area_hect"] = ((df.geometry.area)/10**4)
    a = df["area_hect"].max()
    def area_class(df):
        if 5 <= df["area_hect"] < 20:
            return "A"
        elif 20<= df["area_hect"] < 100:
            return "B"
        elif 100<= df["area_hect"] <= a:
            return "C"  
        else:
            return "D"
    df["area_class"] =df.apply(area_class, axis=1)
    df = df.to_crs(4326)
    print(df.area_hect.sum())
    return df[["area_hect","area_class","geometry"]]


# %% [markdown]
# ### define func for the difference and intersection between shape files

# %%
def intersection(df,df1,dist):
    df = gpd.overlay(dist,df,how ="intersection")
    df1 = gpd.overlay(dist,df1,how ="intersection")
    df2 = gpd.overlay(df,df1,how ="intersection")
    return df2   


# %% [markdown]
# ### def fun for Calculating overlap area

# %%
def find_overlap_area(df,tag,fdf2):
    crs_utm = 32644    
    df = df.to_crs(crs_utm)
    df1 = pd.DataFrame(columns = ['olap%'+tag,'olaparea'+tag])
    df1['olap%'+tag]=df1['olap%'+tag].astype('object')
    df1['olaparea'+tag]=df1['olaparea'+tag].astype('object')
    
    fdf2=fdf2.to_crs(crs_utm)
    #set spatial index for data for faster processing
    sindex = fdf2.sindex
    for i in range(len(df)):
        geometry = df.iloc[i]['geometry']
        fids = list(sindex.intersection(geometry.bounds))
        if fids:
            olaparea = ((fdf2.iloc[fids]['geometry'].intersection(geometry)).area).sum()
            olap_perc = olaparea*100/geometry.area
            olaparea = (olaparea/10**6)*247.1               
        else:
            olaparea = 0
            olap_perc = 0
        df1.at[i,'olap%'+tag] =  olap_perc      
        df1.at[i,'olaparea'+tag] = olaparea
    return pd.concat([df,df1], axis= 1)
