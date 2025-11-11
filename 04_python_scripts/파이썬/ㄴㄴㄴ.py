import ee
ee.Initialize()

# 예시: 특정 지역에 대한 Landsat 이미지를 불러오기
image = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA') \
    .filterBounds(ee.Geometry.Point([longitude, latitude])) \
    .filterDate('2020-01-01', '2020-12-31') \
    .median()

# 이미지를 시각화
import folium
my_map = folium.Map(location=[latitude, longitude], zoom_start=10)
folium.TileLayer(tiles=image.getMapId(), attr="Google Earth Engine").add_to(my_map)
my_map
