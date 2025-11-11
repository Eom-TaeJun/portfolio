library(readxl)
library(dplyr)
library(ggplot2)
library(gridExtra)

xlsx_file <- "C:/Users/엄태준/Desktop/MLB-Free Agency 1991-2024.xlsx"

# "year" 시트를 제외하고 2012부터 2023까지의 숫자와 year로 지정한 sheet 선택
selected_sheets <- setdiff(c(as.character(1991:2023), "year"), "year")

# Create an empty list to store data frames from each sheet
all_data <- list()
for (sheet_name in selected_sheets) {
  # 각 sheet를 데이터프레임으로 읽기 (14행부터 시작)
  sheet_data <- read_xlsx(xlsx_file, sheet = sheet_name)
  
  # 시트 데이터 확인
  print(paste("Sheet:", sheet_name))
  str(sheet_data)
  
  selected_data <- sheet_data %>% 
    select(Age, Years, Guarantee, AAV) %>%
    mutate(across(where(is.character), as.character),  # 모든 열을 문자열로 변환
           across(everything(), ~ ifelse(is.na(.), 0, .)),  # NA 값을 0으로 대체
           across(where(is.numeric), as.numeric))  # 숫자로 변환
  
  # Years가 0보다 큰 값만 선택
  selected_data <- selected_data %>% 
    filter(Years > 0)
  
  # Guarantee 열이 NA가 아닌 행부터 분석하도록 필터링
  selected_data <- selected_data %>% 
    filter(!is.na(Guarantee))
  
  # Append the selected data frame to the list
  all_data[[sheet_name]] <- selected_data
  
  # 종속변수: Guarantee, 독립변수: Years 회귀 분석
  lm_result_guarantee <- lm(Guarantee ~ Years, data = selected_data)
  
  # 회귀분석 결과 출력
  print(paste("Regression Analysis for Guarantee (Sheet:", sheet_name, ")"))
  print(summary(lm_result_guarantee))
  
  # 종속변수: AAV, 독립변수: Years 회귀 분석
  lm_result_aav <- lm(AAV ~ Years, data = selected_data)
  
  # 회귀분석 결과 출력
  print(paste("Regression Analysis for AAV (Sheet:", sheet_name, ")"))
  print(summary(lm_result_aav))
  
  # 종속변수: Year, 독립변수: Age 회귀 분석
  lm_result_year_age <- lm(Years ~ Age, data = selected_data)
  
  # 회귀분석 결과 출력
  print(paste("Regression Analysis for Year vs Age (Sheet:", sheet_name, ")"))
  print(summary(lm_result_year_age))
  
  # 종속변수: AAV, 독립변수: Years 회귀 분석
  lm_result_AAV <- lm(AAV ~ Age, data = selected_data)
  
  # 회귀분석 결과 출력
  print(paste("Regression Analysis for AAV (Sheet:", sheet_name, ")"))
  print(summary(lm_result_AAV))
}

# Combine all data frames into a single data frame
combined_data <- bind_rows(all_data, .id = "Sheet")

# Perform new analysis on the combined data (replace this with your specific analysis)
new_analysis_result_aav <- lm(AAV ~ Years, data = combined_data)
print("New Analysis Result for AAV:")
print(summary(new_analysis_result_aav))
new_analysis_result_guarantee <- lm(Guarantee ~ Years, data = combined_data)
print("New Analysis Result for Guarantee:")
print(summary(new_analysis_result_guarantee))

new_analysis_result_aavage <- lm(AAV ~ Age, data = combined_data)
print("New Analysis Result for AAV age:")
print(summary(new_analysis_result_aavage))
new_analysis_result_aavage <- lm(Guarantee ~ Age, data = combined_data)
print("New Analysis Result for AAV age:")
print(summary(new_analysis_result_aavage))
new_analysis_result_yearage <- lm(Years ~ Age, data = combined_data)
print("New Analysis Result for Year age:")
print(summary(new_analysis_result_yearage))

# 선형 회귀 모델 생성
lm_model <- lm(AAV ~ Years, data = combined_data)

# 산점도, 선, 추세선(전체 범위) 그리기
ggplot(combined_data, aes(x = Years, y = AAV)) +
  geom_point(aes(color = Sheet), size = 3) +
  geom_line(aes(group = Sheet, color = Sheet), size = 1) +
  geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
  labs(title = "Scatter Plot of AAV vs Years with Lines and Trendline (Subset)",
       x = "Years",
       y = "AAV") +
  theme_minimal()

# 선형 회귀 모델의 계수 출력
summary(lm_model)$coefficients
# 선형 회귀 모델 생성
lm_model1 <- lm(Years ~ Age, data = combined_data)

# 산점도, 선, 추세선(전체 범위) 그리기
ggplot(combined_data, aes(x = Age, y = Years)) +
  geom_point(aes(color = Sheet), size = 3) +
  geom_line(aes(group = Sheet, color = Sheet), size = 1) +
  geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
  labs(title = "Scatter Plot of AAV vs Years with Lines and Trendline (Subset)",
       x = "Age",
       y = "Years") +
  theme_minimal()

# 선형 회귀 모델의 계수 출력
summary(lm_model1)$coefficients

# 최소값을 기준으로 하는 선형 회귀 모델 생성

combined_data1 <- bind_rows(all_data, .id = "Sheet") %>%
  select(Sheet, Age, Years, Guarantee, AAV) %>%
  mutate(across(where(is.character), as.character),  # 모든 열을 문자열로 변환
         across(everything(), ~ ifelse(. == 0, min(.[. != 0], na.rm = TRUE), .)),  # 0을 0이 아닌 값 중 최솟값으로 대체
         across(where(is.numeric), as.numeric))  # 숫자로 변환

# 최소값을 기준으로 하는 선형 회귀 모델 생성
min_age <- min(combined_data1$Age[combined_data1$Age != 0])
lm_model_min <- lm(Years ~ I(Age - min_age), data = combined_data1)
summary(lm_model_min)$coefficients
print(lm_model_min)

# 산점도, 선, 추세선(전체 범위) 그리기 (combined_data1 사용)
ggplot(combined_data1, aes(x = Age - min_age, y = Years)) +
  geom_point(aes(color = Sheet), size = 3) +
  geom_line(aes(group = Sheet, color = Sheet), size = 1) +
  geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
  geom_smooth(aes(x = I(Age - min_age)), 
              method = "lm", 
              se = FALSE, 
              color = "red", 
              linetype = "dashed") +
  labs(title = "Scatter Plot of AAV vs Years with Lines and Trendline (Subset)",
       x = "Age",
       y = "Years") +
  theme_minimal()
str(combined_data1)
print(min_age)


# 데이터에서 Years가 0보다 크고 Age가 정수인 경우만 선택
cleaned_data <- combined_data1 %>%
  filter(Years >= 0, !is.na(as.integer(Age)))

# 새로운 데이터에 대한 분석 수행
lm_model_cleaned <- lm(Years ~ I(40 - Age), data = cleaned_data)
summary(lm_model_cleaned)$coefficients
print(lm_model_cleaned)

# 산점도, 선, 추세선(전체 범위) 그리기
ggplot(cleaned_data, aes(x = 40 - as.integer(Age), y = Years)) +
  geom_point(aes(color = Sheet), size = 3) +
  geom_line(aes(group = Sheet, color = Sheet), size = 1) +
  geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
  geom_smooth(aes(x = I(40 - as.integer(Age))), 
              method = "lm", 
              se = FALSE, 
              color = "red", 
              linetype = "dashed") +
  labs(title = "Scatter Plot of AAV vs Years with Lines and Trendline (Subset)",
       x = "Age",
       y = "Years") +
  theme_minimal()
print(min_age)
# Create an empty list to store ggplot objects for each sheet
gg_list <- list()

# 각 sheet를 읽어와서 분석 수행
for (sheet_name in selected_sheets) {
  # 각 sheet를 데이터프레임으로 읽기 (14행부터 시작)
  sheet_data <- read_xlsx(xlsx_file, sheet = sheet_name)
  
  # 시트 데이터 확인
  print(paste("Sheet:", sheet_name))
  str(sheet_data)
  
  selected_data <- sheet_data %>% 
    select(Age, Years, Guarantee, AAV) %>%
    mutate(across(where(is.character), as.character),  # 모든 열을 문자열로 변환
           across(everything(), ~ ifelse(is.na(.), 0, .)),  # NA 값을 0으로 대체
           across(where(is.numeric), as.numeric))  # 숫자로 변환
  
  # Years가 0보다 큰 값만 선택
  selected_data <- selected_data %>% 
    filter(Years > 0)
  
  # Guarantee 열이 NA가 아닌 행부터 분석하도록 필터링
  selected_data <- selected_data %>% 
    filter(!is.na(Guarantee))
  
  # 산점도, 선, 추세선 그리기 (단위를 1로 변환)
  gg <- ggplot(selected_data, aes(x = Years, y = AAV / 1e6)) +
    geom_point(aes(color = Years), size = 3) +  # 여기서 color aesthetic를 수정
    geom_line(aes(group = Years, color = Years), size = 1) +  # 여기서 color aesthetic를 수정
    geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
    labs(title = paste("Scatter Plot of AAV vs Years with Lines and Trendline -", sheet_name),
         x = "Years",
         y = "AAV (1e6)") +
    theme_minimal()
  
  # Append ggplot object to the list
  gg_list[[sheet_name]] <- gg
}

# 그래프 출력
grid.arrange(grobs = gg_list, ncol = 3)



# 선형 회귀 모델 생성
lm_model <- lm(Guarantee ~ Years, data = combined_data)

# 산점도, 선, 추세선(전체 범위) 그리기
ggplot(combined_data, aes(x = Years, y = Guarantee)) +
  geom_point(aes(color = Sheet), size = 3) +
  geom_line(aes(group = Sheet, color = Sheet), size = 1) +
  geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
  labs(title = "Scatter Plot of Guarantee vs Years with Lines and Trendline (Subset)",
       x = "Years",
       y = "Guarantee") +
  theme_minimal()

# 선형 회귀 모델의 계수 출력
summary(lm_model)$coefficients

# Create an empty list to store data frames from each sheet
all_data <- list()

# Create an empty list to store ggplot objects for each sheet
gg_list <- list()

# 각 sheet를 읽어와서 분석 수행
for (sheet_name in selected_sheets) {
  # 각 sheet를 데이터프레임으로 읽기 (14행부터 시작)
  sheet_data <- read_xlsx(xlsx_file, sheet = sheet_name)
  
  # 시트 데이터 확인
  print(paste("Sheet:", sheet_name))
  str(sheet_data)
  
  selected_data <- sheet_data %>% 
    select(Age, Years, Guarantee, AAV) %>%
    mutate(across(where(is.character), as.character),  # 모든 열을 문자열로 변환
           across(everything(), ~ ifelse(is.na(.), 0, .)),  # NA 값을 0으로 대체
           across(where(is.numeric), as.numeric))  # 숫자로 변환
  
  # Years가 0보다 큰 값만 선택
  selected_data <- selected_data %>% 
    filter(Years > 0)
  
  
  library(readxl)
  library(dplyr)
  library(ggplot2)
  library(gridExtra)
  
  xlsx_file <- "C:/Users/엄태준/Desktop/MLB-Free Agency 1991-2024.xlsx"
  
  # "year" 시트를 제외하고 2012부터 2023까지의 숫자와 year로 지정한 sheet 선택
  selected_sheets <- setdiff(c(as.character(2020:2023), "year"), "year")
  
  # Create an empty list to store data frames from each sheet
  all_data <- list()
  
  # Create an empty list to store ggplot objects for each sheet
  gg_list <- list()
  
  for (sheet_name in selected_sheets) {
    # 각 sheet를 데이터프레임으로 읽기 (14행부터 시작)
    sheet_data <- read_xlsx(xlsx_file, sheet = sheet_name)
    
    # 시트 데이터 확인
    print(paste("Sheet:", sheet_name))
    str(sheet_data)
    
    selected_data <- sheet_data %>% 
      select(Age, Years, Guarantee, AAV) %>%
      mutate(across(where(is.character), as.character),  # 모든 열을 문자열로 변환
             across(everything(), ~ ifelse(is.na(.), 0, .)),  # NA 값을 0으로 대체
             across(where(is.numeric), as.numeric))  # 숫자로 변환
    
    # Years가 0보다 크고 Age가 정수인 경우만 선택
    selected_data <- selected_data %>%
      filter(Years > 0, !is.na(as.integer(Age)))
    
    # Guarantee 열이 NA가 아닌 행부터 분석하도록 필터링
    selected_data <- selected_data %>% 
      filter(!is.na(Guarantee))
    
    # Append the selected data frame to the list
    all_data[[sheet_name]] <- selected_data
    
    # 종속변수: Guarantee, 독립변수: Years 회귀 분석
    lm_result_guarantee <- lm(Guarantee ~ Years, data = selected_data)
    
    # 회귀분석 결과 출력
    print(paste("Regression Analysis for Guarantee (Sheet:", sheet_name, ")"))
    print(summary(lm_result_guarantee))
    
    # 종속변수: AAV, 독립변수: Years 회귀 분석
    lm_result_aav <- lm(AAV ~ Years, data = selected_data)
    
    # 회귀분석 결과 출력
    print(paste("Regression Analysis for AAV (Sheet:", sheet_name, ")"))
    print(summary(lm_result_aav))
    
    # 종속변수: Year, 독립변수: Age 회귀 분석
    lm_result_year_age <- lm(Years ~ Age, data = selected_data)
    
    # 회귀분석 결과 출력
    print(paste("Regression Analysis for Year vs Age (Sheet:", sheet_name, ")"))
    print(summary(lm_result_year_age))
    
    # 종속변수: AAV, 독립변수: Years 회귀 분석
    lm_result_AAV <- lm(AAV ~ Age, data = selected_data)
    
    # 회귀분석 결과 출력
    print(paste("Regression Analysis for AAV (Sheet:", sheet_name, ")"))
    print(summary(lm_result_AAV))
    
    # 산점도, 선, 추세선 그리기 (단위를 1로 변환)
    gg <- ggplot(selected_data, aes(x = Years, y = AAV / 1e6)) +
      geom_point(aes(color = Years), size = 3) +
      geom_line(aes(group = Years, color = Years), size = 1) +
      geom_smooth(method = "lm", se = FALSE, color = "black", linetype = "dashed") +
      labs(title = paste("Scatter Plot of AAV vs Years with Lines and Trendline -", sheet_name),
           x = "Years",
           y = "AAV (1e6)") +
      theme_minimal()
    
    # Append ggplot object to the list
    gg_list[[sheet_name]] <- gg
  }
  
  # 그래프 출력
  grid.arrange(grobs = gg_list, ncol = 3)

  
  