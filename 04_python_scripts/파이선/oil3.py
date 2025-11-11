import pandas as pd
from qgis.core import *
from qgis.utils import iface
from PyQt5.QtCore import QVariant

def get_region(address):
    sido = address.split()[0]
    # 권역 구분
    regions = {
        '수도권': ['서울', '경기', '인천'],
        '강원권': ['강원'],
        '충청권': ['충북', '충남', '대전', '세종'],
        '전라권': ['전북', '전남', '광주'],
        '경상권': ['경북', '경남', '대구', '부산', '울산'],
        '제주권': ['제주']
    }
    
    for region, sidos in regions.items():
        if sido in sidos:
            return region
    return '기타'

def create_region_layer(df, selected_region):
    # 권역 필터링
    df['권역'] = df['주소'].apply(get_region)
    region_data = df[df['권역'] == selected_region]
    
    print(f"\n=== {selected_region} 알뜰주유소 현황 ===")
    print(f"총 주유소 수: {len(region_data)}개")
    print(f"셀프 주유소: {len(region_data[region_data['셀프여부'] == 'Y'])}개")
    print(f"일반 주유소: {len(region_data[region_data['셀프여부'] == 'N'])}개")
    
    # 벡터 레이어 생성
    vl = QgsVectorLayer("Point?crs=EPSG:4326", f"알뜰주유소_{selected_region}", "memory")
    pr = vl.dataProvider()
    
    # 필드 추가
    pr.addAttributes([
        QgsField("상호", QVariant.String),
        QgsField("주소", QVariant.String),
        QgsField("셀프여부", QVariant.String)
    ])
    vl.updateFields()
    
    features = []
    for idx, row in region_data.iterrows():
        feat = QgsFeature()
        # 임시 좌표 설정 (실제 구현시 geocoding 필요)
        base_coords = {
            '수도권': (126.978, 37.566),
            '강원권': (128.168, 37.555),
            '충청권': (127.384, 36.350),
            '전라권': (126.851, 35.160),
            '경상권': (128.601, 35.871),
            '제주권': (126.498, 33.489)
        }
        
        base_x, base_y = base_coords[selected_region]
        point = QgsPointXY(base_x + idx*0.005, base_y + idx*0.005)
        feat.setGeometry(QgsGeometry.fromPointXY(point))
        feat.setAttributes([
            row['상호'],
            row['주소'],
            '셀프' if row['셀프여부'] == 'Y' else '일반'
        ])
        features.append(feat)
    
    # 피처 추가
    pr.addFeatures(features)
    vl.updateExtents()
    
    # 심볼 설정
    categories = []
    
    # 셀프 주유소 심볼
    symbol_self = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'color': 'blue',
        'size': '3',
    })
    categories.append(QgsRendererCategory('셀프', symbol_self, '셀프주유소'))
    
    # 일반 주유소 심볼
    symbol_normal = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'color': 'red',
        'size': '3',
    })
    categories.append(QgsRendererCategory('일반', symbol_normal, '일반주유소'))
    
    # 렌더러 설정
    renderer = QgsCategorizedSymbolRenderer('셀프여부', categories)
    vl.setRenderer(renderer)
    
    # 레이어 추가
    QgsProject.instance().addMapLayer(vl)
    iface.setActiveLayer(vl)
    iface.zoomToActiveLayer()

# 메인 실행
csv_file = "C:/Users/TJ/Downloads/20231231.csv"
df = pd.read_csv(csv_file, encoding='euc-kr')
df.columns = ['상호', '주소', '유형', '셀프여부']

# 권역별로 레이어 생성
selected_region = '수도권'  # 여기서 원하는 권역으로 변경 가능
create_region_layer(df, selected_region)