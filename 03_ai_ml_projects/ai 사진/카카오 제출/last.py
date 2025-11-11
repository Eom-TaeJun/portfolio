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
        
        # 좌표 범위 확인
        if not (33 <= lat <= 43) or not (124 <= lon <= 132):
            print("경고: 변환된 좌표가 한국 영역을 벗어났습니다!")
            
        return lat, lon
        
    except Exception as e:
        print(f"좌표 변환 중 오류 발생: {str(e)}")
        import traceback
        print("상세 오류 정보:")
        print(traceback.format_exc())
        raise

def get_nearby_gas_stations(api_key, x_coord, y_coord, radius_meters=1600, outer_radius_meters=3200):
    """주변 주유소 정보 조회"""
    base_url = "http://www.opinet.co.kr/api/aroundAll.do"
    
    try:
        # 입력 좌표의 좌표계를 WGS84에서 KATEC으로 변환
        katec_proj = CRS.from_proj4(
            "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 +ellps=bessel "
            "+units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43"
        )
        wgs84_proj = CRS.from_epsg(4326)
        transformer = Transformer.from_crs(wgs84_proj, katec_proj, always_xy=True)
        
        search_x, search_y = transformer.transform(float(x_coord), float(y_coord))
        
        params = {
            'code': api_key,
            'x': str(search_x),
            'y': str(search_y),
            'radius': str(radius_meters),
            'sort': 1,
            'out': 'json'
        }
        
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

def save_html_as_image(html_path, station_name):
    """HTML 지도를 이미지로 변환"""
    driver = None
    try:
        file_base = os.path.splitext(os.path.basename(html_path))[0]
        temp_path = os.path.join(DOWNLOAD_PATH, f'temp_{file_base}.png')
        final_path = os.path.join(DOWNLOAD_PATH, f'{file_base}_map.jpg')
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
        final_path = os.path.join(DOWNLOAD_PATH, f'NH_GasStation_{safe_name}_satellite.jpg')
        
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
def create_map(lat, lon, station_name, address, nearby_stations=None):
    """지도 생성"""
    try:
        # 파일명 생성
        safe_name = ''.join(c for c in station_name if c.isalnum() or c.isspace())
        safe_name = safe_name.replace(' ', '_')
        file_base = f'NH_GasStation_{safe_name}'
        html_file = os.path.join(DOWNLOAD_PATH, f'{file_base}.html')

        # 지도 생성
        map_ = folium.Map(
            location=[lat, lon],
            zoom_start=14,
            tiles='OpenStreetMap'
        )

        # 기준 주유소 마커
        popup_content = f"""
            <div style='font-size: 14px'>
                <b>[기준 알뜰주유소]</b><br>
                <b>{station_name}</b><br>
                주소: {address}
            </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"[기준] {station_name}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(map_)

        # 반경 표시
        folium.Circle(
            location=[lat, lon],
            radius=1600,
            color='red',
            fill=True,
            fill_opacity=0.1,
            popup='1마일 반경'
        ).add_to(map_)

        folium.Circle(
            location=[lat, lon],
            radius=3200,
            color='blue',
            fill=True,
            fill_opacity=0.1,
            popup='2마일 반경'
        ).add_to(map_)

        # 주변 주유소 마커 추가
        if nearby_stations:
            for station in nearby_stations:
                try:
                    station_lat, station_lon = convert_utm_to_wgs84(
                        float(station.get('GIS_X_COOR', 0)),
                        float(station.get('GIS_Y_COOR', 0))
                    )
                    
                    station_name = station.get('OS_NM', 'Unknown')
                    station_price = station.get('PRICE', 'N/A')
                    station_addr = station.get('NEW_ADR', station.get('VAN_ADR', '주소 없음'))
                    
                    popup_content = f"""
                        <div style='font-size: 12px'>
                            <b>{station_name}</b><br>
                            주소: {station_addr}<br>
                            가격: {station_price}원
                        </div>
                    """
                    
                    folium.Marker(
                        location=[station_lat, station_lon],
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=f"{station_name} ({station_price}원)",
                        icon=folium.Icon(color='blue', icon='info-sign')
                    ).add_to(map_)
                    
                except Exception as e:
                    continue

        # 맵 경계 자동 조정
        bounds = [
            [lat - 0.02, lon - 0.02],
            [lat + 0.02, lon + 0.02]
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
        print(f"지도 생성 중 오류 발생")
        return None, None

def get_satellite_image(lat, lon, station_name, zoom_level=17):
    """위성 이미지 획득"""
    driver = None
    try:
        print(f"위성 이미지 캡처 시작 - 좌표: {lat}, {lon}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--force-device-scale-factor=1')
        options.add_argument('--hide-scrollbars')  # 스크롤바 숨기기
        
        print("웹드라이버 초기화 중...")
        driver = webdriver.Chrome(service=WEBDRIVER_SERVICE, options=options)
        driver.set_window_size(1920, 1080)
        
        # 네이버 지도 위성 지도 URL로 변경
        naver_url = f"https://map.naver.com/v5/aerial/{lon},{lat},17z"
        print(f"페이지 로딩 중: {naver_url}")
        
        driver.get(naver_url)
        print("페이지 로딩 완료")
        
        # 지도 로딩 대기
        print("지도 로딩 대기 중...")
        time.sleep(8)  # 위성 이미지 로딩을 위한 충분한 대기 시간
        
        # 스크린샷 저장
        safe_name = ''.join(c for c in station_name if c.isalnum())
        temp_path = os.path.join(DOWNLOAD_PATH, f'temp_{safe_name}_satellite.png')
        final_path = os.path.join(DOWNLOAD_PATH, f'NH_GasStation_{safe_name}_satellite.jpg')
        
        print(f"스크린샷 캡처 시도 중... ({temp_path})")
        
        # 전체 화면 캡처
        driver.save_screenshot(temp_path)
        
        if os.path.exists(temp_path):
            print("스크린샷 캡처 성공")
            
            # 이미지 처리 - 크롭 및 품질 향상
            image = Image.open(temp_path)
            
            # 이미지 중앙 부분만 크롭 (네비게이션 UI 제거)
            width, height = image.size
            crop_size = min(width, height)
            left = (width - crop_size) // 2
            top = (height - crop_size) // 2
            right = left + crop_size
            bottom = top + crop_size
            
            image = image.crop((left, top, right, bottom))
            image = image.convert('RGB')
            
            # 최종 이미지 저장
            image.save(final_path, 'JPEG', quality=95)
            os.remove(temp_path)
            
            print(f"최종 이미지 저장 완료: {final_path}")
            return final_path
            
        else:
            print("스크린샷 캡처 실패")
            return None
            
    except Exception as e:
        print(f"위성 이미지 획득 중 오류 발생: {str(e)}")
        import traceback
        print("상세 오류 정보:")
        print(traceback.format_exc())
        return None
        
    finally:
        if driver:
            print("웹드라이버 종료")
            driver.quit()
            
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
        
        result = is_eco_by_code or is_eco_by_name
        
        if result:
            print(f"\n알뜰주유소 확인:")
            reasons = []
            if poll_div_cd in economical_codes['POLL_DIV_CD']:
                reasons.append(f"정유사 코드: {poll_div_cd}")
            if van_co_cd in economical_codes['VAN_CO_CD']:
                reasons.append(f"회사 코드: {van_co_cd}")
            if is_eco_by_name:
                reasons.append("이름에 '알뜰' 포함")
            print(f"- 판별 근거: {', '.join(reasons)}")
        
        return result
        
    except Exception as e:
        print(f"알뜰주유소 확인 중 오류: {str(e)}")
        return False

def fetch_gas_station_data(api_key):
    """모든 알뜰주유소 데이터 조회"""
    try:
        all_stations = []
        
        # 지역별 조회를 위한 시도 코드
        area_codes = {
            '01': '서울', '02': '경기', '03': '인천', '04': '강원',
            '05': '충북', '06': '충남', '07': '대전', '08': '경북',
            '09': '경남', '10': '부산', '11': '울산', '12': '대구',
            '13': '전북', '14': '전남', '15': '광주', '16': '제주'
        }
        
        print("\n=== 알뜰주유소 데이터 조회 중 ===")
        
        # 각 지역별로 조회
        for area_code, area_name in area_codes.items():
            params = {
                'code': api_key,
                'out': 'json',
                'area': area_code
            }
            
            # 각 정유사별 코드로 조회
            for prodcd in ['B027', 'D047', 'E019', 'F027', 'C004', 'C003', 'B034', 'E011']:
                params['prodcd'] = prodcd
                response = requests.get(BASE_URL, params=params)
                data = response.json()
                
                if 'RESULT' in data and 'OIL' in data['RESULT']:
                    stations = data['RESULT']['OIL']
                    eco_stations = [station for station in stations 
                                  if is_economical_station(station)]
                    if eco_stations:
                        print(f"{area_name} - 상품코드 {prodcd}: {len(eco_stations)}개의 알뜰주유소")
                        all_stations.extend(eco_stations)
        
        # 중복 제거
        unique_stations = list({station['UNI_ID']: station for station in all_stations}.values())
        
        # 지역별 통계
        print("\n=== 지역별 알뜰주유소 현황 ===")
        stations_by_region = {}
        for station in unique_stations:
            addr = station.get('NEW_ADR', station.get('VAN_ADR', ''))
            region = addr.split(' ')[0] if addr else '기타'
            stations_by_region[region] = stations_by_region.get(region, 0) + 1
            
        for region, count in sorted(stations_by_region.items()):
            print(f"{region}: {count}개")
        
        print(f"\n총 {len(unique_stations)}개의 알뜰주유소를 찾았습니다.")
        return unique_stations
        
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None
def analyze_nearby_stations(api_key, station):
    """주유소 분석"""
    try:
        if not is_economical_station(station):
            print("알뜰주유소가 아닙니다. 다른 주유소를 선택합니다.")
            return False
            
        print("\n=== 주유소 상세 정보 ===")
        utm_x = float(station["GIS_X_COOR"])
        utm_y = float(station["GIS_Y_COOR"])
        lat, lon = convert_utm_to_wgs84(utm_x, utm_y)
        
        station_name = station["OS_NM"]
        address = station.get("NEW_ADR", station.get("VAN_ADR", "주소 없음"))
        price = station["PRICE"]
        
        print(f"주유소: {station_name}")
        print(f"주소: {address}")
        print(f"가격: {price}원")
        
        result = get_nearby_gas_stations(api_key, lon, lat)
        
        if result['success']:
            if result['inner_station_count'] > 0:
                print(f"\n반경 1마일 내 분석 결과:")
                print(f"총 주유소 수: {result['inner_station_count']}개")
                print(f"유효 가격 주유소: {result['inner_valid_station_count']}개")
                if result['inner_avg_price']:
                    print(f"평균 가격: {result['inner_avg_price']:,.0f}원")
                else:
                    print("평균 가격: 정보 없음")
            else:
                print("반경 1마일 내에 주유소가 없습니다.")
            
            if result['outer_station_count'] > 0:
                print(f"\n반경 1~2마일 사이 분석 결과:")
                print(f"총 주유소 수: {result['outer_station_count']}개")
                print(f"유효 가격 주유소: {result['outer_valid_station_count']}개")
                if result['outer_avg_price']:
                    print(f"평균 가격: {result['outer_avg_price']:,.0f}원")
                else:
                    print("평균 가격: 정보 없음")
            else:
                print("반경 1~2마일 내에 주유소가 없습니다.")
            
            if result['inner_avg_price'] and result['outer_avg_price']:
                avg_price_diff = result['inner_avg_price'] - result['outer_avg_price']
                print(f"\n1마일 이내와 1~2마일 사이의 평균 가격 차이: {avg_price_diff:,.0f}원")
                
            print("\n지도 생성 중...")
            map_path = create_map(lat, lon, station_name, address, 
                              result['inner_stations'] + result['outer_stations'])
            if map_path:
                print(f"지도 생성 완료")
            
            return True
        else:
            print(f"분석 실패: {result['message']}")
            return False
            
    except Exception as e:
        print(f"주유소 분석 중 오류 발생: {str(e)}")
        return False


def main():
    """메인 함수"""
    try:
        print("=== 주유소 분석 프로그램 시작 ===")
        
        # 알뜰주유소 데이터 조회
        print("\n알뜰주유소 데이터 조회 중...")
        stations = fetch_gas_station_data(API_KEY)
        
        if not stations:
            print("주유소 정보가 없습니다.")
            return
        
        print(f"\n전체 {len(stations)}개의 알뜰주유소를 찾았습니다.")
        
        # 무작위 선택을 위한 가중치 부여
        weighted_stations = []
        for station in stations:
            # 가격이 낮을수록 더 높은 가중치 부여
            price = float(station.get('PRICE', 9999))
            weight = 1.0
            if price < 1600:  # 저렴한 주유소에 더 높은 가중치
                weight = 2.0
            
            # 수도권 지역은 약간 낮은 가중치 (지역 다양성)
            addr = station.get('NEW_ADR', station.get('VAN_ADR', ''))
            if any(region in addr for region in ['서울', '경기', '인천']):
                weight *= 0.8
                
            weighted_stations.extend([station] * int(weight * 10))
        
        # 분석 시도
        success = False
        tried_stations = set()
        
        while not success and len(tried_stations) < len(stations):
            # 가중치가 적용된 목록에서 무작위 선택
            random_station = random.choice(weighted_stations)
            station_id = random_station['UNI_ID']
            
            if station_id not in tried_stations:
                tried_stations.add(station_id)
                print(f"\n선택된 주유소: {random_station['OS_NM']}")
                print(f"주소: {random_station.get('NEW_ADR', random_station.get('VAN_ADR', '주소 없음'))}")
                
                # 선택된 주유소 분석
                success = analyze_nearby_stations(API_KEY, random_station)
        
        if not success:
            print("분석 가능한 알뜰주유소를 찾지 못했습니다.")
        
    except Exception as e:
        print(f"\n프로그램 실행 중 오류 발생: {str(e)}")
        import traceback
        print("\n상세 오류 정보:")
        print(traceback.format_exc())
    finally:
        print("\n=== 프로그램 종료 ===")

# 프로그램 시작
if __name__ == "__main__":
    main()
