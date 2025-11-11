import requests
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsProject, QgsField
from PyQt5.QtCore import QVariant

# API 호출 정보
url = "http://api.vworld.kr/req/search"
params = {
    'service': 'search',
    'request': 'search',
    'version': '2.0',
    'crs': 'EPSG:4326',
    'size': '100',
    'page': '1',
    'query': '알뜰',
    'type': 'place',
    'format': 'json',
    'key': '9178F15A-B959-392E-9997-FF025928BD6B'
}

# API 호출
response = requests.get(url, params=params)
data = response.json()

# 메모리 레이어 생성
layer = QgsVectorLayer("Point?crs=EPSG:4326", "알뜰주유소1", "memory")
provider = layer.dataProvider()

# 필드 추가
provider.addAttributes([
    QgsField("이름", QVariant.String),
    QgsField("주소", QVariant.String),
    QgsField("전화번호", QVariant.String)
])
layer.updateFields()

# 데이터 추가
if 'response' in data and 'result' in data['response'] and 'items' in data['response']['result']:
    for item in data['response']['result']['items']:
        feature = QgsFeature()
        point = QgsPointXY(float(item['point']['x']), float(item['point']['y']))
        feature.setGeometry(QgsGeometry.fromPointXY(point))
        feature.setAttributes([
            item['title'],
            item['address']['road'],
            item.get('tel', '')
        ])
        provider.addFeature(feature)

# 레이어 추가
QgsProject.instance().addMapLayer(layer)
layer.updateExtents()