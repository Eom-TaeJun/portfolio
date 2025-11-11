import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# MySQL 연결 설정
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='!eomtaejun01',
    database='my_database'
)
# SQL 쿼리
query = "SELECT * FROM my_table"

# 데이터프레임으로 가져오기
df = pd.read_sql(query, con=db_connection)

# 데이터프레임 확인
print(df.head())

# 연결 종료
db_connection.close()

# NaN 값을 None으로 변환
df = df.replace({np.nan: None})

# 데이터의 기본 통계
print(df.describe())

# 홈런(HR) 열의 기본 통계
print(df['HR'].describe())

# 홈런(HR) 상위 10명의 선수
top_hr_players = df[['Name', 'HR']].sort_values(by='HR', ascending=False).head(10)
print(top_hr_players)

# 히스토그램: 홈런(HR) 분포
plt.figure(figsize=(10, 6))
sns.histplot(df['HR'], bins=20, kde=True)
plt.title('Home Run Distribution')
plt.xlabel('Home Runs')
plt.ylabel('Frequency')
plt.show()

# 상관 관계 히트맵
plt.figure(figsize=(12, 8))
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()

# 특정 조건 필터링: 타율(AVG) 0.300 이상인 선수
high_avg_players = df[df['AVG'] >= 0.300]
print(high_avg_players)

# 팀별 평균 타율(AVG) 계산
# 팀 열이 있는 경우에만 실행 가능
if 'Team' in df.columns:
    team_avg = df.groupby('Team')['AVG'].mean().reset_index()
    print(team_avg)
