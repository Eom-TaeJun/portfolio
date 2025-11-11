import os
import time
import requests
import folium
from pyproj import Proj, transform
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
import random

# Set up the path to the WebDriver directly
webdriver_path = "C:/Users/TJ/.wdm/drivers/chromedriver/win64/131.0.6778.85/chromedriver-win32/chromedriver.exe"
webdriver_service = Service(webdriver_path)

# Set download path
DOWNLOAD_PATH = "C:\\Users\\TJ\\Downloads"

def get_nearby_gas_stations(api_key, x_coord, y_coord, radius_meters=1600, outer_radius_meters=3200):
    base_url = "http://www.opinet.co.kr/api/aroundAll.do"
    
    params = {
        'code': api_key,
        'x': str(x_coord),
        'y': str(y_coord),
        'radius': str(radius_meters),
        'sort': 1,
        'out': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if 'RESULT' not in data:
            raise Exception(f"API 응답 형식 오류: {response.text}")
            
        inner_stations = data['RESULT']['OIL']
        
        params['radius'] = str(outer_radius_meters)
        response = requests.get(base_url, params=params)
        data = response.json()
        outer_stations = data['RESULT']['OIL']
        
        inner_valid_prices = [float(station['PRICE']) for station in inner_stations if float(station.get('PRICE', 0)) > 0]
        outer_valid_prices = [float(station['PRICE']) for station in outer_stations if float(station.get('PRICE', 0)) > 0]
        
        return {
            'inner_stations': inner_stations,
            'outer_stations': outer_stations,
            'inner_station_count': len(inner_stations),
            'inner_valid_station_count': len(inner_valid_prices),
            'inner_avg_price': sum(inner_valid_prices) / len(inner_valid_prices) if inner_valid_prices else None,
            'outer_station_count': len(outer_stations),
            'outer_valid_station_count': len(outer_valid_prices),
            'outer_avg_price': sum(outer_valid_prices) / len(outer_valid_prices) if outer_valid_prices else None,
            'success': True,
            'message': '정상적으로 조회되었습니다.'
        }
        
    except Exception as e:
        return {'success': False, 'message': f'처리 중 오류 발생: {str(e)}'}

def create_map(lat, lon, name, address, nearby_stations=None):
    try:
        lat = float(lat)
        lon = float(lon)

        map_ = folium.Map(
            location=[lat, lon],
            zoom_start=14,
            control_scale=True
        )

        folium.TileLayer(
            tiles='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        ).add_to(map_)

        folium.LayerControl().add_to(map_)

        popup_content = f"<b>{name}</b><br>{address}"
        folium.Marker(
            [lat, lon],
            popup=popup_content,
            tooltip=name,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(map_)

        folium.Circle(
            location=[lat, lon],
            radius=3000,
            color='red',
            fill=True,
            fill_opacity=0.2
        ).add_to(map_)

        if nearby_stations:
            for station in nearby_stations:
                try:
                    station_lat = float(station.get('GIS_Y_COOR', 0))
                    station_lon = float(station.get('GIS_X_COOR', 0))
                    station_name = station.get('OS_NM', 'Unknown')
                    station_price = station.get('PRICE', 'N/A')
                    
                    folium.Marker(
                        [station_lat, station_lon],
                        popup=f"<b>{station_name}</b><br>가격: {station_price}원",
                        tooltip=station_name,
                        icon=folium.Icon(color='blue', icon='info-sign')
                    ).add_to(map_)
                except:
                    continue

        safe_name = ''.join(c for c in name if c.isalnum())
        html_file = os.path.join(DOWNLOAD_PATH, f'NH_GasStation_{safe_name}.html')
        map_.save(html_file)

        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1280,800')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(service=webdriver_service, options=options)
        driver.set_window_size(1280, 800)
        
        driver.get('file:///' + os.path.abspath(html_file))
        time.sleep(5)

        screenshot_path = os.path.join(DOWNLOAD_PATH, f'NH_GasStation_{safe_name}.png')
        driver.save_screenshot(screenshot_path)
        driver.quit()

        image = Image.open(screenshot_path)
        jpeg_path = os.path.join(DOWNLOAD_PATH, f'NH_GasStation_{safe_name}.jpg')
        image.convert('RGB').save(jpeg_path, 'JPEG', quality=95)
        
        os.remove(html_file)
        os.remove(screenshot_path)

        print(f"이미지가 저장된 경로: {jpeg_path}")
        return jpeg_path

    except Exception as e:
        print(f"지도 생성 중 오류 발생 ({name}): {str(e)}")
        return None

def analyze_nearby_stations(api_key, station):
    station_name = station['OS_NM']
    station_addr = station.get('NEW_ADR', station.get('VAN_ADR', '주소 없음'))
    lat = station.get('GIS_Y_COOR')
    lon = station.get('GIS_X_COOR')

    print(f"\n=== {station_name} 주변 주유소 분석 ===")
    print(f"주소: {station_addr}")
    print(f"위도: {lat}, 경도: {lon}")
    
    result = get_nearby_gas_stations(
        api_key, 
        lon, 
        lat
    )
    
    if result['success']:
        if result['inner_station_count'] == 0:
            print("반경 1마일 내에 주유소가 없습니다.")
        else:
            print(f"\n반경 1마일 내 분석 결과:")
            print(f"총 주유소 수: {result['inner_station_count']}개")
            print(f"유효 가격 주유소: {result['inner_valid_station_count']}개")
            if result['inner_avg_price']:
                print(f"평균 가격: {result['inner_avg_price']:,.0f}원")
            else:
                print("평균 가격: 정보 없음")
        
        if result['outer_station_count'] == 0:
            print("반경 1~2마일 내에 주유소가 없습니다.")
        else:
            print(f"\n반경 1~2마일 사이 분석 결과:")
            print(f"총 주유소 수: {result['outer_station_count']}개")
            print(f"유효 가격 주유소: {result['outer_valid_station_count']}개")
            if result['outer_avg_price']:
                print(f"평균 가격: {result['outer_avg_price']:,.0f}원")
            else:
                print("평균 가격: 정보 없음")
        
        if result['inner_avg_price'] and result['outer_avg_price']:
            avg_price_diff = result['inner_avg_price'] - result['outer_avg_price']
            print(f"\n1마일 이내와 1~2마일 사이의 평균 가격 차이: {avg_price_diff:,.0f}원")
        
        img_path = create_map(lat, lon, station_name, station_addr, result['inner_stations'] + result['outer_stations'])
        if img_path:
            print(f"지도 이미지가 성공적으로 생성되었습니다: {img_path}")
        
    else:
        print(f"분석 실패: {result['message']}")

# API 키 설정
api_key = 'F241130499'
base_url = "http://www.opinet.co.kr/api/lowTop10.do"

# UTM 좌표를 WGS84로 변환하는 함수
def convert_utm_to_wgs84(utm_x, utm_y, zone=52):
    utm_proj = Proj(proj="utm", zone=zone, ellps="WGS84")  # UTM 좌표계 (zone: 한국에 맞는 값)
    wgs84_proj = Proj(proj="latlong", datum="WGS84")  # WGS84 좌표계
    lon, lat = transform(utm_proj, wgs84_proj, utm_x, utm_y)
    return lat, lon

# 지도 생성 함수
def create_map(lat, lon, station_name, save_path):
    # 지도 객체 생성
    map_ = folium.Map(location=[lat, lon], zoom_start=14, control_scale=True, tiles='Stamen Terrain')
    
    # 마커 추가
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(f"{station_name} ({lat}, {lon})", max_width=300),
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(map_)
    
    # 지도 저장
    map_.save(save_path)
    print(f"지도 이미지가 성공적으로 생성되었습니다: {save_path}")

# 주유소 데이터 가져오기
def fetch_gas_station_data(api_key):
    try:
        params = {
            'code': api_key,
            'prodcd': 'B027',  # 'prodcd' 값을 확인하세요.
            'out': 'json'
        }
        
        response = requests.get(base_url, params=params)
        print(f"API 응답 상태 코드: {response.status_code}")
        print(f"API 응답 내용: {response.text[:200]}...")  # 응답 내용 일부 출력
        
        return response.json()
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")
        return None

# 주유소 분석 및 지도 생성
def analyze_nearby_stations(api_key, station):
    # UTM 좌표로부터 위도, 경도 변환
    utm_x = float(station["LAT"])  # UTM 좌표 x (예시)
    utm_y = float(station["LON"])  # UTM 좌표 y (예시)
    lat, lon = convert_utm_to_wgs84(utm_x, utm_y)
    
    # 주유소 정보 출력
    station_name = station["OS_NM"]
    address = station["VAN_ADR"]  # 주소 정보
    price = station["PRICE"]  # 가격 정보
    print(f"주유소: {station_name}, 주소: {address}, 가격: {price}원")
    print(f"위도: {lat}, 경도: {lon}")
    
    # 지도 이미지 생성 및 저장
    save_path = f"C:/Users/TJ/Downloads/NH_GasStation_{station_name}.html"
    create_map(lat, lon, station_name, save_path)

# 메인 함수
def main():
    api_key = 'F241130499'  # 제공된 API 키
    
    try:
        # API에서 주유소 데이터 가져오기
        data = fetch_gas_station_data(api_key)
        
        if not data or "RESULT" not in data or "OIL" not in data["RESULT"]:
            print("주유소 정보가 없습니다.")
            return
        
        stations = data['RESULT']['OIL']
        
        print(f"\n전체 {len(stations)}개의 알뜰주유소를 찾았습니다.")
        
        # 무작위로 주유소 선택
        random_station = random.choice(stations)
        
        # 선택된 주유소에 대해 분석
        analyze_nearby_stations(api_key, random_station)
        
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")

# 프로그램 시작
if __name__ == "__main__":
    main()
