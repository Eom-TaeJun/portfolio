import mysql.connector
import pandas as pd

# CSV 파일 경로
file_path = "C:/Users/엄태준/Desktop/2024semi.csv"

# CSV 파일 읽기
df = pd.read_csv(file_path)

# 열 목록 확인
columns = df.columns.tolist()

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
    `id` INT AUTO_INCREMENT,
    {column_definitions},
    PRIMARY KEY (`id`)
);
"""

print(create_table_query)  # 쿼리 확인용 출력

# 테이블 생성 쿼리 실행
for result in cursor.execute(create_table_query, multi=True):
    pass

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

# 연결 종료
cursor.close()
db_connection.close()
