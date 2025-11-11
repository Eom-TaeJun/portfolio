from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ChromeOptions 설정
options = Options()
options.add_argument('--headless')  # 필요에 따라 headless 모드 사용
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# ChromeDriverManager로 WebDriver 경로 자동 관리
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 드라이버 사용 예시
driver.get("https://www.google.com")
print(driver.title)
driver.quit()

