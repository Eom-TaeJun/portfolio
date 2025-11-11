# 필요한 패키지 설치 및 불러오기
install.packages("readxl")
install.packages("dplyr")
library(readxl)

# 엑셀 파일 경로 설정 및 파일 불러오기
excel_file_path <- "C:/Users/TJ/Downloads/market.xlsx"
market_data <- read_excel(excel_file_path)
# 데이터 구조 확인
str(market_data)
head(market_data)

# (1) 논문에서 요구한 <표 2>와 <그림 1> 작성하기
# treat에 따른 sc 평균 계산
library(dplyr)
table_2 <- market_data %>%
  group_by(yr, treat) %>%
  summarize(mean_sc = mean(sc, na.rm = TRUE)) %>%
  mutate(mean_sc = round(mean_sc, 5)) # 소수점 5자리까지 표시

print(table_2)

# (그림 1) treat 변수에 따른 sc 변화 시각화
library(ggplot2)
ggplot(market_data, aes(x = factor(yr), y = sc, color = factor(treat))) +
  geom_line(aes(group = treat)) +
  geom_point() +
  labs(title = "그림 1: 대형마트 진입 여부에 따른 신용카드 결제 시행률 변화",
       x = "연도", y = "신용카드 결제 시행률", color = "대형마트 진입 여부") +
  theme_minimal()

