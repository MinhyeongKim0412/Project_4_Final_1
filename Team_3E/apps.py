from django.apps import AppConfig
import os

class AsdConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Team_3E"

    # 김민형_0930
    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':  # 중복 실행 방지
            import Team_3E.signals
            from . import views
            views.start()  # 앱이 시작될 때 스케줄러도 시작
            # print("스케줄러가 시작되었습니다.")  # 스케줄러 시작 확인용 출력
