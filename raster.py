# %% [markdown] noqa: D212, D400, D415
"""
## Raster data

Example notebook to show an introduction to raster data.

### Data Sources

Example raster files have been downloaded from the [Global Human Settlement
Layer, European Commision.](https://ghsl.jrc.ec.europa.eu/download.php)

In this example we are using the GHS-POP 2020 dataset, 1 km Mollweide
projection. The dataset contains population values in a 1km x 1km grid.
"""

# %%
# imports
import os

import rasterio as rio
import geopandas as gpd
import matplotlib.pyplot as plt

from rasterio.mask import raster_geometry_mask
from shapely import box
from pyprojroot import here

# %% [markdown] noqa: D212, D400, D415
"""
A raster file consists of a matrix of cells. Each cell contains a value
representing some information. A file may contain several layers, each
representing different information.

A Python package useful to process raster files is called rasterio.
"""

# %%
# read raster file
path = here("data")
dataset = rio.open(
    os.path.join(path, "GHS_POP_E2020_GLOBE_R2023A_54009_1000_V1_0_R3_C18.tif")
)

# %% [markdown] noqa: D212, D400, D415
"""
When reading a raster file, it is possible to access some of its attributes,
such as CRS, number of layers, size and boundaries.
<br>
<br>
An important attribute is the affine transformation matrix.
A simple transform could have the following format:
\begin{bmatrix} a \ b \ c \\\ d \ e \ f \end{bmatrix}
<br>
<br>
This matrix serves to map every pixel in its relative position in the matrix
(row, col) to spatial positions (x, y or lat, lon). `c` and `f` are the
coordinates of the top left corner of the dataset. `a` is the value you'd
need to add to `c` to move it one step to the right. `e` is the value you'd
need to add to `f` to move it one step down. Using this, it is possible
to trim, reproject or resample a raster. More details can be found in
[this link](https://pygis.io/docs/d_affine.html).
<br>
<br>
In the example below, CRS is `ESRI: 54009`, so the numbers represent
metres. The dataset has one layer, with width 1000 and height 1000.
The transform indicates that every cell moves 1000 m to the right and
1000 m down, so we can conclude that every cell is 1000x1000 m.

"""  # noqa: W605
# %%
# properties
print(f"Number of layers: {dataset.count}")
print(f"Number of columns: {dataset.width}")
print(f"Number of rows: {dataset.height}")

# geometry information
print(f"CRS: {dataset.crs}")
print(f"Affine transform:\n{dataset.transform}")
print(f"Boundaries: {dataset.bounds}")

# %% [markdown] noqa: D212, D400, D415
"""
To be able to plot the contents of the raster, we first need to read a specific
layer. In our case, we only have one. We use the `.read` method, indicating
the number of the layer we want to read.
<br>
<br>
Inspecting the band after reading, we can see it's a simple numpy array.
This data is supposed to contain population values on each cell, but you
might notice some values are negative. A raster layer can only contain data
of a single type, so if the data contained is numerical null values need to
be represented as numbers too. In this case, the number that indicates a
null value is `-200`. You can examine this value by accessing the raster
attribute `nodata`.
<br>
<br>
If we want to plot its contents, we can use matplotlib `imshow` function.

"""
# %%
band = dataset.read(1)
print(band)
print(type(band))

plt.imshow(band)

# %%
# %% [markdown] noqa: D212, D400, D415
"""
It is also possible to read a specific chunk of a band (e.g. whatever falls
within a specific bounding box).
<br>
<br>
To do this, we can use the method `raster_geometry_mask`, which will return
a mask array with values False in the positions that fall within the limits,
or True otherwise. If giving the argument `crop=True`, it will return only
the cells within the box, and a `Window` object with the col and row limits
of the crop provided. We can use this window as an argument when reading a
layer.

"""
# bbox around the Bristol channel
bbox = [-3.6955, 51.1869, -2.3002, 51.9855]
bbox_gdf = gpd.GeoDataFrame(geometry=[box(*bbox)], crs="EPSG: 4326").to_crs(
    "ESRI: 54009"
)

_, aff, window = raster_geometry_mask(
    dataset, bbox_gdf.geometry.values, crop=True, all_touched=True
)

band_cropped = dataset.read(1, window=window)
plt.imshow(band_cropped)

# %%
