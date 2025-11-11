import requests

test_url = "https://dapi.kakao.com/v2/local/search/category.json"
test_headers = {
    "Authorization": "KakaoAK " + KAKAO_API_KEY
}
test_params = {
    "category_group_code": "OL7",
    "x": "127.0",  # 서울 중심부 좌표
    "y": "37.5",
    "radius": 3000
}

response = requests.get(test_url, headers=test_headers, params=test_params)
print(f"테스트 응답 코드: {response.status_code}")
print(f"테스트 응답 내용: {response.text}")
