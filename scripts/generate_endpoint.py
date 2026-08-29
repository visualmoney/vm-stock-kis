#!/usr/bin/env python3
"""추출된 스펙에서 vmkis 스타일 엔드포인트 모듈을 생성합니다. (이슈 #21 파일럿)

## 무엇을 생성하는가

- `KisEndpoint` 상수 (경로 + TR ID)
- 응답 항목 클래스 (`KisDynamic` 상속, 필드 + 한글 라벨 docstring)
- 응답 래퍼 클래스 (`KisAPIResponse`, `output` 을 리스트/단건으로)

## 무엇을 생성하지 **않는가** — 손이 필요한 부분

| | 왜 |
|---|---|
| `output` 이 리스트인지 단건인지 | 샘플이 `pd.DataFrame(...)` 으로만 알려줍니다. `--list`/`--single` 로 지정 |
| 파라미터 검증 규칙 | 샘플의 `raise ValueError(...)` 는 **원문 로직**입니다. 옮기지 않습니다 |
| scope 바인딩 (`kis.stock().xxx()`) | Protocol 필요 여부 판정이 필요합니다 (ARCHITECTURE.md 판정표) |
| 필드 이름의 한국어→영어 번역 | 기계가 정하면 공개 API 이름이 흔들립니다 |

## 원문 복사 금지

원본(`koreainvestment/open-trading-api`)에는 LICENSE 가 없습니다. 이 생성기는
**사실만** 씁니다 — 경로, TR ID, 필드명, 한글 라벨. 원문 docstring 설명문은
스펙에 들어 있지도 않습니다(`extract_kis_specs.py` 가 추출하지 않습니다).

`tests/unit/test_codegen_pilot.py` 가 생성물에 원문 문장이 섞이지 않았는지
기계적으로 검사합니다. **사람이 눈으로 지키는 규칙은 300개 규모에서 지켜지지
않습니다.**

## 사용법

    python scripts/generate_endpoint.py specs.json volume_rank -o out/
"""

from __future__ import annotations

import argparse
import json
import keyword
import pathlib
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from extract_kis_specs import guess_type  # noqa: E402

#: 생성 헤더. 손으로 고치면 다음 생성 때 날아간다는 것을 파일 자신이 말해야 합니다.
HEADER = '''"""{title}

**이 파일은 생성물입니다.** `scripts/generate_endpoint.py` 가 만들었습니다.
손으로 고치면 다음 생성 때 사라집니다.

출처 스펙: `examples_llm/{category}/{name}` — **사실만** 옮겼습니다
(경로 · TR ID · 필드명 · 한글 라벨). 원문 설명문은 옮기지 않습니다.

이슈 [#21](https://github.com/visualmoney/vm-stock-kis/issues/21) 파일럿 산출물이며,
아직 패키지에 편입되지 않았습니다.
"""
'''


def _pascal(name: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[_\-]", name) if part)


def _safe_ident(name: str) -> str:
    ident = re.sub(r"\W", "_", name)
    if not ident or ident[0].isdigit():
        ident = f"f_{ident}"
    if keyword.iskeyword(ident):
        ident = f"{ident}_"
    return ident


#: KisType 이름 -> 파이썬 주석 타입.
PY_TYPE = {
    "KisString": "str",
    "KisInt": "int",
    "KisDecimal": "Decimal",
    "KisBool": "bool",
    "KisDate": "date",
    "KisTime": "time",
}


def render(spec: dict, as_list: bool) -> str:
    name = spec["name"]
    cls = f"Kis{_pascal(name)}"
    const = name.upper()
    title = f"[{spec['category']}] {name}" + (f"  {spec['doc_code']}" if spec["doc_code"] else "")

    fields = spec["fields"]
    kis_types = {f: (guess_type(f) or "KisString") for f in fields}
    used = sorted(set(kis_types.values()) | {"KisString"})
    py_imports = sorted({PY_TYPE[t] for t in used if PY_TYPE[t] in ("Decimal", "date", "time")})

    out: list[str] = [HEADER.format(title=title, category=spec["category"], name=name)]

    if py_imports:
        std = [i for i in py_imports if i in ("date", "time")]
        if std:
            out.append(f"from datetime import {', '.join(std)}")
        if "Decimal" in py_imports:
            out.append("from decimal import Decimal")
        out.append("")

    out.append("from vmkis.client.endpoint import KisEndpoint")
    out.append("from vmkis.responses.dynamic import KisDynamic, KisList")
    out.append("from vmkis.responses.response import KisAPIResponse")
    out.append(f"from vmkis.responses.types import {', '.join(used)}")
    out.append("")
    out.append("")

    # ── 엔드포인트 상수 ──────────────────────────────────────────────────────
    tr_ids = spec["tr_ids"]
    out.append(f"{const} = KisEndpoint(")
    out.append(f'    path="{spec["path"]}",')
    out.append(f'    tr_live="{tr_ids[0]}",')
    if len(tr_ids) > 1:
        # 모의 TR ID 는 실전 TR ID 의 첫 글자를 V 로 바꾼 것이 관례입니다.
        paper = [t for t in tr_ids[1:] if t.startswith("V")]
        if paper:
            out.append(f'    tr_paper="{paper[0]}",')
        rest = [t for t in tr_ids[1:] if t not in paper]
        if rest:
            out.append(f"    # 분기 TR ID 가 더 있습니다: {', '.join(rest)}")
            out.append("    # 어떤 조건에서 갈리는지는 사람이 정해야 합니다.")
    if spec["method"] == "POST":
        out.append('    method="POST",')
    out.append(")")
    out.append("")
    if spec["method"] == "POST":
        out.append("# ⚠️ 주문 계열입니다. 오생성 시 금전 사고로 이어지므로 수동 리뷰 없이")
        out.append("#    패키지에 넣지 마세요. (#21 의 '주의' 항목)")
        out.append("")
    out.append("")

    # ── 항목 클래스 ─────────────────────────────────────────────────────────
    item_cls = f"{cls}Item" if as_list else cls
    out.append(f"class {item_cls}(KisDynamic):")
    out.append(f'    """{name} 응답 항목 ({len(fields)}개 필드)"""')
    out.append("")
    for raw, label in fields.items():
        kt = kis_types[raw]
        ident = _safe_ident(raw)
        out.append(f'    {ident}: {PY_TYPE[kt]} = {kt}["{raw}"]')
        out.append(f'    """{label}"""')
    out.append("")
    out.append("")

    # ── 응답 래퍼 ───────────────────────────────────────────────────────────
    if as_list:
        out.append(f"class {cls}(KisAPIResponse):")
        out.append(f'    """{name} 응답"""')
        out.append("")
        out.append("    __path__ = None")
        out.append("")
        out.append(f'    items: list[{item_cls}] = KisList({item_cls})["output"]')
        out.append(f'    """{name} 목록"""')
    else:
        out.append(f"class {cls}Response(KisAPIResponse, {item_cls}):")
        out.append(f'    """{name} 응답"""')
        out.append("")
        out.append('    __path__ = "output"')
    out.append("")

    untyped = [f for f, t in kis_types.items() if guess_type(f) is None]
    if untyped:
        out.append("")
        out.append(f"# 타입을 추정하지 못해 KisString 으로 둔 필드 {len(untyped)}개:")
        for chunk in [untyped[i : i + 6] for i in range(0, len(untyped), 6)]:
            out.append(f"#   {', '.join(chunk)}")
        out.append("# KisString 은 어떤 문자열도 받으므로 런타임 오류가 나지 않습니다.")
        out.append("# 실제 응답을 보고 승격하세요.")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("specs", type=pathlib.Path)
    ap.add_argument(
        "names",
        nargs="+",
        help="생성할 엔드포인트. `category/name` 또는 `name`. "
        "이름은 카테고리 간에 유일하지 않습니다 — 332개 중 30개가 겹칩니다",
    )
    ap.add_argument("-o", "--out", type=pathlib.Path, required=True)
    ap.add_argument("--single", nargs="*", default=[], help="output 이 단건인 엔드포인트")
    args = ap.parse_args()

    raw = json.loads(args.specs.read_text(encoding="utf-8"))
    # **이름만으로 키를 잡으면 안 됩니다.** `inquire_price` 는 카테고리 5곳에
    # 있고, 뒤엣것이 앞엣것을 덮어 조용히 다른 엔드포인트를 생성합니다.
    specs = {f"{s['category']}/{s['name']}": s for s in raw}
    args.out.mkdir(parents=True, exist_ok=True)

    for name in args.names:
        if name in specs:
            spec = specs[name]
        else:
            matches = [k for k in specs if k.rsplit("/", 1)[1] == name]
            if not matches:
                print(f"스펙에 없습니다: {name}", file=sys.stderr)
                return 1
            if len(matches) > 1:
                print(
                    f"이름이 모호합니다: {name} — {', '.join(matches)}\n`category/name` 형태로 지정하세요.",
                    file=sys.stderr,
                )
                return 1
            spec = specs[matches[0]]
        if not spec["complete"] if "complete" in spec else spec["problems"]:
            print(f"완전 파싱되지 않은 스펙입니다: {name} — {spec['problems']}", file=sys.stderr)
            return 1
        code = render(spec, as_list=name not in args.single and spec["name"] not in args.single)
        # 파일명에도 카테고리를 넣습니다. 이름이 겹치면 생성물끼리 덮어씁니다.
        path = args.out / f"{spec['category']}__{spec['name']}.py"
        path.write_text(code, encoding="utf-8")
        print(f"{len(code.splitlines()):4d}줄  {path}")

    _format(args.out)
    return 0


def _format(out: pathlib.Path) -> None:
    """생성물을 저장소의 ruff 설정으로 다듬습니다.

    생성기가 빈 줄까지 완벽하게 맞추게 만들면 템플릿이 읽기 어려워집니다.
    포매팅은 포매터에게 맡기고, 생성기는 **내용**만 책임집니다.

    ruff 가 없으면 조용히 건너뜁니다 — 생성 자체는 성공했기 때문입니다.
    """
    ruff = shutil.which("ruff")
    if ruff is None:
        print("ruff 를 찾지 못해 포매팅을 건너뜁니다.", file=sys.stderr)
        return
    subprocess.run([ruff, "check", "--fix", "--quiet", str(out)], check=False)
    subprocess.run([ruff, "format", "--quiet", str(out)], check=False)


if __name__ == "__main__":
    raise SystemExit(main())
