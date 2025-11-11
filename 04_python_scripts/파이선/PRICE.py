import requests

def get_thrifty_stations(api_key):
    """
    전국 알뜰주유소 목록을 조회하는 함수
    """
    base_url = "http://www.opinet.co.kr/api/lowTop10.do"
    
    params = {
        'code': api_key,
        'prodcd': 'B027',  # 휘발유
        'out': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if 'RESULT' not in data:
            raise Exception("API 응답 형식이 올바르지 않습니다.")
            
        return data['RESULT']['OIL']
        
    except Exception as e:
        print(f"알뜰주유소 조회 중 오류: {str(e)}")
        return []

def get_nearby_gas_stations(api_key, latitude, longitude, radius_km):
    """
    특정 좌표 주변의 주유소 정보를 조회하는 함수
    """
    base_url = "http://www.opinet.co.kr/api/aroundAll.do"
    
    params = {
        'code': api_key,
        'x': str(longitude),
        'y': str(latitude),
        'radius': str(radius_km * 1000),
        'sort': 1,
        'out': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if 'RESULT' not in data:
            raise Exception("API 응답 형식이 올바르지 않습니다.")
            
        stations = data['RESULT']['OIL']
        
        total_stations = len(stations)
        
        if total_stations == 0:
            return {
                'station_count': 0,
                'avg_price': None,
                'success': True,
                'message': '검색 반경 내 주유소가 없습니다.'
            }
        
        # API 응답의 가격 필드명에 따라 처리
        prices = [float(station.get('PRICE', station.get('GAS_PRICE', 0))) 
                 for station in stations 
                 if float(station.get('PRICE', station.get('GAS_PRICE', 0))) > 0]
        
        avg_price = sum(prices) / len(prices) if prices else None
        
        return {
            'station_count': total_stations,
            'avg_price': avg_price,
            'success': True,
            'message': '정상적으로 조회되었습니다.',
            'stations': stations
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'처리 중 오류 발생: {str(e)}'
        }

def analyze_station(api_key, station, radius_km):
    """
    단일 주유소 기준 주변 분석을 수행하는 함수
    """
    station_name = station['OS_NM']
    station_addr = station.get('NEW_ADR', station.get('VAN_ADR', '주소 없음'))
    station_price = float(station['PRICE'])
    
    try:
        latitude = float(station.get('GIS_Y_COOR', 0))
        longitude = float(station.get('GIS_X_COOR', 0))
    except ValueError:
        print(f"주유소 {station_name}의 좌표 정보가 잘못되었습니다.")
        return
    
    print(f"\n=== {station_name} 분석 ===")
    print(f"주소: {station_addr}")
    print(f"현재 가격: {station_price}원")
    print(f"좌표: ({latitude}, {longitude})")
    
    result = get_nearby_gas_stations(api_key, latitude, longitude, radius_km)
    
    if result['success']:
        print(f"반경 {radius_km}km 이내 주유소 수: {result['station_count']}개")
        if result['avg_price']:
            print(f"주변 평균 가격: {result['avg_price']:.1f}원")
            price_diff = station_price - result['avg_price']
            print(f"평균과의 차이: {price_diff:+.1f}원")
    else:
        print(f"주변 정보 조회 실패: {result['message']}")

def main():
    api_key = 'F241130499'
    radius_km = 3
    
    print("=== 알뜰주유소 분석 시작 ===")
    
    # 알뜰주유소 목록 조회
    stations = get_thrifty_stations(api_key)
    
    if not stations:
        print("알뜰주유소 정보를 가져올 수 없습니다.")
        return
        
    print(f"\n전체 {len(stations)}개의 알뜰주유소를 찾았습니다.")
    
    # 각 알뜰주유소에 대해 분석 수행
    for station in stations:
        analyze_station(api_key, station, radius_km)

if __name__ == "__main__":
    main()
