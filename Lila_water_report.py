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
import Input_template 
from Input_template import area_acres, find_overlap_area, merge, area_class_total,top15


# %%
def get_rooted(stem):
    return "D:\\LiLa_Nagapattinam\\" + stem
def read_df_UT(stem):
    return gpd.read_file(get_rooted(stem)).to_crs(epsg = 4326)


# %% [markdown]
# ### Importing Required Shape files

# %%
shp_water_high =read_df_UT("water\\_wd_run_high\\LC_Water_final.shp")
shp_water_med =read_df_UT("water\\_wd_run_med\\LC_Water_final.shp")
shp_water_low = read_df_UT("water\\_wd_run_low\\LC_Water_final.shp")
_shp_district = read_df_UT("Practice\\Nagapattinam_proj32644.shp")
lc_theo_water = read_df_UT("solar\\all_lands_barren\\all_BarrenLands_Mayu.shp") ##all barren lands

# %%
forest_med = read_df_UT("forest\\_ter_elev_watpot_ar_med\\LC_Forest_final_area_mask_1_Nagapattinam.shp")

# %% [markdown]
# ### Technical Potential 

# %%
lc_tech_water = gpd.pd.concat([shp_water_high,shp_water_med,shp_water_low])

# %%
print(shp_water_high.columns.to_list())

# %% [markdown]
# ### Calculating the Total area

# %%
shp_water_high =area_acres(shp_water_high)
shp_water_med =area_acres(shp_water_med)
shp_water_low = area_acres(shp_water_low)

# %%
lc_tech_water= area_acres(lc_tech_water)

# %%
lc_theo_water = area_acres(lc_theo_water)

# %%
lc_tech_water.columns

# %%
area_class_total(lc_tech_water)

# %%
area_class_total(lc_theo_water)

# %%
area_class_total(shp_water_high)

# %%
area_class_total(shp_water_low)

# %% [markdown]
# ### Top 15 calculation

# %%
top15 = top15(shp_water_high,shp_water_med)

# %%
find_overlap_area(top15,"forest",lc_tech_water)

# %%
