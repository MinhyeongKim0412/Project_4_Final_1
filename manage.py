# manage.py: 프로젝트 진입점 (서버실행, 마이그레이션 수행, 관리 명령어 실행)

import os  # OS 관련 기능을 사용하기 위한 라이브러리
import sys  # 시스템 관련 기능을 사용하기 위한 라이브러리

# main 함수는 이 파일의 핵심 함수로, Django 관리 명령어를 실행하는 역할
def main():
    # Django 프로젝트의 설정 파일을 지정
    # 'config.settings'는 프로젝트의 설정 파일 경로
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        # Django의 명령어 관리 도구를 불러옴
        # 'execute_from_command_line'은 터미널 명령을 실행하는 함수
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # ImportError 발생 시 예외 처리
        # Django가 설치되지 않았거나 PYTHONPATH에 추가되지 않았을 때 발생
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
            # 여기서 발생한 예외(exc)를 상위 예외로 재발생 시킴
        ) from exc

    # 명령줄에서 받은 인자를 기반으로 Django 명령어를 실행
    execute_from_command_line(sys.argv)

# 이 스크립트가 실행될 때(main 함수가 호출되는지 확인하는 블록)
if __name__ == "__main__":
    main()