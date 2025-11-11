import requests

def get_nearby_gas_stations(api_key, x_coord, y_coord, radius_meters=1600, outer_radius_meters=3200):
    """
    특정 좌표 주변의 주유소 정보를 조회하는 함수
    radius_meters: 내부 반경(미터) - 기본값 1600m (약 1마일)
    outer_radius_meters: 외부 반경(미터) - 기본값 3200m (약 2마일)
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
            
        inner_stations = data['RESULT']['OIL']
        
        # 외부 반경으로 확장
        params['radius'] = str(outer_radius_meters)
        response = requests.get(base_url, params=params)
        data = response.json()
        outer_stations = data['RESULT']['OIL']
        
        # 가격 분석
        inner_valid_prices = [float(station['PRICE']) for station in inner_stations if float(station.get('PRICE', 0)) > 0]
        outer_valid_prices = [float(station['PRICE']) for station in outer_stations if float(station.get('PRICE', 0)) > 0]
        
        return {
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

def analyze_nearby_stations(api_key, station):
    """
    단일 주유소 기준 주변 주유소 분석을 수행하는 함수
    """
    station_name = station['OS_NM']
    station_addr = station.get('NEW_ADR', station.get('VAN_ADR', '주소 없음'))
    
    print(f"\n=== {station_name} 주변 주유소 분석 ===")
    print(f"주소: {station_addr}")
    
    result = get_nearby_gas_stations(
        api_key, 
        station.get('GIS_X_COOR'), 
        station.get('GIS_Y_COOR')
    )
    
    if result['success']:
        print(f"\n반경 1마일 내 분석 결과:")
        print(f"총 주유소 수: {result['inner_station_count']}개")
        print(f"유효 가격 주유소: {result['inner_valid_station_count']}개")
        
        if result['inner_avg_price']:
            print(f"평균 가격: {result['inner_avg_price']:,.0f}원")
        else:
            print("평균 가격: 정보 없음")
        
        print(f"\n반경 1~2마일 사이 분석 결과:")
        print(f"총 주유소 수: {result['outer_station_count']}개")
        print(f"유효 가격 주유소: {result['outer_valid_station_count']}개")
        
        if result['outer_avg_price']:
            print(f"평균 가격: {result['outer_avg_price']:,.0f}원")
        else:
            print("평균 가격: 정보 없음")
        
        print(f"\n1마일 이내와 1~2마일 사이의 평균 가격 차이: {(result['inner_avg_price'] or 0) - (result['outer_avg_price'] or 0):+,.0f}원")
    else:
        print(f"분석 실패: {result['message']}")

def main():
    api_key = 'F241130499'
    
    print("=== 알뜰주유소 주변 가격 분석 시작 ===")
    
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
            analyze_nearby_stations(api_key, station)
            
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
