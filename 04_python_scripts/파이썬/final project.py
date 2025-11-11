import os
import time
import json
import requests
import pandas as pd
import numpy as np
import folium
from pyproj import CRS, Transformer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random
from PIL import Image
import logging
import cv2
from pathlib import Path
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from geopy.distance import geodesic

# 상수 정의
CONFIG = {
    'API_KEY': 'F241130499',
    'BASE_URL': "http://www.opinet.co.kr/api/lowTop10.do",
    'DOWNLOAD_PATH': os.path.join(os.path.expanduser("~"), "Downloads"),
    'WEBDRIVER_PATH': "C:/Users/TJ/.wdm/drivers/chromedriver/win64/131.0.6778.85/chromedriver-win32/chromedriver.exe",
    'IMAGE_PATH': "C:\\Users\\TJ\\Desktop\\image",
    'EXCEL_PATH': "C:\\Users\\TJ\\Desktop\\ex",
    'SAMPLE_SIZE': 50
}

def setup_logging():
    """로깅 설정"""
    os.makedirs(CONFIG['EXCEL_PATH'], exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(CONFIG['EXCEL_PATH'], 'gas_station_analysis.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def api_call_with_retry(url, params, max_retries=3, timeout=10):
    """API 호출 재시도 메커니즘"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

def convert_utm_to_wgs84(utm_x, utm_y):
    """KATEC/UTM-K 좌표를 WGS84 위경도로 변환"""
    try:
        katec_proj = CRS.from_proj4(
            "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 +ellps=bessel "
            "+units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43"
        )
        wgs84_proj = CRS.from_epsg(4326)
        transformer = Transformer.from_crs(katec_proj, wgs84_proj, always_xy=True)
        lon, lat = transformer.transform(float(utm_x), float(utm_y))
        return lat, lon
    except Exception as e:
        logging.error(f"좌표 변환 중 오류: {str(e)}")
        raise

def is_economical_station(station):
    """알뜰주유소 판별"""
    try:
        poll_div_cd = station.get('POLL_DIV_CD', '').upper()
        van_co_cd = station.get('VAN_CO_CD', '').upper()
        os_nm = station.get('OS_NM', '').upper()
        
        eco_codes = ['SKE', 'GSC', 'HDO', 'SOL', 'RTO', 'RTX', 'NHO', 'NH', 'SK', 'GS', 'HD', 'SO', 'RT']
        eco_keywords = ['알뜰', '농협', 'NH']
        
        is_eco_by_code = any(code in [poll_div_cd, van_co_cd] for code in eco_codes)
        is_eco_by_name = any(keyword in os_nm for keyword in eco_keywords)
        
        return is_eco_by_code or is_eco_by_name
    except Exception as e:
        logging.error(f"알뜰주유소 확인 중 오류: {str(e)}")
        return False

def get_station_prices(api_key, rad_lat, rad_lon, radius):
    """특정 반경 내의 주유소 가격 정보 조회"""
    try:
        # 좌표를 KATEC으로 변환
        katec_proj = CRS.from_proj4(
            "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 +ellps=bessel "
            "+units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43"
        )
        wgs84_proj = CRS.from_epsg(4326)
        transformer = Transformer.from_crs(wgs84_proj, katec_proj, always_xy=True)
        
        katec_x, katec_y = transformer.transform(rad_lon, rad_lat)
        
        url = "http://www.opinet.co.kr/api/aroundAll.do"
        params = {
            'code': api_key,
            'out': 'json',
            'x': str(int(katec_x)),
            'y': str(int(katec_y)),
            'radius': str(int(radius * 1000)),  # km를 m로 변환
            'prodcd': 'B027'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        
        for attempt in range(3):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                
                # HTML 응답 체크
                if '<html' in response.text or '<!DOCTYPE' in response.text:
                    logging.warning("HTML 응답 수신, 재시도...")
                    time.sleep(2)
                    continue
                
                data = response.json()
                if 'RESULT' in data and 'OIL' in data['RESULT']:
                    return data['RESULT']['OIL']
                    
                logging.warning(f"유효하지 않은 응답 형식: {response.text[:200]}")
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"API 호출 시도 {attempt + 1} 실패: {str(e)}")
                time.sleep(2)
                continue
                
        return []
        
    except Exception as e:
        logging.error(f"가격 정보 조회 중 오류: {str(e)}")
        return []
def analyze_price_impact(station, config):
    """주유소 주변 가격 영향 분석"""
    try:
        utm_x = float(station["GIS_X_COOR"])
        utm_y = float(station["GIS_Y_COOR"])
        lat, lon = convert_utm_to_wgs84(utm_x, utm_y)
        
        # 반경을 좀 더 크게 설정하여 데이터 수집
        inner_radius = 2.0  # 1.6km에서 2.0km로 증가
        outer_radius = 4.0  # 3.2km에서 4.0km로 증가
        
        # 재시도 메커니즘
        max_retries = 3
        inner_stations = []
        outer_stations = []
        
        for attempt in range(max_retries):
            inner_stations = get_station_prices(config['API_KEY'], lat, lon, inner_radius)
            if inner_stations:
                break
            logging.info(f"내부 반경 데이터 재시도 {attempt + 1}")
            time.sleep(2)
            
        for attempt in range(max_retries):
            outer_stations = get_station_prices(config['API_KEY'], lat, lon, outer_radius)
            if outer_stations:
                break
            logging.info(f"외부 반경 데이터 재시도 {attempt + 1}")
            time.sleep(2)
        
        # 가격 분석
        inner_prices = []
        for s in inner_stations:
            try:
                price = float(s.get('PRICE', 0))
                if price > 0:
                    inner_prices.append(price)
                    logging.info(f"내부 반경 주유소 가격: {price}")
            except:
                continue
        
        outer_prices = []
        for s in outer_stations:
            try:
                s_lat, s_lon = convert_utm_to_wgs84(float(s["GIS_X_COOR"]), float(s["GIS_Y_COOR"]))
                distance = geodesic((lat, lon), (s_lat, s_lon)).kilometers
                price = float(s.get('PRICE', 0))
                if inner_radius < distance <= outer_radius and price > 0:
                    outer_prices.append(price)
                    logging.info(f"외부 반경 주유소 가격: {price}")
            except:
                continue
        
        # 최소 데이터 요구사항 완화
        if len(inner_prices) >= 1 and len(outer_prices) >= 1:
            inner_avg = sum(inner_prices) / len(inner_prices)
            outer_avg = sum(outer_prices) / len(outer_prices)
            price_impact = outer_avg - inner_avg
            
            result = {
                'inner_station_count': len(inner_prices),
                'outer_station_count': len(outer_prices),
                'inner_avg_price': round(inner_avg, 2),
                'outer_avg_price': round(outer_avg, 2),
                'price_impact': round(price_impact, 2)
            }
            
            logging.info(f"가격 분석 결과: {result}")
            return result
            
        else:
            logging.warning(f"데이터 부족 - 내부: {len(inner_prices)}개, 외부: {len(outer_prices)}개")
            # 부분적 데이터라도 반환
            return {
                'inner_station_count': len(inner_prices),
                'outer_station_count': len(outer_prices),
                'inner_avg_price': round(sum(inner_prices) / len(inner_prices), 2) if inner_prices else 0,
                'outer_avg_price': round(sum(outer_prices) / len(outer_prices), 2) if outer_prices else 0,
                'price_impact': 0  # 데이터가 부족한 경우 영향도 0으로 설정
            }
        
    except Exception as e:
        logging.error(f"가격 영향 분석 중 오류: {str(e)}")
        return None
def save_map_for_cnn(lat, lon, station_name, config):
    """지도 이미지 생성 및 저장"""
    try:
        safe_name = ''.join(c for c in station_name if c.isalnum() or c.isspace())
        safe_name = safe_name.replace(' ', '_')
        file_base = f'GasStation_{safe_name}'
        html_file = os.path.join(config['DOWNLOAD_PATH'], f'{file_base}.html')
        
        delta = 0.0145 / 2
        bounds = [[lat - delta, lon - delta], [lat + delta, lon + delta]]
        
        map_ = folium.Map(location=[lat, lon], zoom_start=15, tiles='OpenStreetMap')
        map_.fit_bounds(bounds)
        map_.save(html_file)
        
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(config['WEBDRIVER_PATH']), options=options)
        
        driver.set_window_size(1000, 1000)
        driver.get(f'file:///{os.path.abspath(html_file)}')
        time.sleep(5)
        
        os.makedirs(config['IMAGE_PATH'], exist_ok=True)
        # 임시로 PNG 파일로 저장
        temp_png_path = os.path.join(config['IMAGE_PATH'], f'{file_base}_temp.png')
        driver.save_screenshot(temp_png_path)
        
        # PNG를 JPG로 변환
        if os.path.exists(temp_png_path):
            image = Image.open(temp_png_path)
            image = image.convert('RGB')  # PNG to JPG 변환을 위해 필요
            final_jpg_path = os.path.join(config['IMAGE_PATH'], f'{file_base}.jpg')
            image.save(final_jpg_path, 'JPEG', quality=95)
            os.remove(temp_png_path)  # 임시 PNG 파일 삭제
            
            driver.quit()
            os.remove(html_file)
            return final_jpg_path
            
    except Exception as e:
        logging.error(f"이미지 생성 중 오류 발생: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None
def extract_image_features(image_path):
    """이미지에서 특성 추출"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        features = {
            'mean_intensity': np.mean(gray),
            'std_intensity': np.std(gray),
            'median_intensity': np.median(gray),
            'road_density': np.sum(gray > 200) / gray.size,
            'building_density': np.sum((gray > 100) & (gray < 200)) / gray.size
        }
        
        edges = cv2.Canny(gray, 100, 200)
        features['edge_density'] = np.sum(edges > 0) / edges.size
        
        h, w = gray.shape
        quadrants = [
            gray[:h//2, :w//2],
            gray[:h//2, w//2:],
            gray[h//2:, :w//2],
            gray[h//2:, w//2:]
        ]
        
        for i, quad in enumerate(quadrants):
            features[f'quadrant_{i+1}_density'] = np.mean(quad)
        
        return features
    except Exception as e:
        logging.error(f"이미지 특성 추출 중 오류: {str(e)}")
        return None

def fetch_gas_station_data(config):
    """수도권 주유소 데이터 수집"""
    try:
        all_stations = []
        area_codes = {'01': '서울', '02': '경기', '03': '인천'}
        product_codes = ['B027', 'D047', 'C004', 'K015', 'B034']
        
        for area_code, area_name in area_codes.items():
            area_stations = []
            for prodcd in product_codes:
                try:
                    params = {
                        'code': config['API_KEY'],
                        'out': 'json',
                        'area': area_code,
                        'prodcd': prodcd
                    }
                    
                    data = api_call_with_retry(config['BASE_URL'], params)
                    if 'RESULT' in data and 'OIL' in data['RESULT']:
                        for station in data['RESULT']['OIL']:
                            if is_economical_station(station):
                                area_stations.append(station)
                except Exception as e:
                    logging.error(f"{area_name} {prodcd} 조회 중 오류: {str(e)}")
                    continue
            
            if area_stations:
                logging.info(f"{area_name}: {len(area_stations)}개의 알뜰주유소")
                all_stations.extend(area_stations)
        
        # 중복 제거 및 샘플링
        df = pd.DataFrame(all_stations).drop_duplicates(subset=['UNI_ID'])
        if len(df) > config['SAMPLE_SIZE']:
            df = df.sample(n=config['SAMPLE_SIZE'], random_state=42)
        
        return df
    except Exception as e:
        logging.error(f"데이터 수집 중 오류: {str(e)}")
        return None

def process_stations(stations_df, config):
    """주유소 데이터 처리 및 분석"""
    try:
        processed_data = []
        total_stations = len(stations_df)
        success_count = 0
        
        for idx, station in stations_df.iterrows():
            try:
                logging.info(f"Processing station {idx+1}/{total_stations}: {station['OS_NM']}")
                
                # 1. 가격 영향 분석
                price_analysis = analyze_price_impact(station, config)
                if not price_analysis:
                    logging.warning(f"Price analysis failed for station: {station['OS_NM']}")
                    continue
                    
                # 2. 이미지 생성
                utm_x = float(station["GIS_X_COOR"])
                utm_y = float(station["GIS_Y_COOR"])
                lat, lon = convert_utm_to_wgs84(utm_x, utm_y)
                
                image_path = save_map_for_cnn(lat, lon, station["OS_NM"], config)
                if not image_path:
                    logging.warning(f"Image save failed for station: {station['OS_NM']}")
                    continue
                    
                # 3. 이미지 특성 추출
                image_features = extract_image_features(image_path)
                if not image_features:
                    logging.warning(f"Feature extraction failed for station: {station['OS_NM']}")
                    continue
                    
                # 4. 데이터 통합
                station_data = {
                    **station.to_dict(),
                    **price_analysis,
                    **image_features
                }
                
                processed_data.append(station_data)
                success_count += 1
                logging.info(f"Successfully processed station: {station['OS_NM']}")
                
            except Exception as e:
                logging.error(f"Error processing station {station['OS_NM']}: {str(e)}")
                continue
        
        logging.info(f"Total stations: {total_stations}, Successfully processed: {success_count}")
        
        # 여기에 데이터 검증 부분 추가
        if len(processed_data) == 0:
            logging.error("No data was processed successfully")
            return None
            
        df = pd.DataFrame(processed_data)
        logging.info(f"Final processed dataframe shape: {df.shape}")
        logging.info(f"Columns: {df.columns.tolist()}")
        
        # 필수 컬럼 존재 여부 확인
        required_columns = ['OS_NM', 'price_impact', 'inner_avg_price', 'outer_avg_price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logging.error(f"Missing required columns: {missing_columns}")
            return None
            
        # 데이터 타입 검증
        try:
            df['price_impact'] = df['price_impact'].astype(float)
            df['inner_avg_price'] = df['inner_avg_price'].astype(float)
            df['outer_avg_price'] = df['outer_avg_price'].astype(float)
        except Exception as e:
            logging.error(f"Error converting data types: {str(e)}")
            return None
            
        # 결측치 확인
        null_counts = df.isnull().sum()
        if null_counts.any():
            logging.warning(f"Null values found in columns: \n{null_counts[null_counts > 0]}")
            
        return df
        
    except Exception as e:
        logging.error(f"데이터 처리 중 오류: {str(e)}")
        return None

def train_and_analyze(df):
    """XGBoost 모델 학습 및 분석"""
    try:
        # 특성 선택
        exclude_cols = ['OS_NM', 'UNI_ID', 'GIS_X_COOR', 'GIS_Y_COOR']
        features = [col for col in df.columns if col not in exclude_cols]
        X = df[features]
        y = df['price_impact']
        
        # 데이터 스케일링
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
        
        # 모델 학습
        model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        model.fit(X_scaled, y)
        
        # 특성 중요도 분석
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return model, feature_importance
    except Exception as e:
        logging.error(f"모델 학습 및 분석 중 오류: {str(e)}")
        return None, None

def save_results(df, feature_importance, config):
    """결과 저장"""
    try:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # 처리된 데이터 저장
        data_path = os.path.join(config['EXCEL_PATH'], f'processed_data_{timestamp}.xlsx')
        df.to_excel(data_path, index=False)
        logging.info(f"처리된 데이터 저장 완료: {data_path}")
        
        # 특성 중요도 저장
        if feature_importance is not None:
            importance_path = os.path.join(config['EXCEL_PATH'], f'feature_importance_{timestamp}.xlsx')
            feature_importance.to_excel(importance_path, index=False)
            logging.info(f"특성 중요도 저장 완료: {importance_path}")
            
            # 특성 중요도 시각화
            plt.figure(figsize=(10, 6))
            plt.bar(feature_importance['feature'][:10], feature_importance['importance'][:10])
            plt.xticks(rotation=45, ha='right')
            plt.title('Top 10 Feature Importance')
            plt.tight_layout()
            
            plot_path = os.path.join(config['EXCEL_PATH'], f'feature_importance_{timestamp}.png')
            plt.savefig(plot_path)
            plt.close()
            logging.info(f"특성 중요도 시각화 저장 완료: {plot_path}")
        
        return True
    except Exception as e:
        logging.error(f"결과 저장 중 오류: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    try:
        # 초기 설정
        setup_logging()
        logging.info("=== 주유소 통합 분석 프로그램 시작 ===")
        
        # 디렉토리 생성
        os.makedirs(CONFIG['IMAGE_PATH'], exist_ok=True)
        os.makedirs(CONFIG['EXCEL_PATH'], exist_ok=True)
        
        # 1. 주유소 데이터 수집
        logging.info("주유소 데이터 수집 중...")
        stations_df = fetch_gas_station_data(CONFIG)
        if stations_df is None or stations_df.empty:
            raise Exception("주유소 데이터 수집 실패")
        logging.info(f"수집된 주유소 수: {len(stations_df)}")
        
        # 2. 데이터 처리 및 분석
        logging.info("데이터 처리 및 분석 중...")
        processed_df = process_stations(stations_df, CONFIG)
        if processed_df is None or processed_df.empty:
            raise Exception("데이터 처리 실패")
        logging.info(f"처리된 주유소 수: {len(processed_df)}")
        
        # 3. 모델 학습 및 분석
        logging.info("모델 학습 및 분석 중...")
        model, feature_importance = train_and_analyze(processed_df)
        if model is None:
            raise Exception("모델 학습 실패")
        
        # 4. 결과 저장
        logging.info("결과 저장 중...")
        if not save_results(processed_df, feature_importance, CONFIG):
            raise Exception("결과 저장 실패")
        
        logging.info("=== 프로그램 성공적으로 완료 ===")
        
    except Exception as e:
        logging.error(f"\n프로그램 실행 중 오류 발생: {str(e)}")
        import traceback
        logging.error("\n상세 오류 정보:")
        logging.error(traceback.format_exc())
    finally:
        logging.info("\n=== 프로그램 종료 ===")

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    main()
