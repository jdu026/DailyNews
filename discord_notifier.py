import requests

class DiscordNotifier:
    def _format_message(self, news_list, keyword):
        """뉴스 목록을 디스코드 Markdown 형식의 문자열로 변환합니다."""
        if not news_list:
            return f"🚨 키워드 **'{keyword}'**에 대한 최신 뉴스가 없습니다."

        message = f"📰 **[{keyword}] 최신 뉴스 알림** 📰\n\n"

        for i, news in enumerate(news_list, 1):
            # 디스코드 Markdown을 사용하여 굵은 글씨와 링크를 추가
            message += f"**{i}. {news['title']}**\n"
            message += f"[자세히 보기]({news['link']})\n\n"

        message += "---"
        return message

    def send_notification(self, webhook_url, news_list, keyword):
        """디스코드 웹훅으로 최종 메시지를 전송합니다."""
        content = self._format_message(news_list, keyword)

        payload = {
            "content": content
        }

        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            print(f"디스코드 알림 전송 성공: {webhook_url}")
            return True
        except requests.exceptions.RequestException as e:
            # 웹훅 전송 오류 처리
            print(f"디스코드 웹훅 전송 오류 발생 ({webhook_url}): {e}")
            return False