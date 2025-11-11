import pandas as pd
import requests
import os

# API 설정
API_KEY = 'F241130499'
BASE_URL = "http://www.opinet.co.kr/api/lowTop10.do"

def read_excel_data(file_path):
    """Excel 파일에서 시군구 데이터 읽기"""
    try:
        print(f"\nExcel 파일 읽기 시작: {file_path}")
        df = pd.read_excel(file_path)
        print(f"데이터 로드 완료: {len(df)}개 행")
        return df
    except Exception as e:
        print(f"Excel 파일 읽기 오류: {str(e)}")
        return None

def process_gas_station_data():
    """알뜰주유소 데이터 수집 및 처리"""
    try:
        # 지역별 조회를 위한 시도 코드
        area_codes = {
            '01': '서울', '02': '경기', '03': '인천', '04': '강원',
            '05': '충북', '06': '충남', '07': '대전', '08': '경북',
            '09': '경남', '10': '부산', '11': '울산', '12': '대구',
            '13': '전북', '14': '전남', '15': '광주', '16': '제주'
        }
        
        all_stations = []
        print("\n알뜰주유소 데이터 조회 중...")
        
        # 각 지역별로 조회
        for area_code, area_name in area_codes.items():
            params = {
                'code': API_KEY,
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
                    all_stations.extend(stations)
        
        # 주소 기반으로 시군구 데이터 생성
        station_data = []
        for station in all_stations:
            address = station.get('NEW_ADR', station.get('VAN_ADR', ''))
            if address:
                parts = address.split()
                if len(parts) >= 2:
                    sido = parts[0]
                    sigungu = parts[1]
                    
                    # 특별시/광역시 처리
                    if sido in ['서울특별시', '서울', '부산', '대구', '인천', '광주', '대전', '울산']:
                        if not sigungu.endswith('구'):
                            sigungu += '구'
                    
                    station_data.append({
                        'sido': sido,
                        'sigungu': sigungu,
                        'full_address': address
                    })
        
        # 시군구별 집계
        df = pd.DataFrame(station_data)
        sigungu_counts = df.groupby(['sigungu']).size().reset_index(name='gas_station_count')
        print(f"총 {len(sigungu_counts)}개 시군구의 알뜰주유소 데이터 수집 완료")
        
        return sigungu_counts
        
    except Exception as e:
        print(f"알뜰주유소 데이터 처리 중 오류: {str(e)}")
        return None

def merge_and_save_data(excel_df, gas_stations_df, output_path):
    """데이터 병합 및 저장"""
    try:
        # 시군구 이름으로 데이터 병합
        merged_df = excel_df.merge(
            gas_stations_df,
            left_on='SIGUNGU_NM',
            right_on='sigungu',
            how='left'
        )
        
        # 결측치를 0으로 처리
        merged_df['gas_station_count'] = merged_df['gas_station_count'].fillna(0).astype(int)
        
        # 결과 저장
        output_file = os.path.join(os.path.dirname(output_path), 'sigungu_with_gas_stations.xlsx')
        merged_df.to_excel(output_file, index=False)
        print(f"\n결과가 저장되었습니다: {output_file}")
        
        # 기본 통계 출력
        print("\n=== 통계 정보 ===")
        print(f"전체 시군구 수: {len(merged_df)}")
        print(f"알뜰주유소가 있는 시군구 수: {len(merged_df[merged_df['gas_station_count'] > 0])}")
        print(f"시군구당 평균 알뜰주유소 수: {merged_df['gas_station_count'].mean():.2f}")
        print("\n=== 알뜰주유소 상위 10개 시군구 ===")
        print(merged_df.sort_values('gas_station_count', ascending=False)[['SIGUNGU_NM', 'gas_station_count']].head(10))
        
        return merged_df
        
    except Exception as e:
        print(f"데이터 병합 중 오류: {str(e)}")
        return None

def main():
    try:
        # 파일 경로 설정
        file_path = r"C:\Users\TJ\Desktop\www.xlsx"
        
        # Excel 데이터 읽기
        excel_df = read_excel_data(file_path)
        if excel_df is None:
            return
        
        # 알뜰주유소 데이터 수집
        gas_stations_df = process_gas_station_data()
        if gas_stations_df is None:
            return
        
        # 데이터 병합 및 저장
        merged_df = merge_and_save_data(excel_df, gas_stations_df, file_path)
        
        print("\n처리가 완료되었습니다.")
        
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
