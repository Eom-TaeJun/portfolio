Python 3.12.4 (tags/v3.12.4:8e8a4ba, Jun  6 2024, 19:30:16) [MSC v.1940 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import pandas as pd
... from sqlalchemy import create_engine
... 
... # 엑셀 파일 읽기
... df = pd.read_excel('data.xlsx')
... 
... # MySQL 엔진 생성
... engine = create_engine('mysql+pymysql://username:password@host:port/regression_db')
... 
... # 데이터프레임을 MySQL 테이블로 업로드
