# 동적 버저닝 시스템 (Dynamic Versioning)

이 문서는 VM-Stock-KIS의 현재 버전 관리 방식(현행)과 개선 방향(권장)을 설명합니다.

---

## 목표
- 릴리스 자동화: Git 태그 기반으로 버전을 자동 주입
- 일관성: 소스(`src/vmkis/__env__.py`), 배포 메타데이터(`pyproject.toml`), 배포 아티팩트(휠/SDist) 간 동일 버전 보장
- 단순화: 수동 버전 갱신 제거 및 CI에서 재현 가능

---

## 요약

| 옵션 | 빌드 경로 | 버전 소스(SoT) | 주요 장점 | 주요 단점 | 권장 상황 |
|---|---|---|---|---|---|
| A (setuptools-scm) | `python -m build` (PEP 517, setuptools) | Git 태그 (`setuptools-scm`) | 단일 소스, placeholder 제거, 런타임/배포 자동 일치 | `poetry build` 비호환, VCS 메타 필요, 태그 없을 때 fallback 버전 처리 필요 | Poetry 빌드 의존이 약하고 표준 PEP 517 빌드를 선호할 때 |
| B (현행 + CI 검사) | `poetry build` | `__env__.py` CI 치환 | 변경 최소, 즉시 적용 | 이중 관리 지속, 치환/검증 스크립트 유지 비용 | 단기 유지/긴급 릴리스 안정화 필요 시 |
| C (Poetry 플러그인) | `poetry build` | 플러그인(`poetry-dynamic-versioning`) | Poetry 단일 경로, 태그→버전 자동화 | 플러그인 의존, 설정 충돌 시 정리 필요 | 팀이 Poetry에 표준화되어 있고 플러그인 사용 허용 시 |
| D (Poetry, CI 주입) | `poetry build` | CI 태그→PEP 440 정규화 후 `poetry version` | 플러그인 비의존, CI 제어 용이 | 정규화 스크립트 유지, 비태그 정책 정의 필요 | CI 규율 강하고 플러그인 사용을 피하려는 경우 |

## 현행 설계

### 구성 요소
- `pyproject.toml`
  - `[project] dynamic = ["version"]`
  - `[tool.setuptools.dynamic] version = { attr = "vmkis.__env__.__version__" }`
- `src/vmkis/__env__.py`
  - `VERSION = "{{VERSION_PLACEHOLDER}}"` (CI에서 태그로 대체)
  - `__version__ = VERSION`
- `setuptools-scm` (build-system에 선언)
  - 현재는 직접 사용하지 않음(참조만 있음)
- `tool.poetry.version = "2.1.6"`
  - Poetry 메타 전용(실제 배포 버전과 불일치 가능)

### 동작 흐름
1. 개발 중: `__env__.py` 내 `VERSION`은 `24+dev`로 동작 (placeholder 미치환)
2. 릴리스 태그(v2.2.0 등) 생성 → CI에서 `VERSION_PLACEHOLDER`를 태그 값으로 치환
3. `pip build`/`poetry build` 시 `[tool.setuptools.dynamic]`이 `vmkis.__env__.__version__`를 읽어 프로젝트 버전 사용

### 장단점
- 장점: 단일 소스(`__env__.py`)에서 런타임과 배포 메타 버전을 동기화
- 단점:
  - `tool.poetry.version`과의 이중 관리 위험
  - Git 태그가 없을 때 버전 추론 불가 (개발 스냅샷은 `24+dev` 고정)
  - `setuptools-scm` 미활용 (잠재적 자동화 기회 미사용)

---

## 개선 방향 (권장 아키텍처)

### 옵션 A: setuptools-scm 기반 단일 소스 (권장)
- 원칙: "Git 태그 = 단일 진실 공급원(SoT)"
- 구성:
  - `pyproject.toml`
    - `[project] dynamic = ["version"]`
    - `setuptools-scm` 활성(기본값) → Git 태그에서 버전 자동 추론
  - `src/vmkis/__env__.py`
    - `from importlib.metadata import version as _dist_version`
    - `__version__ = _dist_version("vm-stock-kis")`
    - 개발 환경(소스 실행)에서는 `try/except`로 `setuptools_scm.get_version()` fallback 사용
- 이점:
  - 태그만으로 배포 버전, 런타임 버전 자동 일치
  - placeholder 치환 스텝 제거(단순화)

#### 단점 (A안)
- `poetry build`와 직접 호환되지 않음: `[tool.poetry].version` 제거 시 Poetry는 빌드 버전을 요구하여 실패함. 순수 A안은 `python -m build`로 빌드 경로 전환 필요.
- VCS 메타데이터 의존: 태그/커밋 정보가 없거나 소스가 VCS 외부로 추출된 경우 버전 추론이 어려워 `0.0.0+unknown` 같은 fallback을 쓸 수 있음.
- 도구체인 혼합 관리 비용: Poetry를 의존하는 다른 워크플로(예: `poetry install`)와 빌드 체인이 분리되며, 설정 충돌을 피하기 위한 정리(불필요한 `[tool.poetry].version` 제거 등)가 필요.
- 로컬 비태그 개발 버전 정책 필요: 태그가 없는 브랜치에서의 버전 표기(`+devN`, `+dirty`) 허용/노출 정책을 문서화해야 일관성이 유지됨.

#### Poetry 빌드 호환성 (검토 결과 반영)
- 확인된 사실: `[tool.poetry].version`를 제거한 상태에서 `poetry build`를 실행하면 다음 오류로 빌드가 실패합니다.
  - 메시지: "Either [project.version] or [tool.poetry.version] is required in package mode."
- 결론: 옵션 A를 채택하면서 동시에 `poetry build`를 계속 사용할 수는 없습니다. 선택지는 두 가지입니다.
  1) 빌드 경로를 Poetry에서 PEP 517 표준 빌드로 전환합니다.
     - 권장 명령: `python -m build` (또는 `pipx run build`)
     - 이 경로에서는 `[project] dynamic`과 `setuptools-scm`가 버전을 해결하며, `[tool.poetry].version`이 없어도 문제가 없습니다.
  2) 계속 Poetry를 사용할 경우에는 옵션 A가 아닌 옵션 C(플러그인) 또는 옵션 D(CI 주입)로 버전을 `tool.poetry.version`에 설정해야 합니다.
     - 옵션 C: `poetry-dynamic-versioning` 플러그인으로 태그→버전 자동화
     - 옵션 D: CI에서 태그를 PEP 440으로 정규화 후 `poetry version`으로 주입

#### 권장 빌드 경로 (옵션 A를 순수 적용 시)
- 로컬/CI 공통:
  - `pipx install build`
  - `python -m build`
- CI에서 태그가 없는 커밋에 대해선 `setuptools-scm`의 `+devN`/`+dirty` 형식 허용 정책을 문서화합니다.

### 옵션 B: 현재 구조 유지 + CI 정합성 검사 추가
- CI에서 다음을 보장:
  - 태그 `vX.Y.Z` → `__env__.py` 치환 → 빌드 후 휠 `Metadata-Version` 확인
  - `tool.poetry.version`를 태그와 자동 동기화(커밋)
- 이점: 변경 최소화, 즉시 적용 가능
- 단점: 치환 스크립트/커밋 오버헤드 지속

---

### 옵션 C: Poetry 중심 빌드/배포 (플러그인 기반)

Poetry를 주 빌드/배포 도구로 사용하는 현 상황을 반영하여, 버전을 Git 태그에서 자동으로 주입하는 접근입니다.

**권장 플러그인**: `poetry-dynamic-versioning`

- 기능: Git 태그에서 버전을 추출하여 `tool.poetry.version`을 동적으로 설정
- 장점:
  - Poetry 단일 경로로 메타데이터 관리 (간결성)
  - 태그만으로 버전 일치 자동화 (CI/로컬 모두 유효)
  - `__env__.py` placeholder 제거 가능 (A안과 유사한 단순화)
- 단점:
  - 플러그인 의존성 추가
  - setuptools 기반 동적 버전과 중복 설정 시 충돌 위험 → 한 경로만 유지 필요

**도입 절차**:

1) 플러그인 설치

```bash
poetry self add poetry-dynamic-versioning
poetry self show poetry-dynamic-versioning
```

2) 설정 추가 (`pyproject.toml`)

```toml
[tool.poetry]
version = "0.0.0"  # placeholder, 실제 버전은 태그에서 주입

[tool.poetry-dynamic-versioning]
enable = true
vcs = "git"
style = "pep440"
strict = true
tagged-metadata = true
```

3) 코드 측 (선택)

`src/vmkis/__env__.py`에서 런타임 버전을 배포 메타에서 읽도록 단순화:

```python
from importlib.metadata import version as _dist_version
__version__ = _dist_version("vm-stock-kis")
```

4) CI 반영

- 태그 푸시 시 `poetry build` 실행 → 플러그인이 태그를 버전으로 사용
- 비태그 브랜치: `strict=false`로 설정하거나, 사전 릴리스 규칙(`+devN`) 지정

**권고사항**:

- 옵션 C를 채택하는 경우, `[build-system]`의 `setuptools-dynamic` 경로는 제거하여 단일 경로(Poetry)만 사용합니다.
- 문서에 "버전은 Git 태그로 관리한다"를 명시하고, 태그 없이 배포 금지 규칙을 CI로 enforce 합니다.

#### 개발 버전(.devN) 운영 가이드 (옵션 C)
- 원칙: 개발/프리뷰 버전은 Git "프리릴리스 태그"로 표기한 뒤 플러그인이 이를 PEP 440 형식으로 변환합니다.
- 태그 포맷 규칙(권장):
  - `vX.Y.Z-dev.N` → `X.Y.Z.devN`
  - `vX.Y.Z-rc.N` → `X.Y.ZrcN`
  - `vX.Y.Z-beta.N` → `X.Y.ZbN`
  - `vX.Y.Z-alpha.N` → `X.Y.ZaN`
- 플러그인 설정(예시):

```toml
[tool.poetry]
version = "0.0.0"  # placeholder, 실제 버전은 태그에서 주입

[tool.poetry-dynamic-versioning]
enable = true
vcs = "git"
style = "pep440"
strict = true       # 태그가 없으면 빌드 실패로 처리(권장)
tagged-metadata = true
```

- 개발자 워크플로(예시):
  1) 다음 릴리스 기반으로 개발 프리뷰 태그 생성

```bash
git tag v2.3.0-dev.1
git push origin v2.3.0-dev.1
```

  2) CI가 태그로 트리거되어 `poetry build` 실행, 플러그인이 `2.3.0.dev1`을 주입
  3) 개발/프리뷰 태그는 TestPyPI로만 게시, 정식 태그(`vX.Y.Z`)만 PyPI 게시

- 로컬 개발 빌드(태그 없이):
  - 팀 규칙상 태그를 요구하지만, 임시 스냅샷이 필요하면 아래 중 하나를 사용합니다(배포 금지).
    - 임시로 `strict = false`로 낮춰 로컬 빌드만 수행(버전 자동화는 환경에 따라 달라질 수 있음).
    - 또는 로컬에서 수동으로 `poetry version "X.Y.Z.devN"` 실행 후 빌드(변경사항 커밋 금지).

- CI 예시(프리릴리스 태그 분기):

```yaml
jobs:
  build-and-publish:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install Poetry
        run: pipx install poetry
      - name: Install deps
        run: poetry install --no-interaction --with=dev
      - name: Build
        run: poetry build
      - name: Decide publish target
        id: target
        shell: bash
        run: |
          TAG="${GITHUB_REF_NAME}"
          if [[ "$TAG" == *"-dev."* || "$TAG" == *"-alpha."* || "$TAG" == *"-beta."* || "$TAG" == *"-rc."* ]]; then
            echo "name=testpypi" >> "$GITHUB_OUTPUT"
          else
            echo "name=pypi" >> "$GITHUB_OUTPUT"
          fi
      - name: Configure repository
        shell: bash
        run: |
          if [ "${{ steps.target.outputs.name }}" = "testpypi" ]; then
            poetry config repositories.testpypi https://test.pypi.org/legacy/
            poetry config pypi-token.testpypi "${{ secrets.TESTPYPI_TOKEN }}"
          else
            poetry config pypi-token.pypi "${{ secrets.PYPI_TOKEN }}"
          fi
      - name: Publish
        shell: bash
        run: |
          if [ "${{ steps.target.outputs.name }}" = "testpypi" ]; then
            poetry publish -r testpypi
          else
            poetry publish
          fi
```

- 문서화 체크리스트(개발자용):
  - [ ] 프리릴리스/개발 태그 표기 규칙을 팀 컨벤션으로 고정(`-dev.N`, `-alpha.N`, `-beta.N`, `-rc.N`).
  - [ ] 정식 릴리스 태그(`vX.Y.Z`)만 PyPI로 게시, 프리릴리스 태그는 TestPyPI로 게시.
  - [ ] 로컬 스냅샷은 배포 금지, 필요 시 `poetry version "X.Y.Z.devN"`로 일시 버전 지정 후 빌드.
  - [ ] 플러그인 설정은 `strict=true`로 유지해 태그 없는 빌드가 CI에서 통과하지 않도록 함.

---

### 옵션 D: Poetry 호환(플러그인 없이), 태그→PEP 440 정규화

플러그인 없이 CI에서 Git 태그를 PEP 440 규칙으로 정규화하여 `poetry version`에 주입하는 방법입니다.

**원칙**:
- Git 태그를 단일 진실 공급원(SoT)으로 사용
- 태그 표기 → PEP 440 매핑 규칙을 CI 스크립트로 정의
- 런타임 버전은 배포 메타에서 읽음 (`importlib.metadata.version("vm-stock-kis")`)

**태그→PEP 440 매핑 예시**:
- `v1.2.3` → `1.2.3`
- `v1.2.3-rc.1` → `1.2.3rc1`
- `v1.2.3-beta.2` → `1.2.3b2`
- `v1.2.3-alpha.1` → `1.2.3a1`
- `v1.2.3-dev.4` → `1.2.3.dev4`

**CI 단계(샘플)**:

```yaml
jobs:
  build:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install Poetry
        run: pipx install poetry
      - name: Set version from Git tag (PEP 440 normalize)
        shell: bash
        run: |
          raw="${GITHUB_REF_NAME#v}"
          pep="${raw//-rc./rc}"
          pep="${pep//-alpha./a}"
          pep="${pep//-beta./b}"
          pep="${pep//-dev./.dev}"
          echo "Normalized tag: $pep"
          poetry version "$pep"
      - name: Install deps
        run: poetry install --no-interaction --with=dev
      - name: Build
        run: poetry build
```

**장점**:
- Poetry만으로 버전 주입(플러그인 비의존), CI 제어 용이, PEP 440 준수

**단점**:
- 매핑 스크립트 유지 필요, 비태그 커밋의 버전 정책(예: 빌드 금지 또는 `.devN`) 별도 정의 필요

**도입 시 권장 조치**:
- `src/vmkis/__env__.py`는 `importlib.metadata.version()` 기반으로 단순화
- 태그 없는 빌드는 릴리스 배포 금지, 필요시 프리뷰 빌드 규칙 문서화

#### 비태그 커밋 버전 정책 (예시)
- 원칙: 태그가 없는 커밋은 PyPI 정식 배포 대상이 아니며, 내부 검증/아티팩트 업로드만 수행.
- `main` 브랜치:
  - 기준 버전: 최근 태그 `vX.Y.Z`를 기반으로 `X.Y.Z.devN` (N = 최근 태그 이후 커밋 수)
  - 예: 최근 태그 `v2.2.0`, 커밋 수 5 → `2.2.0.dev5`
- 기능 브랜치(feature/*):
  - 기준 버전: 최근 태그 `X.Y.Z.dev<runNumber>-<shortSHA>` (내부 식별 목적, PyPI 업로드 금지)
  - 예: `2.2.0.dev143-abc1234`
- 야간/스냅샷(nightly):
  - 기준 버전: `X.Y.Z.dev<YYYYMMDDHH>` (빌드 타임스탬프 기반)
  - 예: `2.2.0.dev20251220`

샘플 CI (비태그 push 시 dev 버전 적용):

```yaml
jobs:
  build-dev:
    if: startsWith(github.ref, 'refs/heads/') && !startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install Poetry
        run: pipx install poetry
      - name: Compute dev version from latest tag
        shell: bash
        run: |
          tag="$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || echo 'v0.0.0')"
          base="${tag#v}"
          count="$(git rev-list "$tag"..HEAD --count 2>/dev/null || echo 0)"
          pep="${base}.dev${count}"
          echo "Dev version: $pep"
          poetry version "$pep"
      - name: Install deps
        run: poetry install --no-interaction --with=dev
      - name: Build (artifact only)
        run: poetry build
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: vm-stock-kis-dev-dist
          path: dist/*
```

기능 브랜치용 예시(간단한 식별자 포함):

```yaml
      - name: Compute dev version with branch+sha
        shell: bash
        run: |
          tag="$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || echo 'v0.0.0')"
          base="${tag#v}"
          runnum="${GITHUB_RUN_NUMBER}"
          sha="$(git rev-parse --short HEAD)"
          pep="${base}.dev${runnum}-${sha}"
          poetry version "$pep"
```

야간/스냅샷 버전 예시(타임스탬프 기반):

```yaml
      - name: Compute nightly dev version
        shell: bash
        run: |
          tag="$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || echo 'v0.0.0')"
          base="${tag#v}"
          ts="$(date +%Y%m%d%H%M)"
          pep="${base}.dev${ts}"
          poetry version "$pep"
```

#### 프리뷰 빌드 규칙 (예시)
- 원칙: 프리뷰는 정식 PyPI가 아닌 TestPyPI로만 배포.
- 버전 표기: 릴리스 후보/베타/알파 형태 사용(PEP 440), 예: `X.Y.Zrc1`, `X.Y.Zb2`, `X.Y.Za1`.
- 태그 기준이 아닌 경우에는 베타 번호를 CI 러닝 넘버로 매핑하여 일관성을 유지.

샘플 CI (비태그 프리뷰, TestPyPI 게시):

```yaml
jobs:
  preview:
    if: startsWith(github.ref, 'refs/heads/') && !startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install Poetry
        run: pipx install poetry
      - name: Set preview version (beta)
        shell: bash
        run: |
          tag="$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || echo 'v0.0.0')"
          base="${tag#v}"
          pep="${base}b${GITHUB_RUN_NUMBER}"
          echo "Preview version: $pep"
          poetry version "$pep"
      - name: Install deps
        run: poetry install --no-interaction --with=dev
      - name: Build
        run: poetry build
      - name: Configure TestPyPI
        run: |
          poetry config repositories.testpypi https://test.pypi.org/legacy/
          poetry config pypi-token.testpypi "${{ secrets.TESTPYPI_TOKEN }}"
      - name: Publish to TestPyPI
        run: poetry publish -r testpypi
```

문서화 체크리스트(권장):
- [ ] `main`/기능/야간 빌드별 버전 표기 규칙 고정(예시 중 하나 선택)
- [ ] 비태그 빌드는 PyPI 비공개(금지), 아티팩트 업로드 대상만 명시
- [ ] 프리뷰는 TestPyPI로 게시하고 토큰/레포 설정을 보안 변수로 관리
- [ ] 태그 기반 릴리스와의 충돌 방지를 위해 pre-release 번호(bN/aN/rcN) 정책 명확화

## 구현 가이드

### A안 (setuptools-scm 전환) 구현 체크리스트
- [ ] `src/vmkis/__env__.py`에서 placeholder 제거 및 `setuptools_scm` fallback 추가
- [ ] CI에서 태그가 없는 커밋은 `+devN` 형태 버전 허용
- [ ] `tool.poetry.version` 제거(또는 문서화: 관리 대상 아님)
- [ ] 배포 전 `git tag` 강제

추가(빌드 경로 명시):
- [ ] 빌드는 `python -m build`(PEP 517)로 수행하고, `poetry build`는 사용하지 않음

샘플 코드(`src/vmkis/__env__.py`):
```python
try:
    from importlib.metadata import version as _dist_version
    __version__ = _dist_version("vm-stock-kis")
except Exception:
    try:
        from setuptools_scm import get_version
        __version__ = get_version(root="..", relative_to=__file__)
    except Exception:
        __version__ = "0.0.0+unknown"
```

### B안 (현행 유지) 보강 체크리스트
- [ ] CI: 태그 파싱(`vX.Y.Z`) → `__env__.py` placeholder 치환 → 빌드
- [ ] CI: 빌드 산출물의 버전과 태그 일치 검사
- [ ] CI: `pyproject.toml`의 `tool.poetry.version` 자동 동기화 커밋(Optional)

치환 스텝 예시(GitHub Actions):
```bash
$tag=${GITHUB_REF_NAME#v}
python - <<'PY'
from pathlib import Path
p=Path('src/vmkis/__env__.py')
s=p.read_text(encoding='utf-8')
s=s.replace('{{VERSION_PLACEHOLDER}}', '${tag}')
p.write_text(s, encoding='utf-8')
print('Set version to', '${tag}')
PY
```

---

## CI 파이프라인 반영(요약)
- 테스트: `pytest -m "not requires_api" --cov --cov-report=xml`
- 커버리지: `--cov-fail-under=90` 또는 리포터만 업로드 후 대시보드 정책으로 관리
- 아티팩트: `reports/coverage.xml`, `reports/test_report.html` 업로드
- 릴리스(태그): 버전 치환/검증 → `poetry build` → (선택) PyPI 공개

---

## FAQ
- Q: Poetry의 `tool.poetry.version`은 어떻게 하나요?
  - A: 배포 버전은 `[project]/setuptools` 기준으로 관리합니다. 혼동 방지를 위해 제거 또는 문서로 비관리 필드임을 명시합니다. 옵션 C에서는 `version = "0.0.0"` placeholder만 남기고 `poetry-dynamic-versioning`이 태그를 주입하도록 하며, `[tool.setuptools.dynamic]`을 제거해 중복 경로를 없앱니다.
- Q: 태그 없이 로컬에서 버전은?
  - A: A안은 `setuptools_scm`가 `0.0.0+dirty`/`+devN` 형식을 제공합니다. B안은 `24+dev` 등 개발 표식 유지. 옵션 C는 `strict=true`일 때 태그가 없으면 실패하므로, 로컬 스냅샷이 필요하면 프리릴리스 태그(`vX.Y.Z-dev.N`)를 만들거나 일시적으로 `poetry version "X.Y.Z.devN"`로 지정(커밋 금지)하거나 로컬에서만 `strict=false`로 낮춰 빌드합니다.
- Q: 런타임에서 `__version__`은?
  - A: 배포 패키지 설치 시 배포 메타에서 읽은 정확한 버전으로 노출됩니다. 옵션 C에서는 `importlib.metadata.version("vm-stock-kis")`가 플러그인 주입 버전과 동일하며, `__env__.py` placeholder 없이도 동작합니다.

- Q: 왜 `[tool.poetry].version`을 제거하면 `poetry build`가 실패하나요?
  - A: Poetry는 빌드 시 버전 필드가 필수입니다. 옵션 A(순수 `setuptools-scm`)로 전환하려면 빌드를 `python -m build`로 수행해야 하며, Poetry로 빌드를 유지하려면 옵션 C(플러그인) 또는 옵션 D(CI에서 `poetry version` 주입)로 버전을 설정해야 합니다. 옵션 C는 `version = "0.0.0"` placeholder를 두고 플러그인이 태그를 읽어 필드를 채우므로 빌드 요구 사항을 충족합니다.

- Q: 권장 Git 태그 표기 규칙은 무엇인가요?
  - A: 정식 릴리스는 `vX.Y.Z`를 권장합니다. 프리릴리스는 `vX.Y.Z-rc.N`, `-beta.N`, `-alpha.N`, 개발 스냅샷은 `vX.Y.Z-dev.N` 형식을 사용할 수 있습니다. 옵션 C에서는 플러그인이 `style="pep440"`로 자동 변환하여 `X.Y.Z`, `X.Y.ZrcN`, `X.Y.ZbN`, `X.Y.ZaN`, `X.Y.Z.devN`으로 매핑합니다. 옵션 D는 CI 스크립트로 동일한 매핑을 수행합니다.

- Q: 비태그 커밋의 버전은 어떻게 처리하나요?
  - A: 태그 없는 커밋은 PyPI 정식 배포 대상이 아닙니다. 옵션 D 예시 정책을 따라 `main`은 `X.Y.Z.devN`(최근 태그 이후 커밋 수), 기능 브랜치는 `X.Y.Z.dev<runNumber>-<shortSHA>`, 야간 빌드는 `X.Y.Z.dev<YYYYMMDDHHMM>`로 표기하고, 아티팩트만 업로드합니다. 옵션 C에서는 `strict=true`면 CI에서 즉시 실패하도록 두고, 필요 시 프리릴리스 태그를 미리 만들거나 로컬 전용으로 `poetry version "X.Y.Z.devN"`을 주입한 뒤 TestPyPI/아티팩트만 사용합니다.

- Q: 로컬에서 옵션 A 빌드를 어떻게 검증하나요?
  - A: `pipx install build` 후 `python -m build`(또는 `pipx run build`)로 빌드합니다. 태그가 없으면 `setuptools-scm`가 `+dirty`/`+devN` 버전을 생성할 수 있습니다. 산출물의 메타데이터 버전을 확인해 일관성을 검증하세요. 옵션 C에서는 프리릴리스 태그를 만든 뒤 `poetry build`를 실행하면 플러그인이 메타데이터에 태그 기반 버전을 주입하므로 `dist/*`의 `Version:` 필드가 태그와 일치하는지 확인하면 됩니다.

- Q: 빌드 산출물의 버전을 어떻게 검증하나요?
  - A: `dist/*.whl`의 `METADATA` 파일을 열어 `Version:` 값을 확인하거나, 임시 가상환경에 설치 후 `python -c "import importlib.metadata as m; print(m.version('vm-stock-kis'))"`로 런타임 버전을 확인합니다. 옵션 C는 플러그인이 빌드 시점에 메타데이터를 덮어쓰므로 `Version:` 값이 Git 태그와 일치하는지 확인하면 충분합니다.

- Q: 코드에서 버전 문자열을 안정적으로 읽는 방법은?
  - A: 설치된 배포에서는 `importlib.metadata.version('vm-stock-kis')`를 사용합니다. 소스 실행에서 태그 기반 버전이 필요하면 `setuptools_scm.get_version()`을 보조로 사용하고, 실패 시 `0.0.0+unknown` 등의 안전한 기본값을 사용합니다. 옵션 C를 선택하면 런타임은 항상 배포 메타에 기록된 버전을 그대로 읽으므로 `__env__.py` placeholder 없이도 동일 동작을 기대할 수 있습니다.

- Q: 버전 소스 충돌을 피하려면 어떻게 해야 하나요?
  - A: 단일 경로만 유지하세요. 옵션 C를 선택하면 `[tool.poetry].version`을 플러그인으로 관리하고 `[tool.setuptools.dynamic]`(setuptools 경로)와 `__env__.py` placeholder는 제거합니다. 옵션 A를 선택하면 `[project] dynamic`+`setuptools-scm`만 남기고 Poetry 빌드는 사용하지 않습니다. 옵션 D를 선택하면 CI에서만 `poetry version`을 설정하여 중복 설정을 피합니다.

- Q: 옵션 C(플러그인) 사용할 때 주의할 점은?
  - A: 태그가 단일 소스입니다. `strict=true`로 태그 없는 빌드를 실패 처리하고, 프리릴리스/개발 태그(`-dev.N/-alpha.N/-beta.N/-rc.N`)는 TestPyPI로만 게시하세요. `[build-system]`에서 setuptools 동적 버전 설정을 제거해 충돌을 막고, 로컬 스냅샷이 필요하면 태그를 만들거나 `poetry version "X.Y.Z.devN"`로 임시 버전을 지정하되 커밋하지 않습니다. 플러그인 버전을 명시적으로 고정하고(`poetry self add poetry-dynamic-versioning==<pin>`), CI와 로컬 설정이 동일하도록 `pyproject.toml`에만 설정을 둔 뒤 `.lock`/`poetry self show`로 확인하는 절차를 추가하세요.
