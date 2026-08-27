# PyPI 배포 가이드 (vm-stock-kis)

**작성일**: 2026-08-27
**대상**: 최초 배포자 / 릴리스 담당자
**전제**: 이 저장소는 `hatchling` + `hatch-vcs` 로 빌드하며, **버전은 git 태그에서 자동 생성**됩니다.

---

## 0. 사전 확인 (현재 저장소 상태)

| 항목 | 상태 |
|------|------|
| 배포명 | `vm-stock-kis` (PyPI/TestPyPI 모두 **미등록 = 선점 가능**, 2026-08-27 확인) |
| 임포트명 | `vmkis` (`src/vmkis`) |
| 빌드 백엔드 | `hatchling` (`pyproject.toml`) |
| 버전 소스 | git 태그 (`[tool.hatch.version] source = "vcs"`) |
| 배포 워크플로 | `.github/workflows/publish.yml` (태그 `v*.*.*` push 시 실행) |
| 인증 방식 | Trusted Publishing (OIDC) — `pypa/gh-action-pypi-publish`, `permissions: id-token: write` |

> **중요**: 버전이 태그에서 나오므로, **태그가 정확히 찍힌 커밋에서만** PyPI에 올릴 수 있는
> 버전(`2.2.0`)이 나옵니다. 태그 이후 커밋에서 빌드하면
> `2.1.6.post1.dev5+g11ea7787f` 처럼 **로컬 버전 식별자(`+...`)** 가 붙고,
> **PyPI는 로컬 버전이 붙은 파일을 거부**합니다.

---

## 1. 계정 준비 (최초 1회)

1. **PyPI 계정 생성**: https://pypi.org/account/register/
2. **TestPyPI 계정 생성**: https://test.pypi.org/account/register/
   - PyPI와 **별개 계정**입니다. 비밀번호/2FA를 따로 설정해야 합니다.
3. **2FA 활성화 (필수)**: PyPI는 모든 업로드 계정에 2FA를 요구합니다.
   - Account settings → Two factor authentication → TOTP 앱(예: Google Authenticator) 등록
   - **복구 코드는 반드시 별도 보관**하세요. 분실 시 계정 복구가 매우 번거롭습니다.

---

## 2. Trusted Publishing 등록 (권장, 토큰 불필요)

API 토큰을 저장소 시크릿에 넣지 않고, GitHub Actions가 OIDC로 신원을 증명하는 방식입니다.
이 저장소의 `publish.yml`은 이미 이 방식으로 작성되어 있습니다.

### 2-1. PyPI 쪽 (프로젝트가 아직 없으므로 "pending publisher")

https://pypi.org/manage/account/publishing/ 에서 **Add a new pending publisher**:

| 필드 | 값 |
|------|-----|
| PyPI Project Name | `vm-stock-kis` |
| Owner | `visualmoney` |
| Repository name | `vm-stock-kis` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

> Environment name은 워크플로의 `environment: name: pypi` 와 **문자 그대로 일치**해야 합니다.

### 2-2. TestPyPI 쪽

https://test.pypi.org/manage/account/publishing/ 에서 동일하게 등록하되,
Environment name은 TestPyPI용 잡에서 쓸 이름(예: `testpypi`)으로 맞춥니다.

### 2-3. GitHub 저장소 쪽

Settings → Environments → **New environment** → `pypi`
- (선택) Deployment branches/tags 를 `v*` 태그로 제한
- (선택) Required reviewers 를 지정하면 태그 push 후 수동 승인 단계가 생깁니다.

---

## 3. 로컬에서 빌드 검증 (업로드 전 필수)

```bash
# 작업 트리를 깨끗하게
git status --porcelain     # 출력이 비어 있어야 함

rm -rf dist/
uv build                   # 또는: python -m build
ls dist/
# vm_stock_kis-<version>-py3-none-any.whl
# vm_stock_kis-<version>.tar.gz

# 메타데이터 검증
uvx twine check dist/*     # PASSED 두 줄이 나와야 함
```

### 설치 스모크 테스트 (격리 환경)

```bash
uv venv /tmp/vmkis-smoke
VIRTUAL_ENV=/tmp/vmkis-smoke uv pip install dist/vm_stock_kis-*.whl
VIRTUAL_ENV=/tmp/vmkis-smoke /tmp/vmkis-smoke/bin/python -c \
  "import vmkis; print(vmkis.__version__)"
```

sdist가 실제로 빌드되는지도 확인합니다(누락된 파일 탐지):

```bash
uv venv /tmp/vmkis-sdist
VIRTUAL_ENV=/tmp/vmkis-sdist uv pip install dist/vm_stock_kis-*.tar.gz
```

---

## 4. TestPyPI 리허설 (강력 권장)

PyPI는 **같은 버전 번호를 재업로드할 수 없고, 삭제해도 그 번호는 영구히 재사용 불가**입니다.
그래서 실수를 여기서 다 소진합니다.

```bash
# 리허설용 태그 (예: 2.2.0rc1)
git tag -a v2.2.0rc1 -m "TestPyPI rehearsal"
rm -rf dist/ && uv build
uvx twine check dist/*

# 업로드 (토큰 방식)
uvx twine upload --repository testpypi dist/*
#   username: __token__
#   password: pypi-... (TestPyPI에서 발급한 API 토큰)
```

설치 확인 — **의존성은 실제 PyPI에서** 받아야 합니다(TestPyPI에는 없음):

```bash
uv venv /tmp/vmkis-test
VIRTUAL_ENV=/tmp/vmkis-test uv pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  vm-stock-kis
```

프로젝트 페이지에서 README 렌더링이 깨지지 않았는지 눈으로 확인합니다:
https://test.pypi.org/project/vm-stock-kis/

리허설 태그는 확인 후 정리합니다:

```bash
git tag -d v2.2.0rc1
```

---

## 5. 실제 배포

```bash
# 1) main 최신화
git checkout main && git pull

# 2) CI 통과 확인 (테스트/린트/커버리지)

# 3) 태그 생성 및 push  → publish.yml 이 자동 실행됨
git tag -a v2.2.0 -m "Release 2.2.0"
git push origin v2.2.0
```

이후 GitHub → Actions → "Publish Python 🐍 distributions 📦 to PyPI" 에서 진행 상황을 봅니다.
`pypi` 환경에 승인자를 걸어 두었다면 여기서 **Approve** 를 눌러야 업로드가 진행됩니다.

수동 업로드가 필요한 경우(워크플로 없이):

```bash
uvx twine upload dist/*     # username: __token__ / password: pypi-...
```

---

## 6. 배포 후 확인

```bash
uv venv /tmp/vmkis-prod
VIRTUAL_ENV=/tmp/vmkis-prod uv pip install vm-stock-kis
VIRTUAL_ENV=/tmp/vmkis-prod /tmp/vmkis-prod/bin/python -c \
  "import vmkis; print(vmkis.__version__)"
```

- 프로젝트 페이지: https://pypi.org/project/vm-stock-kis/
- GitHub Releases 에 릴리스 노트 작성
- `docs/dev_logs/` 에 배포 일지 기록

---

## 7. 자주 걸리는 함정

| 증상 | 원인 / 해결 |
|------|-------------|
| `400 Bad Request: ... local version label` | 태그가 안 찍힌 커밋에서 빌드함. 정확한 태그 커밋에서 다시 빌드 |
| `403 Forbidden` (Trusted Publishing) | pending publisher의 owner/repo/workflow/environment 중 하나가 불일치 |
| `400 File already exists` | 그 버전은 영구히 사용 불가. 버전을 올려서 다시 배포 |
| README가 깨짐 | `twine check` 로 사전 검증. `readme = "README.md"` 이므로 GFM 확장 문법 주의 |
| 버전이 `0.0.0` | git 메타데이터 없이 빌드됨(shallow clone/tarball). `fetch-depth: 0` 필요 |
| 이름이 선점됨 | `vm-stock-kis` 는 2026-08-27 기준 미등록. 늦어지면 선점 위험 → 조기 선점 배포 고려 |

---

## 8. 알려진 정리 대상

`.github/workflows/publish.yml` 의 "Update version in src/vmkis/\_\_env\_\_.py" 스텝은
`{{VERSION_PLACEHOLDER}}` 를 치환하지만, 현재 `__env__.py` 는
`importlib.metadata` 로 버전을 읽으므로 **플레이스홀더가 존재하지 않습니다**.
동작에는 영향이 없으나(치환 대상 없음 = no-op) 혼란을 주므로 삭제 대상입니다.
