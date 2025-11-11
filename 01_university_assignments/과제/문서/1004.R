# 필요한 패키지 설치 및 불러오기
install.packages("readxl")  # 엑셀 파일 읽기
install.packages("ggplot2")  # 그래프 그리기
library(readxl)
library(ggplot2)

# 엑셀 파일 불러오기
file_path <- "C:/Users/TJ/Desktop/111.xlsx"
sheet1_data <- read_excel(file_path, sheet = 1)
sheet2_data <- read_excel(file_path, sheet = 2)
sheet3_data <- read_excel(file_path, sheet = 3)
sheet4_data <- read_excel(file_path, sheet = 4)

# 열 이름 수동으로 변경
colnames(sheet1_data) <- c("Country", "FDI_Outward_Stock_GDP")  # FDI Outward Stock (백만 달러)
colnames(sheet2_data) <- c("Country", "FDI_Inward_Stock_GDP")   # FDI Inward Stock (백만 달러)
colnames(sheet3_data) <- c("Country", "GDP_per_capita")         # GDP per capita (억 달러)
colnames(sheet4_data) <- c("Country", "Population")              # Population

# FDI를 억 달러로 변환 (백만 달러를 억 달러로 변환)
sheet1_data$FDI_Outward_Stock_GDP <- sheet1_data$FDI_Outward_Stock_GDP / 10000
sheet2_data$FDI_Inward_Stock_GDP <- sheet2_data$FDI_Inward_Stock_GDP / 10000

# 교집합 구하기
common_countries <- Reduce(intersect, list(sheet1_data$Country, sheet2_data$Country, sheet3_data$Country, sheet4_data$Country))

# 교집합에 해당하는 국가들만 필터링
sheet1_filtered <- sheet1_data[sheet1_data$Country %in% common_countries, ]
sheet2_filtered <- sheet2_data[sheet2_data$Country %in% common_countries, ]
sheet3_filtered <- sheet3_data[sheet3_data$Country %in% common_countries, ]
sheet4_filtered <- sheet4_data[sheet4_data$Country %in% common_countries, ]

# 데이터 합치기
merged_data <- merge(sheet1_filtered, sheet2_filtered, by = "Country")
merged_data <- merge(merged_data, sheet3_filtered, by = "Country")
merged_data <- merge(merged_data, sheet4_filtered, by = "Country")

# 3번 문제: GDP per capita와 FDI Outward Stock / GDP 비율에 대한 산점도 그리기
ggplot(merged_data, aes(x = GDP_per_capita, y = FDI_Outward_Stock_GDP)) +
  geom_point() +
  labs(title = "GDP per capita vs FDI Outward Stock / GDP",
       x = "GDP per capita (억 달러)", y = "FDI Outward Stock (억 달러)")

# 3번 문제: FDI Inward Stock / GDP 비율에 대한 산점도 그리기
ggplot(merged_data, aes(x = GDP_per_capita, y = FDI_Inward_Stock_GDP)) +
  geom_point() +
  labs(title = "GDP per capita vs FDI Inward Stock / GDP",
       x = "GDP per capita (억 달러)", y = "FDI Inward Stock (억 달러)")

# 4번 문제: 자연 로그 변환
merged_data$log_GDP_per_capita <- log(merged_data$GDP_per_capita)
merged_data$log_FDI_Outward_Stock_GDP <- log(merged_data$FDI_Outward_Stock_GDP)

# 4번 문제: 로그 변환된 변수로 산점도 그리기
ggplot(merged_data, aes(x = log_GDP_per_capita, y = log_FDI_Outward_Stock_GDP)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE, color = "red") +  # 선형 회귀선 추가
  labs(title = "Log(GDP per capita) vs Log(FDI Outward Stock / GDP)",
       x = "Log(GDP per capita)", y = "Log(FDI Outward Stock / GDP)")

# 4번 문제: 선형 회귀 분석 및 결과 확인
model <- lm(log_FDI_Outward_Stock_GDP ~ log_GDP_per_capita, data = merged_data)
summary(model)

