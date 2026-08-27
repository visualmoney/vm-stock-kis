# API Reference

자동 생성된 API 레퍼런스 문서입니다.

---

## 목차

- [pykis.client.auth](#pykis-client-auth)
- [pykis.helpers](#pykis-helpers)
- [pykis.kis](#pykis-kis)
- [pykis.public_types](#pykis-public_types)
- [pykis.simple](#pykis-simple)

---

## pykis.client.auth

### Classes

#### `KisAuth`

한국투자증권 OpenAPI 계좌 및 인증 정보

Examples:
    >>> auth = KisAuth(
    ...     # HTS 아이디  예) soju06
    ...     id="YOUR_HTS_ID",
    ...     # 앱 키  예) Pa0knAM6JLAjIa93Miajz7ykJIXXXXXXXXXX
    ...     appkey="YOUR_APP_KEY",
    ...     # 앱 시크릿 키  예) V9J3YGPE5q2ZRG5EgqnLHn7XqbJjzwXcNpvY . . .
    ...     secretkey="YOUR_APP_SECRET",
    ...     # 앱 키와 연결된 계좌번호  예) 00000000-01
    ...     account="00000000-01",
    ...     # 모의투자 여부
    ...     virtual=False,
    ... )

    안전한 경로에 시크릿 키를 파일로 저장합니다.

    >>> auth.save("secret.json")

**Methods:**

- `key()`: 앱 키
- `account_number()`: 계좌번호
- `save()`: 계좌 및 인증 정보를 JSON 파일로 저장합니다.
- `load()`: JSON 파일에서 계좌 및 인증 정보를 불러옵니다.

### Functions

#### `key()`

앱 키

#### `account_number()`

계좌번호

#### `save()`

계좌 및 인증 정보를 JSON 파일로 저장합니다.

#### `load()`

JSON 파일에서 계좌 및 인증 정보를 불러옵니다.

---

## pykis.helpers

### Functions

#### `load_config()`

Load YAML config from path.

Supports legacy flat config and the new multi-profile format:

multi-profile format example:
    default: virtual
    configs:
        virtual:
            id: ...
            account: ...
            appkey: ...
            secretkey: ...
            virtual: true
        real:
            id: ...
            ...

Profile selection order:
    1. explicit `profile` argument
    2. environment `PYKIS_PROFILE`
    3. `default` key in multi-config
    4. fallback to 'virtual'

#### `create_client()`

Create a `PyKis` client from a YAML config file.

If `virtual` is true in the config, the function will construct a
`KisAuth` and pass it as the `virtual_auth` argument to `PyKis`.
This avoids accidentally treating a virtual-only auth as a real auth.

#### `save_config_interactive()`

Interactively prompt for config values and save to YAML.

Returns the written dict.

#### `load_config()`

Load YAML config from path.

#### `create_client()`

Create a `PyKis` client from a YAML config file.

If `virtual` is true in the config, the function will construct a
`KisAuth` and pass it as the `virtual_auth` argument to `PyKis`.
This avoids accidentally treating a virtual-only auth as a real auth.

#### `save_config_interactive()`

Interactively prompt for config values and save to YAML.

This function hides the secret when echoing and asks for confirmation
before writing. Set environment variable `PYKIS_CONFIRM_SKIP=1` to skip
the interactive prompt (useful for CI scripts).

Returns the written dict.

---

## pykis.kis

### Classes

#### `PyKis`

한국투자증권 API

**Methods:**

- `virtual()`: 모의도메인 여부
- `keep_token()`: API 접속 토큰 자동 저장 여부
- `request()`:
- `fetch()`:
- `token()`: 실전도메인 API 접속 토큰을 반환합니다.
- `token()`: API 접속 토큰을 설정합니다.
- `primary_token()`: API 접속 토큰을 반환합니다.
- `primary_token()`: API 접속 토큰을 설정합니다.
- `discard()`: API 접속 토큰을 폐기합니다.
- `primary()`: 기본 계좌 정보를 반환합니다.
- `websocket()`: 웹소켓 클라이언트를 반환합니다.
- `close()`: API 세션을 종료합니다.

### Functions

#### `virtual()`

모의도메인 여부

#### `keep_token()`

API 접속 토큰 자동 저장 여부

#### `request()`

(No docstring)

#### `fetch()`

(No docstring)

#### `token()`

실전도메인 API 접속 토큰을 반환합니다.

#### `token()`

API 접속 토큰을 설정합니다.

#### `primary_token()`

API 접속 토큰을 반환합니다.

#### `primary_token()`

API 접속 토큰을 설정합니다.

#### `discard()`

API 접속 토큰을 폐기합니다.

#### `primary()`

기본 계좌 정보를 반환합니다.

Raises:
    ValueError: 기본 계좌 정보가 없을 경우

#### `websocket()`

웹소켓 클라이언트를 반환합니다.

#### `close()`

API 세션을 종료합니다.

---

## pykis.public_types

---

## pykis.simple

### Classes

#### `SimpleKIS`

A very small facade for common user flows.

This class intentionally implements a tiny, beginner-friendly API that
delegates to a `PyKis` instance.

**Methods:**

- `from_client()`:
- `get_price()`: Return the quote for `symbol`.
- `get_balance()`: Return account balance object.
- `place_order()`: Place a basic order. If `price` is None, market order is used.
- `cancel_order()`: Cancel an existing order object (delegates to order.cancel()).

### Functions

#### `from_client()`

(No docstring)

#### `get_price()`

Return the quote for `symbol`.

#### `get_balance()`

Return account balance object.

#### `place_order()`

Place a basic order. If `price` is None, market order is used.

#### `cancel_order()`

Cancel an existing order object (delegates to order.cancel()).

---
