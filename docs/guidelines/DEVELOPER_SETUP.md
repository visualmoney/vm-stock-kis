# vm-stock-kis 개발환경 설정 가이드 (Windows)

본 가이드는 `vm-stock-kis` 레포지토리에서 로컬 개발을 시작하기 위한 단계입니다. 이 프로젝트는 `poetry`를 사용합니다.

## 1. 필수 소프트웨어
- Python 3.11 이상 (현재 테스트 환경: 3.12)
- Git
- Poetry
- VS Code (권장)

## 2. 저장소 복제
```powershell
git clone <repo_url> c:\Python\github.com\vm-stock-kis
cd c:\Python\github.com\vm-stock-kis
```

## 3. Poetry 설치 (설치되어 있지 않은 경우)
```powershell
pip install --user poetry
# 또는 choco를 사용하는 경우
choco install poetry -y
```

## 4. 가상환경 생성 및 의존성 설치
프로젝트 루트에서:
```powershell
python -m poetry install --no-interaction --with=test
```
- 위 명령은 개발 및 테스트 의존성을 설치합니다.

## 5. VS Code 설정
- 권장 확장: `Python`, `Pylance`, `PlantUML (jebbs.plantuml)`, `Prettier` 등
- VS Code에서 Python 인터프리터를 Poetry 가상환경으로 설정: `Python: Select Interpreter` → `.venv` 경로 선택

## 6. 테스트 실행
- 전체 테스트 (Poetry를 통해):
```powershell
python -m poetry run pytest
```
- 특정 테스트 파일 실행 예:
```powershell
python -m poetry run pytest tests/unit/responses/test_dynamic_transform.py -q
```

## 7. 코드 스타일/포매팅
- 프로젝트에 포맷터/린터가 설정되어 있으면 해당 명령 사용(예: `black`, `ruff` 등).
- 예시:
```powershell
python -m poetry run black .
python -m poetry run ruff check .
```

## 8. 커밋/브랜치 규칙
- `main` 브랜치는 보호되어 있음(팀 규칙에 따라 다름). 기능별 브랜치에서 작업 후 PR 제출 권장.

## 9. 유용한 명령 모음
```powershell
# 의존성 설치 재실행
python -m poetry install

# 테스트 + 커버리지
python -m poetry run pytest --cov=vmkis --cov-report=html:htmlcov

# 가상환경 셸 접속
python -m poetry shell
```

## 10. 문제해결
- 의존성 문제: `.venv` 삭제 후 `poetry install` 재시도
- 테스트 실패: `python -m poetry run pytest -k <testname> -q`로 좁혀서 디버깅

---
작성자: 자동 생성 가이드
