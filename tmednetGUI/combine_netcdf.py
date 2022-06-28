import netCDF4
import numpy
import xarray

ds = xarray.open_mfdataset('/home/marcjou/sat_data/2022/*.nc',combine = 'by_coords')

ds.to_netcdf('sat_combined.nc')