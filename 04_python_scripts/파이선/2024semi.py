import pandas as pd

# CSV 파일 경로
file_path = "C:/Users/엄태준/Desktop/2024semi.csv"
# CSV 파일 읽기
df = pd.read_csv(file_path)
# CSV 파일의 열 목록 확인
columns = df.columns.tolist()
columns
df.head()
df.info()

import mysql.connector
# 테이블 생성 쿼리 생성
create_table_query = """
CREATE DATABASE IF NOT EXISTS my_database;
USE my_database;

CREATE TABLE IF NOT EXISTS my_table (
    `id` INT AUTO_INCREMENT,
    {}
    PRIMARY KEY (`id`)
);
""".format(
    ",\n    ".join([f"`{col}` VARCHAR(255)" for col in columns])
)

print(create_table_query)  # 쿼리 확인용 출력

# MySQL 연결 설정
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='!eomtaejun01',
    database='my_database'
)

# 커서 생성
cursor = db_connection.cursor()

# 테이블 생성 쿼리 실행
for result in cursor.execute(create_table_query, multi=True):
    pass

# 데이터 삽입 쿼리 생성
insert_query = """
    INSERT INTO my_table ({})
    VALUES ({})
""".format(
    ", ".join([f"`{col}`" for col in columns]),
    ", ".join(["%s" for _ in columns])
)

# 데이터 삽입
for _, row in df.iterrows():
    cursor.execute(insert_query, tuple(row))

# 커밋
db_connection.commit()

# 연결 종료
cursor.close()
db_connection.close()
