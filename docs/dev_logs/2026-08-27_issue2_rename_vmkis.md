# 2026-08-27 - Issue #2 이름 변경 및 src 레이아웃 전환 개발 일지

**대상 이슈**: [visualmoney/vm-stock-kis#2](https://github.com/visualmoney/vm-stock-kis/issues/2)
**프롬프트 문서**: [2026-08-27_issue2_rename_vmkis.md](../prompts/2026-08-27_issue2_rename_vmkis.md)
**범위**: 커밋 1~2 (이름 변경 + src 레이아웃, 패키징). 커밋 3~6은 미착수.

---

## 요약

| 항목 | 이전 | 이후 |
|---|---|---|
| PyPI 배포판 | `python-kis` | `vm-stock-kis` |
| import 모듈 | `pykis` | `vmkis` |
| 공개 클래스 | `PyKis` | `VmKis` |
| 환경변수 | `PYKIS_*` | `VMKIS_*` |
| 작업공간 | `~/.pykis` | `~/.vmkis` |
| User-Agent | `PyKis/x.y.z` | `VmKis/x.y.z` |
| 레이아웃 | flat (`pykis/`) | src (`src/vmkis/`) |
| 산문 표기 | `Python-KIS` | `VM-Stock-KIS` |

```text
959 passed, 8 skipped, 17 deselected — Python 3.10 / 3.13
Total coverage 90.67% (게이트 90)
rename 탐지 76건 (git log --follow 유지)
```

---

## 커밋 1과 2를 합친 이유

이슈는 두 커밋으로 나눌 것을 계획했다. 그러나 커밋 1(`git mv` + 스윕)만으로는
`pyproject.toml`의 `packages = ["vmkis"]`가 **존재하지 않는 디렉터리**를 가리킨다.
설치도 빌드도 되지 않는 중간 커밋이 남는다. 이슈 본문 스스로 "분리하면 모든
import가 깨진 중간 커밋이 남는다"고 지적한 것과 같은 이유가 패키징 설정에도
적용된다. 따라서 한 커밋으로 합쳤다.

rename 탐지는 유지된다: `git diff --find-renames=40%` 기준 76건.

---

## 스윕

이슈가 제시한 sed 규칙을 그대로 쓰되 `Python-KIS` → `VM-Stock-KIS` 규칙을
추가했다(결정된 브랜딩). 업스트림 URL은 sentinel(`@@UPSTREAM@@`)로 보호한 뒤
복원했고, sentinel 잔재가 없음을 확인했다.

### 스윕이 놓친 것 — 단어경계에 걸린 식별자

`\bpykis\b`는 `_`가 단어 문자라 아래를 매치하지 못했다.

| 위치 | 토큰 |
|---|---|
| `scripts/generate_api_reference.py` | `pykis_dir` |
| `tests/env.py` | `load_pykis` |
| `tests/unit/test_account_balance.py` | `virtual_pykis` |
| `src/vmkis/kis.py` docstring | `pykis_auth.json`, `pykis_real_auth.json` 등 |

`tests/unit/test_account_balance.py`에서는 `cls.pykis`가 `cls.vmkis`로 바뀌었는데
`cls.virtual_pykis`는 그대로 남아 **한 파일 안에서 명명이 갈렸다**. 코드
디렉터리(`src`, `tests`, `scripts`, `examples`)에 무경계 `s/pykis/vmkis/g`를
한 번 더 적용해 정리했다. 이 디렉터리들에는 보존해야 할 `pykis` 문자열이 없다.

### 스윕 대상에서 빠져 있던 파일

`docs/NEWSLETTER_TEMPLATE.md`가 이슈의 포함 목록에도 제외 목록에도 없었다.
내용이 "2025년 12월호"로 날짜가 박힌 발행물이라 **기록물로 보고 스윕하지 않았다.**
다만 파일명이 `TEMPLATE`이므로, 다음 호를 이 파일에서 복사해 쓸 경우 옛 이름이
그대로 퍼진다. → 별도 판단 필요.

---

## 수동 수정

### `src/` 접두사 누락

스윕은 `pykis/kis.py` → `vmkis/kis.py`로 바꾸지만 정답은 `src/vmkis/kis.py`다.
`.py`로 끝나는 경로만 골라 접두사를 붙였다. **`~/.vmkis`(작업공간 경로)에는
붙으면 안 되므로** 앞 문자가 `.`, `/`, `~`인 경우를 제외하는 정규식을 썼다.
디렉터리 트리 다이어그램의 루트 라벨(`vmkis/`)은 별도로 처리했다.

### `__env__.py`

* `except Exception` → **`except PackageNotFoundError`**.
  어떤 오류든 삼키고 하드코딩된 버전을 반환하던 상태였다.
* fallback `"2.1.6+dev"` → **`"0.0.0+unknown"`**.
  그럴듯한 거짓값보다 명백히 틀린 값이 낫다.
* `__url__`이 업스트림(`soju06/python-kis`)을 가리키고 있었다. 포크 URL로 바꾸고
  `__upstream_url__`을 따로 뒀다.
* `_dist_version()`에 넘기는 인자가 **배포명**(`vm-stock-kis`)임을 검증했다.
  모듈명(`vmkis`)을 넘기면 `PackageNotFoundError`가 나고 fallback이 조용히
  가짜 버전을 노출한다.

### `scripts/generate_api_reference.py`

`repo_root / "vmkis"` → `repo_root / "src" / "vmkis"`.

---

## 호환 shim 3종

전부 v4.0.0에서 제거한다. 각각 테스트를 붙였다
(`tests/unit/test_compat_aliases.py`, `tests/unit/utils/test_workspace.py`).

### 1. `vmkis.PyKis` 별칭

PEP 562 모듈 `__getattr__`로 노출하며 `DeprecationWarning`을 낸다. 동일 객체를
반환하므로 `isinstance` 검사가 그대로 동작한다. `__all__`에는 넣지 않았다 —
넣으면 `from vmkis import *`가 옛 이름을 계속 퍼뜨린다.

기존에 있던 deprecated 루트 import용 `__getattr__` **앞에** 분기를 넣었다.
그렇게 하지 않으면 "`vmkis.types`를 쓰라"는 엉뚱한 안내가 나간다.

### 2. `~/.pykis` 작업공간 폴백

새 경로가 없고 예전 경로만 있으면 예전 경로를 계속 쓴다. 그렇게 하지 않으면
기존 사용자의 토큰 캐시가 고아가 되어 재인증이 강제된다. 둘 다 있으면 새 경로를
쓰고 경고하지 않는다.

### 3. `PYKIS_*` 환경변수 폴백

`_env()` 헬퍼가 `VMKIS_<name>`을 먼저 보고 없으면 `PYKIS_<name>`으로 떨어진다.
라이브러리가 실제로 읽는 변수는 `PROFILE`, `CONFIRM_SKIP` 둘뿐이다.

### `pykis` 패키지 shim은 배포하지 않음

`vm-stock-kis` 휠 안에 `pykis/`를 넣으면 업스트림 `python-kis` 배포판과 디스크
에서 파일이 충돌한다. 둘 다 설치한 사용자가 한쪽을 uninstall하면 다른 쪽 파일이
지워진다. Python 패키징에는 `Conflicts:`가 없어 패키지 매니저가 해결할 수 없다.

---

## 함께 발견해 고친 결함

### `pyyaml`이 런타임 의존성에 없었다

`helpers.py`가 `import yaml`을 하는데 `[project].dependencies`에 `pyyaml`이
없었다. 현재 개발 환경에 있었던 이유는 **lint 그룹의 `pre-commit`이 전이 의존으로
끌어왔기** 때문이다. 즉 커버리지 측정조차 lint 도구의 전이 의존에 기대고 있었다.

격리 환경에서 재현했다.

```text
$ uv run --isolated --no-project --with dist/*.whl python -c "import vmkis; ..."
create_client = None
save_config_interactive = None
SimpleKIS = None
vmkis.helpers import 실패: ModuleNotFoundError No module named 'yaml'
```

### 같은 `try` 블록이 `SimpleKIS`까지 지우고 있었다

```python
try:
    from vmkis.simple import SimpleKIS          # 성공
    from vmkis.helpers import create_client...  # 실패
except Exception:
    SimpleKIS = None                            # ← 성공한 것까지 덮어씀
```

`SimpleKIS`는 정상 import되는데도 `None`이 됐다. import를 분리하고 `except`를
`Exception` → `ImportError`로 좁혔다. `pyyaml` 추가 후 셋 다 정상 노출을 확인했다.

---

## 패키징 검증

```text
uv lock --check                                    통과
twine check --strict dist/*                        통과 (whl, tar.gz)
휠 최상위: ['vm_stock_kis-*.dist-info', 'vmkis']
  vmkis/py.typed 포함: True
  pykis/ 부재:        True
  tests/ 미포함:      True
격리 설치 후 import 및 버전 해석 확인
```

버전 배관이 처음으로 실제 동작한다:

```text
git tag v2.1.6 ──hatch-vcs──► 2.1.6.post1.dev5+g11ea7787f
                                    └──importlib.metadata──► vmkis.__version__
                                                                  └──► USER_AGENT
```

---

## 변경 파일

* `pykis/**` → `src/vmkis/**` (rename 76건)
* `src/vmkis/__env__.py` — 버전 해석, URL
* `src/vmkis/__init__.py` — `PyKis` 별칭, import 분리
* `src/vmkis/utils/workspace.py` — 레거시 경로 폴백
* `src/vmkis/helpers.py` — `_env()` 환경변수 폴백
* `scripts/generate_api_reference.py` — src 경로
* `pyproject.toml` — `packages`, `source`, sdist `include`, cache-keys, `pyyaml`
* `.python-version` — 신규, `3.10`
* `.gitignore` — `.python-version` 무시 해제
* `.pre-commit-config.yaml` — `check-json`에서 `.vscode/` 제외 (JSONC)
* `tests/unit/test_compat_aliases.py` — 신규
* `tests/unit/utils/test_workspace.py` — 폴백 테스트 추가
* 문서·테스트·예제 전반의 이름 스윕

`.vscode/*.json`은 주석을 포함한 JSONC라 표준 JSON 파서가 거부한다. VS Code가
공식적으로 허용하는 형식이므로 `check-json` 대상에서 제외했다.

---

## 남은 일 (커밋 3~6, 이번 범위 밖)

* **커밋 3**: `ci.yml`/`publish.yml` 재작성, `dependabot.yml` 추가,
  `.github` 템플릿 링크 정정 (현재 업스트림을 가리킴)
* **커밋 4**: `VERSIONING.md` 축소(500줄 → 약 60줄), `MIGRATION_GUIDE.md`에
  v2.x ↔ v3.0.0 대조표, `CONTRIBUTING.md`의 poetry → uv, `CHANGELOG.md` 신규
* **커밋 5**: `ruff check --fix` + `ruff format` 단독 스윕 + `.git-blame-ignore-revs`
  (현재 ruff 오류 1003건, 미포맷 120파일. `[tool.ruff]`에 `select`가 없어 버전에
  따라 판정이 요동친다 — 일괄 정리 시 `select`를 명시할 것)
* **커밋 6**: `git tag -a v3.0.0`

### 판단이 필요한 항목

* `docs/NEWSLETTER_TEMPLATE.md` — 기록물로 보고 스윕 제외했으나 파일명이
  `TEMPLATE`이다. 다음 호에 재사용하면 옛 이름이 퍼진다.
* `__author__` / `__author_email__`이 여전히 `soju06` / `qlskssk@gmail.com`이다.
  `pyproject.toml`의 `authors`에는 두 사람이 모두 있고 `maintainers`는
  `visualmoney`다. 이슈가 명시하지 않아 손대지 않았다.
* `MIGRATION_GUIDE.md`가 스윕되면서 v2.x 시절 표기(`from pykis import PyKis`)가
  사라졌다. 마이그레이션 문서는 옛 이름과 새 이름을 **모두** 보여야 하므로
  커밋 4에서 새로 작성해야 한다.

### 저장소 밖 수동 작업 (이슈 본문 기준)

* PyPI pending publisher 등록 (`vm-stock-kis`, `publish.yml`, environment `pypi`)
* GitHub Environment `pypi` 생성 + 배포 대상을 `v*` 태그로 제한
* TestPyPI에 `v3.0.0rc1` 선행 업로드 (core metadata 2.4/2.5 검증)
