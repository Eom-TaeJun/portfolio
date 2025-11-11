import requests
import json
from datetime import datetime

def get_economical_gas_station_location(api_key="F241130499"):
    # 오피넷 API 엔드포인트
    base_url = "http://www.opinet.co.kr/api/lowTop10.do"
    
    # API 요청 파라미터
    params = {
        'code': api_key,
        'out': 'json',
        'prodcd': 'B027',  # 휘발유
        'area': '01'  # 전국단위
    }
    
    try:
        # API 요청
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # HTTP 오류 체크
        
        # JSON 응답 파싱
        data = response.json()
        
        # 주유소 정보 추출 및 정리
        stations = []
        if 'RESULT' in data and 'OIL' in data['RESULT']:
            for station in data['RESULT']['OIL']:
                station_info = {
                    '상호': station.get('OS_NM', ''),
                    '주소': station.get('NEW_ADR', ''),
                    '가격': station.get('PRICE', ''),
                    '전화번호': station.get('TEL', ''),
                    '위도': station.get('GIS_X_COORD', ''),
                    '경도': station.get('GIS_Y_COORD', '')
                }
                stations.append(station_info)
        
        return stations
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 중 오류 발생: {e}")
        return None

def print_station_info(stations):
    if not stations:
        print("주유소 정보를 가져오는데 실패했습니다.")
        return
        
    print(f"\n=== 알뜰주유소 위치 정보 ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===\n")
    
    for idx, station in enumerate(stations, 1):
        print(f"[{idx}번 주유소]")
        print(f"상호: {station['상호']}")
        print(f"주소: {station['주소']}")
        print(f"가격: {station['가격']}원")
        print(f"전화번호: {station['전화번호']}")
        print(f"좌표: ({station['위도']}, {station['경도']})")
        print("-" * 50)

if __name__ == "__main__":
    # 주유소 정보 가져오기
    stations = get_economical_gas_station_location()
    
    # 정보 출력
    print_station_info(stations)