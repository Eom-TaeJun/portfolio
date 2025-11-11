import requests

def get_nearby_gas_stations(api_key, x_coord, y_coord, radius_meters=1600):
    """
    특정 좌표 주변의 주유소 정보를 조회하는 함수
    radius_meters: 반경(미터) - 기본값 1600m (약 1마일)
    """
    base_url = "http://www.opinet.co.kr/api/aroundAll.do"
    
    params = {
        'code': api_key,
        'x': str(x_coord),
        'y': str(y_coord),
        'radius': str(radius_meters),
        'sort': 1,  # 거리순 정렬
        'out': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if 'RESULT' not in data:
            raise Exception(f"API 응답 형식 오류: {response.text}")
            
        stations = data['RESULT']['OIL']
        
        # 가격 분석
        valid_prices = [float(station['PRICE']) for station in stations if float(station.get('PRICE', 0)) > 0]
        
        if not valid_prices:
            return {
                'station_count': 0,
                'avg_price': None,
                'success': True,
                'message': '유효한 가격 정보가 있는 주유소가 없습니다.'
            }
            
        return {
            'station_count': len(stations),
            'valid_station_count': len(valid_prices),
            'avg_price': sum(valid_prices) / len(valid_prices),
            'min_price': min(valid_prices),
            'max_price': max(valid_prices),
            'success': True,
            'message': '정상적으로 조회되었습니다.',
            'stations': [{
                'name': s['OS_NM'],
                'price': float(s['PRICE']),
                'brand': s.get('POLL_DIV_CD', 'N/A')
            } for s in stations[:5] if float(s.get('PRICE', 0)) > 0]  # 상위 5개만
        }
        
    except Exception as e:
        return {'success': False, 'message': f'처리 중 오류 발생: {str(e)}'}

def analyze_station(api_key, station, radius_meters=1600):
    """
    단일 주유소 기준 주변 분석을 수행하는 함수
    """
    station_name = station['OS_NM']
    station_addr = station.get('NEW_ADR', station.get('VAN_ADR', '주소 없음'))
    station_price = float(station['PRICE'])
    
    print(f"\n=== {station_name} 분석 ===")
    print(f"주소: {station_addr}")
    print(f"현재 가격: {station_price:,.0f}원")
    
    result = get_nearby_gas_stations(
        api_key, 
        station.get('GIS_X_COOR'), 
        station.get('GIS_Y_COOR'), 
        radius_meters
    )
    
    if result['success']:
        print(f"\n반경 {radius_meters/1000:.1f}km 내 분석 결과:")
        print(f"총 주유소 수: {result['station_count']}개")
        print(f"유효 가격 주유소: {result['valid_station_count']}개")
        
        if result['avg_price']:
            print(f"평균 가격: {result['avg_price']:,.0f}원")
            print(f"최저 가격: {result['min_price']:,.0f}원")
            print(f"최고 가격: {result['max_price']:,.0f}원")
            print(f"현재 가격과의 차이: {(station_price - result['avg_price']):+,.0f}원")
        
        if result.get('stations'):
            print("\n주변 주유소 가격:")
            for s in result['stations']:
                print(f"- {s['name']} ({s['brand']}): {s['price']:,.0f}원")
    else:
        print(f"분석 실패: {result['message']}")

def main():
    api_key = 'F241130499'
    radius_meters = 1600  # 약 1마일
    
    print("=== 알뜰주유소 기반 가격 분석 시작 ===")
    
    try:
        # 알뜰주유소 목록 조회
        base_url = "http://www.opinet.co.kr/api/lowTop10.do"
        params = {
            'code': api_key,
            'prodcd': 'B027',  # 휘발유
            'out': 'json'
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
        stations = data['RESULT']['OIL']
        
        print(f"\n전체 {len(stations)}개의 알뜰주유소를 찾았습니다.")
        
        for station in stations:
            analyze_station(api_key, station, radius_meters)
            
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
