import mysql.connector
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm

# CSV 파일 경로
file_path = "C:/Users/엄태준/Desktop/2024semi1.csv"

# CSV 파일 읽기
df = pd.read_csv(file_path)
# 모든 열 출력 설정
pd.set_option('display.max_columns', None)
# 데이터프레임 확인
print(df.head())
# 열 목록 확인
columns = df.columns.tolist()

# NaN 값을 None으로 변환
df = df.replace({np.nan: None})

# MySQL 연결 설정
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='!eomtaejun01',
    database='my_database'
)
# 커서 생성
cursor = db_connection.cursor()

# 데이터 유형 기반 테이블 생성 쿼리 생성
def get_mysql_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "INT"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    else:
        return "VARCHAR(255)"

# 데이터 유형 기반 테이블 생성 쿼리 작성
column_definitions = ",\n    ".join([f"`{col}` {get_mysql_type(dtype)}" for col, dtype in zip(df.columns, df.dtypes)])
create_table_query = f"""
CREATE TABLE IF NOT EXISTS my_table (
    id INT AUTO_INCREMENT,
    {column_definitions},
    PRIMARY KEY (id)
);
"""

print(create_table_query)  # 쿼리 확인용 출력

# 테이블 생성 쿼리 실행
cursor.execute(create_table_query)

# 데이터 삽입 쿼리 생성
insert_query = f"""
    INSERT INTO my_table ({", ".join([f"`{col}`" for col in columns])})
    VALUES ({", ".join(["%s" for _ in columns])})
"""

# 데이터 삽입
for _, row in df.iterrows():
    cursor.execute(insert_query, tuple(row))

# 커밋
db_connection.commit()

# 데이터 가져오기
query = "SELECT EV, xSLG, BABIP, wOBA, `Pull%` FROM my_table;"
df = pd.read_sql_query(query, db_connection)

# 연결 종료
cursor.close()
db_connection.close()

# 데이터프레임 확인
print(df.head())

# EV와 xSLG의 관계
plt.figure(figsize=(10, 6))
sns.scatterplot(x='EV', y='xSLG', data=df)
plt.title('EV&xSLG')
plt.xlabel('EV')
plt.ylabel('xSLG')
plt.show()

# EV와 BABIP의 관계
plt.figure(figsize=(10, 6))
sns.scatterplot(x='EV', y='BABIP', data=df)
plt.title('EV&BABIP')
plt.xlabel('EV')
plt.ylabel('BABIP')
plt.show()

# EV와 wOBA의 관계
plt.figure(figsize=(10, 6))
sns.scatterplot(x='EV', y='wOBA', data=df)
plt.title('EV&wOBA')
plt.xlabel('EV')
plt.ylabel('wOBA')
plt.show()

# EV와 Pull%의 관계
plt.figure(figsize=(10, 6))
sns.scatterplot(x='EV', y='Pull%', data=df)
plt.title('EV&Pull%')
plt.xlabel('EV')
plt.ylabel('Pull%')
plt.show()

# 상관계수 계산
correlation_matrix = df.corr()

print("COR:")
print(correlation_matrix)

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('COR')
plt.show()

# EV와 xSLG 회귀 분석
X = df[['EV']]
X = sm.add_constant(X)  # 절편 추가
y = df['xSLG']

model = sm.OLS(y, X).fit()
print("EV&xSLG regression:")
print(model.summary())

# EV와 BABIP 회귀 분석
X = df[['EV']]
X = sm.add_constant(X)  # 절편 추가
y = df['BABIP']

model = sm.OLS(y, X).fit()
print("EV&BABIP regression:")
print(model.summary())

# EV와 wOBA 회귀 분석
X = df[['EV']]
X = sm.add_constant(X)  # 절편 추가
y = df['wOBA']

model = sm.OLS(y, X).fit()
print("EV&wOBA regression:")
print(model.summary())

# EV와 Pull% 회귀 분석
X = df[['EV']]
X = sm.add_constant(X)  # 절편 추가
y = df['Pull%']

model = sm.OLS(y, X).fit()
print("EV&Pull% regression:")
print(model.summary())
