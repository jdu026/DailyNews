import requests
import re
from config import Config


class NewsAPI:
    NAVER_URL = "https://openapi.naver.com/v1/search/news.json"

    def __init__(self):
        self.client_id = Config.NAVER_CLIENT_ID.strip()
        self.client_secret = Config.NAVER_CLIENT_SECRET.strip()

    def _build_headers(self):
        """API 호출에 필요한 HTTP 헤더를 생성합니다."""
        return {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }

    @staticmethod
    def _parse_response(item):
        """API 응답 항목 하나를 정리된 딕셔너리로 파싱합니다."""
        title = re.sub('<[^>]*>', '', item['title'])

        return {
            "title": title,
            "link": item['link']
        }

    def fetch_news(self, keyword, count=3):
        # ✅ 유지할 로그 1: 검색 키워드 시작 알림
        print(f"--- [API 디버그] 키워드 검색 시작: {keyword} ---")

        params = {
            "query": keyword,
            "display": count,
            "start": 1,
            "sort": "sim"
        }
        headers = self._build_headers()

        try:
            response = requests.get(self.NAVER_URL, headers=headers, params=params)

            if response.status_code != 200:
                # HTTP 오류 발생 시 빈 리스트 반환
                return []

            data = response.json()

            item_count = len(data.get('items', []))
            # ✅ 유지할 로그 2: 검색 결과 아이템 수
            print(f"--- [API 디버그] 검색 결과 아이템 수: {item_count}개 ---")

            if item_count == 0:
                return []

            news_list = [self._parse_response(item) for item in data.get('items', [])]
            return news_list

        except requests.exceptions.RequestException as e:
            # 네트워크 오류 시 빈 리스트 반환
            return []