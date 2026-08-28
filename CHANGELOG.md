# 변경 이력

이 프로젝트는 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 따르며
[유의적 버전](https://semver.org/lang/ko/)을 지킵니다.

버전은 git 태그에서 만들어집니다. [VERSIONING.md](./docs/developer/VERSIONING.md) 참고.

## [미출시] — 0.0.1

### 버전 번호 재시작

이 배포판(`vm-stock-kis`)의 **첫 릴리스**입니다. 업스트림 `python-kis` 2.1.6에서
갈라져 나왔지만 배포명이 다르므로 pip이 두 버전을 비교하지 않으며, 번호를
이어받을 이유가 없습니다. `0.0.1`부터 시작합니다.

- 호환 폴백 제거 시점을 `v4.0.0` → **`1.0.0`** 으로 재지정.
- `Development Status` classifier를 `5 - Production/Stable` → **`4 - Beta`** 로
  조정. `0.0.1`과 `Production/Stable`은 함께 설 수 없습니다. `1.0.0`에서
  되돌립니다.

### 변경 (Breaking)

- **배포명·모듈명·클래스명 변경.** `python-kis`/`pykis`/`PyKis` →
  `vm-stock-kis`/`vmkis`/`VmKis`. 환경변수 `PYKIS_*` → `VMKIS_*`,
  작업공간 `~/.pykis` → `~/.vmkis`, User-Agent `PyKis/x.y.z` → `VmKis/x.y.z`.
  마이그레이션은 [MIGRATION_GUIDE.md](./docs/MIGRATION_GUIDE.md) 참고.
- flat 레이아웃에서 src 레이아웃(`src/vmkis/`)으로 이관.

### 추가

- v2.x 호환 폴백 3종. 모두 `DeprecationWarning`을 내며 1.0.0에서 제거합니다.
  - `vmkis.PyKis` — `VmKis`와 동일 객체를 반환하므로 `isinstance` 검사도 동작합니다.
    `__all__`에는 넣지 않았습니다.
  - `~/.pykis` 작업공간 폴백 — 기존 사용자의 토큰 캐시 보존.
  - `PYKIS_*` 환경변수 폴백.
- `SECURITY.md` / `SECURITY.en.md` — 보안 정책 및 자격증명 취급 방식.
- `CHANGELOG.md` (이 파일), `.python-version`, `.github/dependabot.yml`.
- `archive/` — 동결 보관소. 수명이 끝난 문서·코드를 당시 상태 그대로 두는
  자리이며 린트·포맷·이름 스윕·배포 대상에서 제외합니다.
  규칙은 [archive/README.md](./archive/README.md) 참고.
- `publish.yml`에 게시 전 검증 — 태그/버전 일치, `twine check --strict`,
  휠 내용(`py.typed` 포함, `pykis/`·`tests/` 부재), 격리 환경 스모크 테스트.
- `ci.yml`에 `Version sanity`, `uv lock --check`, 브랜치 보호용 `ci-ok` 집계 잡.

### 수정

- **`pyyaml`이 런타임 의존성에 없었습니다.** `vmkis.helpers`가 import하는데
  `[project].dependencies`에 없어, 새로 설치한 사용자는 `create_client`와
  `save_config_interactive`가 조용히 `None`이 됐습니다.
- **`SimpleKIS`가 helpers의 import 실패에 휩쓸려 함께 `None`이 됐습니다.**
  정상 import되는데도 같은 `try` 블록에 묶여 있었습니다. import를 분리하고
  `except`를 `Exception` → `ImportError`로 좁혔습니다.
- `__env__.py`가 `except Exception`으로 모든 오류를 삼키고 하드코딩된
  `"2.1.6+dev"`를 반환했습니다. `PackageNotFoundError`로 좁히고 fallback을
  `"0.0.0+unknown"`으로 바꿨습니다.
- `actions/checkout`의 shallow clone 때문에 hatch-vcs가 태그를 읽지 못해
  버전이 `0.0.0`이 됐습니다. `fetch-depth: 0`을 추가했습니다. 그대로 뒀다면
  태그를 붙여도 버전 `0.0.0`인 휠이 PyPI에 올라갔을 것입니다.
- **테스트 스위트가 약 8개월간 완주한 적이 없었습니다.**
  `tests/unit/test_logging.py`가 구문 오류인 채로 커밋되어 pytest 수집이
  실패하고 있었습니다. 복구 후 드러난 실패 3건을 정리하고 커버리지 게이트를
  70에서 90으로 복원했습니다.
- **CI가 단 한 번도 실행된 적이 없었습니다.** `ci.yml`이 YAML 파싱에 실패해
  (heredoc이 블록 스칼라를 조기 종료) 잡이 생성되지 않았습니다. 재작성했습니다.
- rate limiter 타이밍 테스트가 전체 실행에서만 실패하는 flake였습니다.
- 문서가 자격증명을 "암호화 저장"한다고 서술했으나 실제로는 평문 JSON입니다.
  정정했습니다.
- `.github/ISSUE_TEMPLATE/*`와 `CONTRIBUTING.md`의 링크가 업스트림 저장소를
  가리키고 있었습니다.
- **사용자 문서의 GitHub 링크 19곳이 존재하지 않는 저장소를 가리켰습니다.**
  소유자가 `QuantumOmega`(`docs/FAQ.md`, `examples/tutorial_basic.ipynb`) 또는
  자리표시자 그대로인 `yourusername`(`docs/user/en/**`, `examples/README.md`)
  이었습니다. 이름 스윕이 `python-kis` → `vm-stock-kis`만 바꾸고 소유자는
  그대로 둬서 오히려 그럴듯한 죽은 링크가 됐습니다.
- `docs/NEWSLETTER_TEMPLATE.md`가 서식이 아니라 2025년 12월에 발행된 한 호였고
  옛 이름을 담고 있었습니다. 기록물을 `archive/docs/2025-12_NEWSLETTER.md`로
  분리하고, 그 자리에 실제 빈 서식을 새로 썼습니다.

### 제거

- `publish.yml`의 `{{VERSION_PLACEHOLDER}}` 치환 스텝. 해당 placeholder가
  이미 없어져 조용한 no-op이었습니다.
- `ci.yml`의 죽은 `build` 잡.
- pre-commit의 `black`·`isort` 훅. black의 기본 88자가
  `[tool.ruff] line-length = 120`과 충돌해 두 포매터가 서로의 결과를
  되돌리고 있었습니다.
- 개발 도구 체인에서 Poetry. uv로 통일했습니다.

---

## [2.1.6] 이전

이 포크 이전의 이력은 업스트림
[Soju06/python-kis](https://github.com/Soju06/python-kis)를 참고하세요.
