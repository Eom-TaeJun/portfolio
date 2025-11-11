import pandas as pd
import folium
from folium import plugins
import requests
import json

def analyze_gas_stations(data_path):
    try:
        # CSV 파일 읽기
        df = pd.read_csv(data_path, encoding='euc-kr')
        df.columns = ['상호', '주소', '유형', '폐업여부']
        
        # 운영 중인 주유소만 필터링
        active_stations = df[df['폐업여부'] == 'N']
        
        # 시도별, 시군구별 분석
        sido_counts = active_stations['주소'].apply(lambda x: x.split()[0]).value_counts()
        sigungu_counts = active_stations['주소'].apply(lambda x: ' '.join(x.split()[:2])).value_counts()
        
        # 분석 결과 저장
        with open('analysis_result.txt', 'w', encoding='utf-8') as f:
            f.write("=== 알뜰주유소 현황 분석 ===\n")
            f.write(f"\n총 운영 주유소 수: {len(active_stations)}개\n")
            
            f.write("\n=== 시도별 현황 ===\n")
            for sido, count in sido_counts.items():
                f.write(f"{sido}: {count}개\n")
            
            f.write("\n=== 시군구별 TOP 10 ===\n")
            for area, count in sigungu_counts.head(10).items():
                f.write(f"{area}: {count}개\n")
        
        return active_stations
        
    except Exception as e:
        print(f"데이터 분석 중 오류 발생: {e}")
        return None

def create_map(stations_df, output_file='gas_stations_map.html'):
    try:
        # 대한민국 중심 좌표
        center_lat, center_lng = 36.5, 127.5
        
        # 지도 생성
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # 마커 클러스터 생성
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        # 각 주유소의 위치를 마커로 표시
        for idx, row in stations_df.iterrows():
            try:
                address = row['주소']
                name = row['상호']
                
                # 주소를 좌표로 변환 (실제 구현 시에는 적절한 geocoding 서비스 사용 필요)
                # 여기서는 예시로 처리
                popup_text = f"상호: {name}<br>주소: {address}"
                folium.Marker(
                    # 임시 좌표 (실제 구현 시 geocoding 결과 사용)
                    location=[center_lat + idx*0.01, center_lng + idx*0.01],
                    popup=popup_text,
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(marker_cluster)
                
            except Exception as e:
                print(f"마커 생성 중 오류 발생: {e}")
                continue
        
        # 지도 저장
        m.save(output_file)
        print(f"지도가 {output_file}로 저장되었습니다.")
        
    except Exception as e:
        print(f"지도 생성 중 오류 발생: {e}")

# 메인 실행
if __name__ == "__main__":
    data_file = '한국석유공사_알뜰주유소 현황_20231231.csv'
    
    # 데이터 분석
    stations_df = analyze_gas_stations(data_file)
    
    if stations_df is not None:
        # 결과 확인
        print("분석 결과가 analysis_result.txt 파일에 저장되었습니다.")
        
        # 지도 생성
        create_map(stations_df)