import os
import time
import requests
import folium
from pyproj import CRS, Transformer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from PIL import Image
import random

# 상수 정의
API_KEY = 'F241130499'
BASE_URL = "http://www.opinet.co.kr/api/lowTop10.do"
DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
WEBDRIVER_PATH = "C:/Users/TJ/.wdm/drivers/chromedriver/win64/131.0.6778.85/chromedriver-win32/chromedriver.exe"
WEBDRIVER_SERVICE = Service(WEBDRIVER_PATH)

def convert_utm_to_wgs84(utm_x, utm_y):
    """
    KATEC/UTM-K 좌표를 WGS84 위경도로 변환
    """
    try:
        print(f"좌표 변환 시작 - X: {utm_x}, Y: {utm_y}")
        
        # KATEC 좌표계 정의
        katec_proj = CRS.from_proj4(
            "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 +ellps=bessel "
            "+units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43"
        )
        
        # WGS84 좌표계
        wgs84_proj = CRS.from_epsg(4326)
        
        # 변환기 생성
        transformer = Transformer.from_crs(katec_proj, wgs84_proj, always_xy=True)
        
        # 좌표 변환
        lon, lat = transformer.transform(float(utm_x), float(utm_y))
        
        print(f"변환된 좌표 - 위도: {lat}, 경도: {lon}")
        
        return lat, lon
        
    except Exception as e:
        print(f"좌표 변환 중 오류 발생: {str(e)}")
        raise

def save_html_as_image(html_path, station_name):
    """HTML 지도를 이미지로 변환"""
    driver = None
    try:
        file_base = os.path.splitext(os.path.basename(html_path))[0]
        temp_path = os.path.join(DOWNLOAD_PATH, f'temp_{file_base}.png')
        print(f"\n=== HTML 지도 이미지 변환 시작 ===")
        print(f"HTML 파일: {html_path}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--force-device-scale-factor=2')
        
        driver = webdriver.Chrome(service=WEBDRIVER_SERVICE, options=options)
        driver.set_window_size(1920, 1080)
        
        # HTML 파일 로드
        driver.get(f'file:///{os.path.abspath(html_path)}')
        print("HTML 파일 로드 완료")
        
        # 지도 로딩 대기
        time.sleep(5)  # 지도 타일이 완전히 로드될 때까지 대기
        
        # 이미지 파일 경로
        safe_name = ''.join(c for c in station_name if c.isalnum())
        temp_path = os.path.join(DOWNLOAD_PATH, f'temp_{safe_name}_map.png')
        final_path = os.path.join(DOWNLOAD_PATH, f'GasStation_{safe_name}_image.jpg')
        
        print("스크린샷 캡처 중...")
        driver.save_screenshot(temp_path)
        
        if os.path.exists(temp_path):
            print("이미지 처리 중...")
            image = Image.open(temp_path)
            
            # 이미지 크롭 (지도 영역만 남기기)
            width, height = image.size
            left = 0
            top = 0
            right = width
            bottom = height - 30  # 하단 속성 표시줄 제거
            
            image = image.crop((left, top, right, bottom))
            image.save(final_path, 'JPEG', quality=95)
            os.remove(temp_path)
            
            print(f"최종 이미지 저장 완료: {final_path}")
            return final_path
            
    except Exception as e:
        print(f"이미지 변환 중 오류 발생: {str(e)}")
        return None
    
    finally:
        if driver:
            driver.quit()

def create_focused_map(lat, lon, station_name, address):
    """반경 1.6km가 보이도록 지도 생성 (Hastings 2004 기준)"""
    try:
        # 파일명 생성
        safe_name = ''.join(c for c in station_name if c.isalnum() or c.isspace())
        safe_name = safe_name.replace(' ', '_')
        file_base = f'GasStation_{safe_name}'
        html_file = os.path.join(DOWNLOAD_PATH, f'{file_base}.html')

        # 지도 생성
        map_ = folium.Map(
            location=[lat, lon],
            zoom_start=15,  # 1.6km 반경이 잘 보이는 줌 레벨
            tiles='OpenStreetMap'
        )

        # 주유소 마커
        popup_content = f"""
            <div style='font-size: 14px'>
                <b>{station_name}</b><br>
                주소: {address}
            </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=station_name,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(map_)

        # 1.6km 반경을 표시하기 위한 Circle 추가
        folium.Circle(
            location=[lat, lon],
            radius=1600,  # 1.6km = 1600m
            color='blue',
            fill=True,
            fill_opacity=0.1,
            popup='경쟁 범위 (1.6km)'
        ).add_to(map_)

        # 맵 경계 자동 조정 (1.6km 반경이 잘 보이도록)
        bounds = [
            [lat - 0.01, lon - 0.01],  # 약 1.6km 반경에 맞춤
            [lat + 0.01, lon + 0.01]
        ]
        map_.fit_bounds(bounds)

        # 지도 저장
        map_.save(html_file)
        
        # HTML을 이미지로 변환
        image_path = save_html_as_image(html_file, station_name)
        if image_path:
            final_image_path = os.path.join(DOWNLOAD_PATH, f'{file_base}_map.jpg')
            os.rename(image_path, final_image_path)
            return html_file, final_image_path

        return html_file, None

    except Exception as e:
        print(f"지도 생성 중 오류 발생: {str(e)}")
        return None, None
def is_economical_station(station):
    """주유소가 알뜰주유소인지 확인"""
    try:
        # 정유사 구분 코드로 확인
        poll_div_cd = station.get('POLL_DIV_CD', '')
        van_co_cd = station.get('VAN_CO_CD', '')
        station_name = station.get('OS_NM', '')
        
        # 알뜰주유소 코드 목록
        economical_codes = {
            'POLL_DIV_CD': ['SKE', 'GSC', 'HDO', 'SOL', 'RTO', 'RTX', 'NHO'],
            'VAN_CO_CD': ['SK', 'GS', 'HD', 'SO', 'NH', 'RT']
        }
        
        # 확인 조건
        is_eco_by_code = (poll_div_cd in economical_codes['POLL_DIV_CD'] or 
                         van_co_cd in economical_codes['VAN_CO_CD'])
        is_eco_by_name = '알뜰' in station_name
        
        return is_eco_by_code or is_eco_by_name
        
    except Exception as e:
        print(f"알뜰주유소 확인 중 오류: {str(e)}")
        return False

def fetch_gas_station_data(api_key):
    """알뜰주유소 데이터 조회"""
    try:
        all_stations = []
        
        # 지역별 조회를 위한 시도 코드
        area_codes = {
            '01': '서울', '02': '경기', '03': '인천', '04': '강원',
            '05': '충북', '06': '충남', '07': '대전', '08': '경북',
            '09': '경남', '10': '부산', '11': '울산', '12': '대구',
            '13': '전북', '14': '전남', '15': '광주', '16': '제주'
        }
        
        # 제품 코드 목록
        product_codes = ['B027', 'D047', 'E019', 'F027', 'C004', 'C003', 'B034']
        
        print("=== 알뜰주유소 데이터 조회 중 ===")
        
        # 각 지역별, 제품별로 조회
        for area_code, area_name in area_codes.items():
            area_stations = []
            for prodcd in product_codes:
                params = {
                    'code': api_key,
                    'out': 'json',
                    'area': area_code,
                    'prodcd': prodcd
                }
                
                try:
                    response = requests.get(BASE_URL, params=params)
                    data = response.json()
                    
                    if 'RESULT' in data and 'OIL' in data['RESULT']:
                        stations = data['RESULT']['OIL']
                        eco_stations = [station for station in stations if is_economical_station(station)]
                        area_stations.extend(eco_stations)
                except Exception as e:
                    continue
            
            if area_stations:
                all_stations.extend(area_stations)
        
        # 중복 제거 (UNI_ID 기준)
        unique_stations = list({station['UNI_ID']: station for station in all_stations}.values())
        return unique_stations
        
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {str(e)}")
        return None

def process_station(station):
    """개별 주유소 처리 및 이미지 생성"""
    try:
        # 좌표 변환
        utm_x = float(station["GIS_X_COOR"])
        utm_y = float(station["GIS_Y_COOR"])
        lat, lon = convert_utm_to_wgs84(utm_x, utm_y)
        
        station_name = station["OS_NM"]
        address = station.get("NEW_ADR", station.get("VAN_ADR", "주소 없음"))
        
        print(f"\n=== 주유소 정보 ===")
        print(f"이름: {station_name}")
        print(f"주소: {address}")
        
        # 지도 생성
        html_file, image_file = create_focused_map(lat, lon, station_name, address)
        
        if image_file:
            print(f"이미지 생성 완료: {image_file}")
            return True
        else:
            print("이미지 생성 실패")
            return False
            
    except Exception as e:
        print(f"주유소 처리 중 오류 발생: {str(e)}")
        return False

def main():
    """메인 함수"""
    try:
        print("=== 주유소 이미지 생성 프로그램 시작 ===")
        
        # 알뜰주유소 데이터 조회
        stations = fetch_gas_station_data(API_KEY)
        
        if not stations:
            print("주유소 정보가 없습니다.")
            return
        
        # 무작위 선택을 위한 가중치 부여
        weighted_stations = []
        for station in stations:
            # 수도권 지역은 약간 낮은 가중치 (지역 다양성)
            addr = station.get('NEW_ADR', station.get('VAN_ADR', ''))
            weight = 0.8 if any(region in addr for region in ['서울', '경기', '인천']) else 1.0
            weighted_stations.extend([station] * int(weight * 10))
        
        # 성공할 때까지 시도
        success = False
        tried_stations = set()
        
        while not success and len(tried_stations) < len(stations):
            random_station = random.choice(weighted_stations)
            station_id = random_station['UNI_ID']
            
            if station_id not in tried_stations:
                tried_stations.add(station_id)
                success = process_station(random_station)
        
        if not success:
            print("이미지 생성에 실패했습니다.")
        
    except Exception as e:
        print(f"\n프로그램 실행 중 오류 발생: {str(e)}")
        import traceback
        print("\n상세 오류 정보:")
        print(traceback.format_exc())
    finally:
        print("\n=== 프로그램 종료 ===")

if __name__ == "__main__":
    main()
