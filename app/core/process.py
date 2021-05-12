import datacube
from shapely import speedups

speedups.disable()

dc = datacube.Datacube(config="datacube.conf")
datasets = dc.index.datasets.search(lat=40)

for dataset in datasets:
    print(dataset)

# products = dc.index.products.get_all()
# data = dc.load(product=next(products))
# print(data)


ds = dc.load(product="ls8_level1_usgs", measurements=["blue"],
             time=("2021-01-01", "2021-12-31"), output_crs='EPSG:4326', resolution=(1, 1)
)
print(ds['blue'])

