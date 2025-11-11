import requests
import pandas as pd
import os

def get_gas_stations():
    # API 호출 정보
    url = "http://api.vworld.kr/req/search"
    stations_data = []
    page = 1
    
    while True:
        params = {
            'service': 'search',
            'request': 'search',
            'version': '2.0',
            'crs': 'EPSG:4326',
            'size': '100',
            'page': str(page),
            'query': '농협주유소',
            'type': 'place',
            'format': 'json',
            'key': '9178F15A-B959-392E-9997-FF025928BD6B'
        }
        
        # API 호출
        response = requests.get(url, params=params)
        data = response.json()
        
        # 데이터 확인 및 추출
        if 'response' in data and 'result' in data['response'] and 'items' in data['response']['result']:
            items = data['response']['result']['items']
            if not items:  # 더 이상 데이터가 없으면 종료
                break
                
            for item in items:
                station = {
                    '이름': item['title'],
                    '도로명주소': item['address'].get('road', ''),
                    '지번주소': item['address'].get('parcel', ''),
                    '전화번호': item.get('tel', ''),
                    '경도': item['point']['x'],
                    '위도': item['point']['y']
                }
                stations_data.append(station)
                
            page += 1
        else:
            break
    
    # 다운로드 폴더 경로 가져오기
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    # DataFrame 생성 및 엑셀 저장
    df = pd.DataFrame(stations_data)
    excel_path = os.path.join(download_path, '알뜰주유소_위치정보 농협.xlsx')
    df.to_excel(excel_path, index=False)
    
    return f"총 {len(stations_data)}개의 주유소 정보가 다운로드 폴더에 저장되었습니다."

if __name__ == "__main__":
    print(get_gas_stations())
