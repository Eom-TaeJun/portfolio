import pandas as pd

# Excel 파일 읽기
file_path = r"C:\Users\TJ\Desktop\sigungu_with_gas_stations.xlsx"
df = pd.read_excel(file_path)

# CSV 파일로 저장
csv_file_path = r"C:\Users\TJ\Desktop\sigungu_with_gas_stations.csv"
df.to_csv(csv_file_path, index=False)
