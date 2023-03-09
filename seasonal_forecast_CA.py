# https://medium.com/@lubomirfranko/visualise-seasonal-weather-forecasts-with-python-and-climate-data-store-b200e43371fd
# installing the dependencies :
# conda create -n weather python=3.9 pandas scipy cartopy cdsapi xarray cfgrib
# import stuff
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import cdsapi
from datetime import datetime
import xarray as xr
import os
#import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import cartopy.feature as cf
# delete the old data
os.system("rm download.grib")
# extract the dates

currentMonth = datetime.now().month
if currentMonth < 10:
    currentMonth ="0"+str(currentMonth)
else:
    currentMonth =str(currentMonth)
currentYear = datetime.now().year

# download the new data
c = cdsapi.Client()
c.retrieve(
    'seasonal-postprocessed-single-levels',
    {
        'originating_centre': 'ecmwf',
        'system': '51',
        'variable': 'snow_depth_anomaly',
        'product_type': 'ensemble_mean',
        'year': str(currentYear),
        'month': currentMonth,
        'leadtime_month': [
            '1', '2', '3', '4', '5' ,'6'
        ],
        'format': 'grib',
    },
    'download.grib')

# read the grib data !
ds = xr.open_dataset(
    "download.grib",engine="cfgrib", 
    filter_by_keys={'dataType': 'em'}
    )


# We want forecast for month ahead, we chose first element of our dataset
import pandas as pd


################################################## 
for i in range(6):
    
    first_month = ds["sda"][i]# Create plot and set up basemap
    plt.figure(dpi=250)
    ax = plt.axes(projection=ccrs.Mercator(), frameon=True)# Set coordinate system of data and change extent of a map
    data_crs = ccrs.PlateCarree()
    ax.set_extent([45, 90, 30, 57], crs=data_crs)# Load values and latitude and longitude
    values = first_month.values
    ax.add_feature(cf.COASTLINE.with_scale("50m"), lw=0.5) # Add borderlines
    ax.add_feature(cf.BORDERS.with_scale("50m"), lw=0.3)
    # Add coastlines
    lonsi, latsi = np.meshgrid(first_month["longitude"], first_month["latitude"]) # Create grid from latitude and longitude
    # Plot the data as filled contour
    levels = np.linspace(-.5, .5, 21)
    cs = ax.contourf(lonsi, latsi, values, transform=data_crs, levels=levels, cmap="seismic_r", vmin=-.5, vmax=.5)
    # Get attributes needed for title
    name = first_month.attrs["GRIB_name"]
    units = first_month.attrs["GRIB_units"]
    valid_date = first_month.valid_time.values
    valid_date = pd.to_datetime(valid_date)
    valid_date = valid_date.strftime("%B %Y")
    plt.title(f"{name} ({units}) \n {valid_date}")
    plt.colorbar(cs,orientation="vertical",ax=ax,pad=.01, aspect=50)
    today = datetime.today()
    d4 = today.strftime("%b-%d-%Y")
    plt.savefig("snowdepthanomalies_lead_time_"+str(i+1)+".png",bbox_inches='tight')
    plt.close()




# put everythin on the website
#cmd="scp -i ~/.ssh/id_rsa snowdepthanomalies_lead_time_* website.md.html fallah@cluster.pik-potsdam.de:/home/fallah/www/GREEN_CENTRAL_ASIA/snowdepthforecast/"
##os.system(cmd)
