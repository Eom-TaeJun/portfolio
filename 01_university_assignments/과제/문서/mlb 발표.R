# readxl 패키지 설치
install.packages("readxl")

# readxl 패키지 로드
library(readxl)

# 엑셀 파일 경로 설정
excel_file <- "경로/파일명.xlsx"

# 엑셀 파일 읽기
data <- read_excel("C:/Users/엄태준/Desktop/consumption.xlsx")

# 데이터 확인
str(data)
model <- lm(consumption ~ income + age + asset + edu, data = data)
summary(model)

model <- lm(consumption ~ income + asset + edu, data = data)
summary(model)
model <- lm(consumption ~ I(10 * income+ age) + asset + edu, data = data)
##model <- lm(mid ~ year, data = data)
# 모델 요약
summary(model)

##
library(readxl)
data <- read_excel("C:/Users/엄태준/Desktop/wage.xlsx")
str(data)
# 회귀분석 수행
model <- lm(log(wage) ~ avg_grade , data = data)
model <- lm((wage) ~ avg_grade , data = data)
# 회귀분석 결과 출력
summary(model)

mid <- ifelse(data$firm_size == 3 | data$firm_size == 4, 1, 0) 
large <- ifelse(data$firm_size>4, 1, 0)
model <- lm(log(wage) ~ avg_grade + mid + large , data = data)
summary(model)
mid <- ifelse(data$firm_size == 3 | data$firm_size == 4, 1, 0) 
large <- ifelse(data$firm_size>4, 1, 0)
model <- lm(log(wage) ~ avg_grade + I(mid + large) , data = data)
summary(model)
mid <- ifelse(data$firm_size == 3 | data$firm_size == 4, 1, 0) 
large <- ifelse(data$firm_size>4, 1, 0)
model <- lm(log(wage) ~ avg_grade + sex + mid + large , data = data)
summary(model)




# 필요한 패키지 설치
# install.packages("readxl")
# install.packages("dplyr")

# 필요한 라이브러리 로드
library(readxl)
library(dplyr)

# 엑셀 파일 경로 설정
xlsx_file <- "C:/Users/엄태준/Desktop/war.xlsx"

# 2023 시트 읽어오기
sheet2023 <- readxl::read_excel(xlsx_file, sheet = "2023")

# 회귀분석
model <- lm(AAV ~ Years + Details , data = selected_data)

# 회귀분석 결과 출력
summary(model)

# VIF 계산
library(car)
vif_values <- car::vif(model)
print("VIF Values:")
print(vif_values)

# 이분산성 검정 (Breusch-Pagan Test)
# 이분산성 검정 (White Test)
library(lmtest)
white_test <- bptest(model)
print("White Test for Heteroscedasticity:")
print(white_test)

# 이분산성이 감지되면 FGLS를 사용하여 모델 보정
if (white_test$p.value < 0.05) {
  print("Heteroscedasticity detected. Applying FGLS correction.")
  
  # FGLS를 사용하여 모델 보정
  w <- 1 / residuals(model)^2
  fgls_model <- lm(AAV ~ Years + Details, weights = w)
  
  # 보정된 모델의 요약 출력
  print(summary(fgls_model))
  
  # 보정된 모델에 대한 이분산성 검정
  white_test_fgls <- bptest(fgls_model)
  print("White Test for Heteroscedasticity (FGLS-corrected):")
  print(white_test_fgls)
} else {
  print("No evidence of heteroscedasticity.")
}

# 자기상관 검정 (Durbin-Watson Test)
auto_corr_test <- durbinWatsonTest(model)
print("Autocorrelation Test:")
print(auto_corr_test)

