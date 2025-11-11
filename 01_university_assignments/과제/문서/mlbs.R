# 필요한 라이브러리 설치 및 불러오기
install.packages("readxl")
library(readxl)

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
model11 <- lm(LA ~ `LD%` + `FB%`+ `GB%` , data = data)
summary(model11)
model12 <- lm(LA ~ `GB/FB` , data = data)
summary(model12)

