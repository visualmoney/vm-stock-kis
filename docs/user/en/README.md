# VM-Stock-KIS: Korea Investment & Securities API Library

**Language**: [한국어](../../README.md) | [English](README.md)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](../../../LICENCE)
[![PyPI Version](https://img.shields.io/pypi/v/vmkis)](https://pypi.org/project/vmkis/)
[![Test Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)](../../../README.md)

---

## Overview

**VM-Stock-KIS** is a Python library for the Korea Investment & Securities (KIS) REST API and WebSocket API. It provides a simple and intuitive interface for:

- 📊 **Real-time stock quotes** (Korea Stock Exchange)
- 💼 **Account management** (balance, holdings, profit/loss)
- 📈 **Order management** (buy, sell, cancel)
- 🔔 **Real-time price updates** (WebSocket)
- 🔐 **Secure authentication** (OAuth 2.0)
- 🛡️ **Error handling** (13 exception types with auto-retry)
- 📝 **Structured logging** (JSON format, ELK compatible)

---

## Key Features

### ✨ Developer-Friendly

```python
# Simple and intuitive API
from vmkis import VmKis

kis = VmKis(app_key="YOUR_KEY", app_secret="YOUR_SECRET")
quote = kis.stock("005930").quote()  # Samsung Electronics
print(f"Current price: {quote.price:,} KRW")
```

### 🔄 Auto-Retry with Exponential Backoff

```python
from vmkis.utils.retry import with_retry

@with_retry(max_retries=5, initial_delay=2.0)
def fetch_quote(symbol):
    return kis.stock(symbol).quote()

# Automatically retries on network errors
quote = fetch_quote("005930")
```

### 📋 Structured Logging (ELK Compatible)

```python
from vmkis.logging import enable_json_logging

enable_json_logging()  # Enable JSON format

# Logs:
# {"timestamp": "2025-12-20T14:30:45Z", "level": "INFO", "message": "Order executed", ...}
```

### 🎯 13 Exception Types

```python
from vmkis.exceptions import (
    KisConnectionError,      # Network issues (retryable)
    KisAuthenticationError,  # Invalid credentials
    KisRateLimitError,       # Too many requests (retryable)
    KisServerError,          # 5xx errors (retryable)
    # ... 9 more exception types
)

try:
    quote = kis.stock("005930").quote()
except KisConnectionError:
    print("Network error - will retry automatically")
except KisAuthenticationError:
    print("Check your API credentials")
```

---

## Quick Start

### 1. Installation

```bash
# Install from PyPI
pip install vm-stock-kis

# Or from source
git clone https://github.com/visualmoney/vm-stock-kis.git
cd vm-stock-kis
pip install -e .
```

### 2. Authentication

#### Method 1: Environment Variables

```bash
export VMKIS_APP_KEY="YOUR_APP_KEY"
export VMKIS_APP_SECRET="YOUR_APP_SECRET"
export VMKIS_ACCOUNT_NUMBER="YOUR_ACCOUNT_NUMBER"
```

```python
from vmkis import VmKis

kis = VmKis()  # Loads from environment
```

#### Method 2: Configuration File

**config.yaml**:

```yaml
kis:
  server: real  # or "virtual" for sandbox
  app_key: YOUR_APP_KEY
  app_secret: YOUR_APP_SECRET
  account_number: "00000000-01"
```

```python
from vmkis.helpers import load_config
from vmkis import VmKis

config = load_config("config.yaml")
kis = VmKis(**config['kis'])
```

#### Method 3: Direct Parameters

```python
from vmkis import VmKis

kis = VmKis(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
    account_number="00000000-01"
)
```

### 3. Basic Usage

#### Get Stock Quote

```python
# Fetch real-time price
samsung = kis.stock("005930")  # Samsung Electronics (ISIN code)
quote = samsung.quote()

print(f"Price: {quote.price:,} KRW")
print(f"High: {quote.high:,} KRW")
print(f"Low: {quote.low:,} KRW")
print(f"Volume: {quote.volume:,}")
```

#### Check Account Balance

```python
account = kis.account()
balance = account.balance()

print(f"Cash: {balance.cash:,} KRW")
print(f"Evaluated Amount: {balance.evaluated_amount:,} KRW")
print(f"Profit/Loss: {balance.profit_loss:,} KRW ({balance.profit_rate}%)")
```

#### Place a Buy Order

```python
# Buy 10 shares of Samsung at 60,000 KRW each
order = kis.stock("005930").buy(quantity=10, price=60000)

print(f"Order ID: {order.order_id}")
print(f"Status: {order.status}")
```

#### Cancel an Order

```python
# Cancel the order
kis.stock("005930").cancel(order_id="12345")
```

### 4. Next Steps

- 📚 **Full Documentation**: [docs/user/en/](./README.md)
- 🚀 **Quick Start Guide**: [QUICKSTART.md](./QUICKSTART.md)
- ❓ **FAQ**: [FAQ.md](./FAQ.md)
- 🛠️ **Examples**: [examples/](../../../examples/)
- 🔧 **Configuration**: [CONFIGURATION.md](./CONFIGURATION.md)

---

## Common Tasks

### Real-Time Price Updates (WebSocket)

```python
async def on_price_update(quote):
    print(f"New price: {quote.price:,} KRW")

# Subscribe to real-time updates
samsung = kis.stock("005930")
samsung.subscribe(callback=on_price_update)
```

### Get Multiple Stock Quotes

```python
import pandas as pd

symbols = ["005930", "000660", "051910"]  # Samsung, SK Hynix, LG Chemical
quotes = [kis.stock(sym).quote() for sym in symbols]

# Convert to DataFrame
df = pd.DataFrame([
    {"Symbol": sym, "Price": q.price, "Volume": q.volume}
    for sym, q in zip(symbols, quotes)
])
print(df)
```

### Order History

```python
account = kis.account()
orders = account.orders()  # Get all orders

for order in orders:
    print(f"{order.symbol}: {order.quantity} @ {order.price:,} KRW")
```

---

## System Requirements

- **Python**: 3.8+
- **OS**: Linux, macOS, Windows
- **Dependencies**:
  - requests >= 2.25.0
  - pyyaml >= 5.4
  - websockets >= 10.0 (optional, for real-time updates)

---

## Community & Support

- 📝 **Issues**: [GitHub Issues](https://github.com/visualmoney/vm-stock-kis/issues)
- 💬 **Questions**: [GitHub Issues](https://github.com/visualmoney/vm-stock-kis/issues)
- 📧 **Email**: <support@vm-stock-kis.org>
- 🌐 **Website**: [https://vm-stock-kis.org](https://vm-stock-kis.org)

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

**Getting Started with Development**:

```bash
# Clone the repository
git clone https://github.com/visualmoney/vm-stock-kis.git
cd vm-stock-kis

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linter
pylint src/vmkis/
```

---

## License

This project is licensed under the MIT License - see [LICENCE](../../../LICENCE) file for details.

---

## Disclaimer

**IMPORTANT**: This library is provided "as-is" for educational and development purposes. The developers are not responsible for:

- 💸 **Financial losses** from incorrect trading
- 🔐 **Security issues** from misuse of API credentials
- 📊 **Data accuracy** issues from the Korea Investment & Securities API
- ⚖️ **Legal compliance** with financial regulations

**Please use responsibly and thoroughly test in sandbox environments before live trading.**

---

## Acknowledgments

- 🙏 Korea Investment & Securities for the API
- 👥 Community contributors for bug reports and improvements
- 📚 Documentation contributors for translations

---

## Changelog

See [CHANGELOG.md](../../../CHANGELOG.md) for version history and updates.

---

**Version**: 2.2.0
**Last Updated**: 2025-12-20
**Status**: 🟢 Stable

---

### Language Selection

- 🇰🇷 [한국어](../ko/README.md)
- 🇬🇧 [English](README.md)
