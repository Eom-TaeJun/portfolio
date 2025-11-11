# 필요한 라이브러리 설치 및 불러오기
install.packages("readxl")
library(readxl)
library(car)
# 엑셀 파일 경로 설정
excel_file_path <- "C:/Users/엄태준/Desktop/mlbs.xlsx"

# 엑셀 파일 불러오기
data <- read_excel(excel_file_path)

# 회귀분석 수행
model <- lm(R ~ H + `2B` + `3B` + HR+ BB + SO + SB + AVG + `GO/AO`, data = data)
model1 <- lm(R ~ H , data = data)
model2 <- lm(R ~ `2B`, data = data)
model3 <- lm(R ~ `3B`, data = data)
model4 <- lm(R ~ HR , data = data)
model5 <- lm(R ~ OBP , data = data)
model6 <- lm(R ~ SLG , data = data)
model7 <- lm(R ~ OPS , data = data)
model8 <- lm(HR ~ `GO/AO` , data = data)
model9 <- lm(R ~ `GO/AO` , data = data)
model10 <- lm(RBI ~ HR , data = data)
model11 <- lm(RBI ~ H , data = data)
model12 <- lm(RBI ~ `2B` , data = data)
model13 <- lm(RBI ~ HIT , data = data)
model14 <- lm(R ~ HIT , data = data)
model15 <- lm(R ~ AVG , data = data)
model16 <- lm(RBI ~ AVG , data = data)
model17 <- lm(RBI ~ HIT+`2B`+`3B`+HR+BB , data = data)
model18 <- lm(R ~ HIT+`2B`+`3B`+HR+BB , data = data)
# 회귀분석 결과 요약
summary(model)
summary(model1)
summary(model2)
summary(model3)
summary(model4)
summary(model5)
summary(model6)
summary(model7)
summary(model8)
summary(model9)
summary(model10)
summary(model11)
summary(model12)
summary(model13)
summary(model14)
summary(model15)
summary(model16)
summary(model17)
summary(model18)


# 필요한 라이브러리 설치 및 불러오기
install.packages("readxl")
library(readxl)

# 엑셀 파일 경로 설정
excel_file_path <- "C:/Users/엄태준/Desktop/mlb30.xlsx"

# 엑셀 파일 불러오기
data <- read_excel(excel_file_path)

# 회귀분석 수행
model1 <- lm(HR ~ Barrels , data = data)
summary(model1)
model2 <- lm(HR ~ Barrelst , data = data)
summary(model2)
model3 <- lm(HR ~ HardHit , data = data)
summary(model3)
model4 <- lm(HR ~ HardHitt , data = data)
summary(model4)
model5 <- lm(AVG ~ HardHit , data = data)
summary(model5)
model6 <- lm(SLG ~ HardHit , data = data)
summary(model6)
model7 <- lm(SLG ~ Barrelst , data = data)
summary(model7)
model8 <- lm(SLG ~ Barrels , data = data)
summary(model8)
model9 <- lm(HR ~ LA , data = data)
summary(model9)

# 필요한 라이브러리 설치 및 불러오기
install.packages("readxl")
library(readxl)

# 엑셀 파일 경로 설정
excel_file_path <- "C:/Users/엄태준/Desktop/mlb2023.xlsx"

# 엑셀 파일 불러오기
data <- read_excel(excel_file_path)

# 회귀분석 수행
model1 <- lm(HR ~ Barrels , data = data)
summary(model1)
model2 <- lm(HR ~ Barrelst , data = data)
summary(model2)
model3 <- lm(HR ~ HardHit , data = data)
summary(model3)
model4 <- lm(HR ~ HardHitt , data = data)
summary(model4)
model5 <- lm(AVG ~ HardHit , data = data)
summary(model5)
model6 <- lm(SLG ~ HardHit , data = data)
summary(model6)
model7 <- lm(SLG ~ Barrelst , data = data)
summary(model7)
model8 <- lm(SLG ~ Barrels , data = data)
summary(model8)
model9 <- lm(HR ~ LA , data = data)
summary(model9)
model10 <- lm(LA ~ `GB/FB` + `LD%` + `FB%`+ `GB%` , data = data)
summary(model10)
model11 <- lm(LA ~ `LD%` + `FB%`, data = data)
summary(model11)
model12 <- lm(LA ~ `LD%` + `FB%`+ `GB/FB`, data = data)
summary(model12)
# 가중치 벡터 생성
model13 <- lm(LA ~ LD + FB , data = data)
summary(model13)

# 엑셀 파일 경로 설정
excel_file_path <- "C:/Users/엄태준/Desktop/mlbla.xlsx"

# 엑셀 파일 불러오기
data <- read_excel(excel_file_path)

# 회귀분석 수행
model1 <- lm(HR ~ Barrels , data = data)
summary(model1)
model2 <- lm(HR ~ Barrelst , data = data)
summary(model2)
model3 <- lm(HR ~ HardHit , data = data)
summary(model3)
model4 <- lm(HR ~ HardHitt , data = data)
summary(model4)
model5 <- lm(AVG ~ HardHit , data = data)
summary(model5)
model6 <- lm(SLG ~ HardHit , data = data)
summary(model6)
model7 <- lm(SLG ~ Barrelst , data = data)
summary(model7)
model8 <- lm(SLG ~ Barrels , data = data)
summary(model8)
model9 <- lm(HR ~ LA , data = data)
summary(model9)
model10 <- lm(LA ~ `GB/FB` + `LD%` + `FB%`+ `GB%` , data = data)
summary(model10)
model11 <- lm(LA ~ `LD%` + `FB%`, data = data)
summary(model11)
model12 <- lm(LA ~ `LD%` + `FB%`+ `GB%`, data = data)
summary(model12)
# 가중치 벡터 생성
model13 <- lm(LA ~ LD + FB , data = data)
summary(model13)

library(readxl)
# 엑셀 파일 경로 설정
excel_file_path <- "C:/Users/엄태준/Desktop/mlblaa.xlsx"

# 엑셀 파일 불러오기
data <- read_excel(excel_file_path)
print(data)

# 회귀분석 수행
model1 <- lm(HR ~ Barrels , data = data)
summary(model1)
model2 <- lm(HR ~ Barrelst , data = data)
summary(model2)
model3 <- lm(HR ~ HardHit , data = data)
summary(model3)
model4 <- lm(HR ~ HardHitt , data = data)
summary(model4)
model5 <- lm(AVG ~ HardHit , data = data)
summary(model5)
model6 <- lm(SLG ~ HardHit , data = data)
summary(model6)
model7 <- lm(SLG ~ Barrelst , data = data)
summary(model7)
model8 <- lm(SLG ~ Barrels , data = data)
summary(model8)
model9 <- lm(HR ~ LA , data = data)
summary(model9)
model10 <- lm(LA ~ `GB/FB` + `LD%` + `FB%`+ `GB%` , data = data)
summary(model10)
model11 <- lm(LA ~ `LD%` + `FB%`, data = data)
summary(model11)
model12 <- lm(LA ~ `LD%` + `FB%`+ `GB/FB`, data = data)
summary(model12)
model13 <- lm(LA ~ `LD%` + `FB%`+`IFFB%`, data = data)
summary(model13)
model14 <- lm(LA ~ `LD%` + `FB%`+`IFFB%` +`HR/FB`, data = data)
summary(model14)
model18 <- lm(LA ~ `LD%` + `FB`+`IFFB%`, data = data)
summary(model18)
model18 <- lm(LA ~ gf+`IFFB%`, data = data)
summary(model18)
model15 <- lm(lam ~ EV, data = data)
summary(model15)
install.packages("car")  # car 패키지가 설치되어 있지 않은 경우 주석 해제 후 설치




# 모델 생성
model16 <- lm(LA ~  `LD%` + `FB%` + `GB%`, data = data)

# VIF 계산
vif_values <- vif(model16)

# VIF 값 출력
print(vif_values)
# 모델 생성 (예시: `FB%` 변수 제거)
model_without_GB <- lm(LA ~ `LD%` + `FB%`, data = data)

# VIF 계산
vif_values_without_GB <- vif(model_without_GB)

# VIF 값 출력
print(vif_values_without_GB)


excel_file_path <- "C:/Users/엄태준/Desktop/mlbho.xlsx"

# 엑셀 파일 불러오기
data <- read_excel(excel_file_path)
print(data)

# 회귀분석 수행
model1 <- lm(la ~ fg+iso , data = data)
summary(model1)
model2 <- lm(la ~ fg , data = data)
summary(model2)
model3 <- lm(la ~ `ib`+gb , data = data)
summary(model3)
model4 <- lm(la ~ `ib`+gb+fb , data = data)
summary(model4)
















install.packages("readxl")
library(readxl)
install.packages("lpSolve")
library(lpSolve)


# 라이브러리 로드
library(lpSolve)
library(readxl)

# 엑셀 데이터 읽어오기 (파일 경로에 주의)
excel_data <- read_excel("C:/Users/엄태준/Desktop/mlbho.xlsx")
print(excel_data)
# 데이터 확인
cat("Head of Excel Data:\n")
head(excel_data)

# 부등식 우변 값 설정
rhs_values <- c(excel_data$la, -excel_data$laa)

# 각 데이터행에 대해 부등식 우변 값이 반복되도록 설정
rhs_values <- rep(rhs_values, each = ncol(excel_data))

# 부등식 우변 값 확인
cat("\nLength of rhs_values:", length(rhs_values), "\n")
print(rhs_values)


# 계수 행렬 확인
cat("\nNumber of rows in coeff_matrix:", nrow(coeff_matrix), "\n")
cat("Number of columns in coeff_matrix:", ncol(coeff_matrix), "\n")
print(coeff_matrix)

# 목적함수 계수 설정 (ib, fb, gb를 최소화하는 것으로 설정)
objective_coefficients <- c(1, 1, 1)

# 최소화 문제 해결
result <- lp("min", objective_coefficients, coeff_matrix, "<=", rhs_values)
result <- lp("min", objective_coefficients, coeff_matrix, "<=", rhs_values)

# 결과 출력
print(result)
# 최적 계수 출력
cat("\nOptimal Coefficients (ib, fb, gb):", result$solution[1:3], "\n")


# 주어진 데이터
data <- data.frame(
  ib = c(0.087, 0.044, 0.096, 0.084, 0.063, 0.019, 0.044, 0.017, 0.015, 0.092),
  gb = c(0.534, 0.487, 0.524, 0.542, 0.549, 0.444, 0.492, 0.486, 0.483, 0.519),
  fb = c(0.183, 0.218, 0.167, 0.186, 0.21, 0.322, 0.271, 0.288, 0.237, 0.233),
  la = c(1, 2, 2, 2, 4, 5, 5, 5, 5, 5),
  laa = c(2, 3, 3, 3, 5, 6, 6, 6, 6, 6)
)

# 선형 회귀 모델의 결과
intercept <- -16.610
coef_ib <- -7.796
coef_gb <- 24.429
coef_fb <- 35.792

# 초기 추정값 설정
initial_guess <- c(-intercept, -coef_ib, -coef_gb, -coef_fb)

# 데이터프레임에 y 열 추가
data$y <- rep(NA, nrow(data))

# 목적 함수 정의
objective_function <- function(params, data) {
  A <- params[1]
  B <- params[2]
  C <- params[3]
  
  data$y <- (data$la < A * data$ib + B * data$gb + C * data$fb) & (A * data$ib + B * data$gb + C * data$fb < data$laa)
  
  return(sum(data$y)^2)
}

# NLS 수행
fit <- nls(
  formula = y ~ objective_function(c(A, B, C), data),
  start = setNames(initial_guess, c("A", "B", "C")),
  algorithm = "port",
  lower = c(0, 0, 0),
  upper = c(Inf, Inf, Inf),
  data = data
)

# 필요한 라이브러리 설치 및 불러오기
if (!require(rgl)) install.packages("rgl", dependencies=TRUE)
library(rgl)

# 부등식의 계수
A <- matrix(c(0.096, 0.524, 0.167,
              0.044, 0.487, 0.218,
              0.087, 0.534, 0.183), ncol = 3, byrow = TRUE)

# 부등식의 우변 상수
b <- c(3, 3, 2)

# 부등식을 만족하는 3차원 공간 그리기
plot3d(z = seq(0, 3, length = 100), y = seq(0, 3, length = 100), x = seq(0, 3, length = 100), type = "n", 
       xlab = "x", ylab = "y", zlab = "z", main = "Feasible Region")

for (i in 1:length(b)) {
  # 부등식의 등식 부분 그리기
  planes3d(a = A[i, 1], b = A[i, 2], c = A[i, 3], d = -b[i], alpha = 0.5, col = i)
  
  # 부등식의 부등호 부분 그리기
  planes3d(a = A[i, 1], b = A[i, 2], c = A[i, 3], d = -b[i], alpha = 0.1, col = i)
}

# 축 범위 설정
rgl.viewpoint(theta = 30, phi = 30, fov = 0, zoom = 0.75)
