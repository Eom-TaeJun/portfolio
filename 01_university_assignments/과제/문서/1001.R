# 필요한 패키지 설치 및 로드
install.packages("readxl")  # 주석 해제하여 설치합니다.
library(readxl)

# 엑셀 파일 경로 설정
excel_file_path <- "C:/Users/TJ/Desktop/111cement50.xlsx"

# 엑셀 파일 불러오기
data <- read_excel(excel_file_path)

# 데이터 확인
head(data)  # 데이터의 처음 몇 줄을 확인
names(data)  # 데이터 프레임의 열 이름 확인

# q와 p, c의 데이터 유형 확인
class(data$q)  # q의 데이터 유형 확인
class(data$p)  # p의 데이터 유형 확인
class(data$c)  # c의 데이터 유형 확인

# q와 p, c가 NULL인 경우 열 이름을 수정
if ("q" %in% names(data) && "p" %in% names(data) && "c" %in% names(data)) {
  data$q <- as.numeric(data$q)
  data$p <- as.numeric(data$p)
  data$c <- as.numeric(data$c)
  
  # 세 가지 회귀 모델 수행
  model <- lm(q ~ p, data = data)
  model1 <- lm(q ~ c, data = data)
  model2 <- lm(p ~ c, data = data)
  
  # 회귀 분석 결과 요약
  summary(model)
  summary(model1)
  summary(model2)
  
  # 각 모델의 계수 추출
  coef_model <- coef(model)
  coef_model1 <- coef(model1)
  coef_model2 <- coef(model2)
  
  # 결과 출력
  print(coef_model)
  print(coef_model1)
  print(coef_model2)
  
  # 잔차 계산
  resid_model1 <- resid(model1)
  resid_model2 <- resid(model2)
  
  # 잔차를 사용한 회귀 모델
  resid_model <- lm(resid_model1 ~ resid_model2)
  summary(resid_model)
  
  # 수요 탄력성 계산
  data$elasticity <- 1.1 * data$p / data$q
  
  # 수요 탄력성의 요약 통계
  elasticity_summary <- summary(data$elasticity)
  average_elasticity <- mean(data$elasticity, na.rm = TRUE)
  min_elasticity <- min(data$elasticity, na.rm = TRUE)
  max_elasticity <- max(data$elasticity, na.rm = TRUE)
  
  # 결과 출력
  print(elasticity_summary)
  print(paste("Average Elasticity:", average_elasticity))
  print(paste("Min Elasticity:", min_elasticity))
  print(paste("Max Elasticity:", max_elasticity))
  
  # 수요 탄력적인 지점 확인 (수요 탄력성이 1보다 큰 경우)
  data$is_elastic <- data$elasticity > 1
  
  # 수요 탄력적인 지점의 비율
  elastic_proportion <- mean(data$is_elastic, na.rm = TRUE)
  
  # 수요 탄력적인 지점에서 생산하고 있는지 확인
  print(paste("Proportion of Elastic Points:", elastic_proportion))
  
} else {
  print("q, p 또는 c 열이 존재하지 않습니다.")
}

