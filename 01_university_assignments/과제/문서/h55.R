install.packages("readxl")
install.packages("dplyr")
install.packages("lmtest")
library(readxl)
library(dplyr)
library(lmtest)
file_path <- "C:/Users/TJ/Desktop/cg76_123.xlsx"
data <- read_excel(file_path)
data <- data %>%
  mutate(
    ln_cost = log(cost),
    ln_q = log(q),
    ln_l = log(pl),
    ln_k = log(pk),
    ln_f = log(pf)
  )

# 회귀 모델 적합
model <- lm(ln_cost ~ ln_q + ln_l+ln_k+ln_f, data = data)  # ln_cost_share 사용
summary(model)

# 계수들의 합 계산
coefficients <- summary(model)$coefficients
alpha_sum <- sum(coefficients[2:4, 1])  # ln_q, ln_pl, ln_pk, ln_pf의 계수 합산
alpha_sum

# 비용 점유율 합 확인
sum_sl_sk_sf <- mean(data$sl + data$sk + data$sf)
sum_sl_sk_sf
# 이상치 제거를 위한 IQR 방법 사용
Q1 <- quantile(data$cost, 0.25)
Q3 <- quantile(data$cost, 0.75)
IQR <- Q3 - Q1

# 이상치가 아닌 데이터만 필터링
data_filtered <- data %>%
  filter(cost > (Q1 - 1.5 * IQR) & cost < (Q3 + 1.5 * IQR))

# 다시 모델 피팅
model <- lm(ln_cost ~ ln_q + ln_cost_share, data = data)  # ln_cost_share 사용
summary(model)

# 계수들의 합 계산
coefficients_filtered <- summary(model_filtered)$coefficients
alpha_sum_filtered <- sum(coefficients_filtered[2:3, 1])  # ln_q, ln_pl, ln_pk, ln_pf의 계수 합산
alpha_sum_filtered
