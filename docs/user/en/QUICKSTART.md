# Quick Start Guide (English)

**Language**: [한국어](../../QUICKSTART.md) | [English](QUICKSTART.md)

Get up and running with VM-Stock-KIS in 5 minutes!

---

## Prerequisites

- ✅ Python 3.8 or higher
- ✅ Korea Investment & Securities (KIS) account
- ✅ App Key and Secret from [KIS Developer Portal](https://developer.kis.co.kr)
- ✅ pip (Python package manager)

---

## Step 1: Installation (1 minute)

```bash
# Install VmKis from PyPI
pip install vmkis

# Verify installation
python -c "import vmkis; print(f'VmKis {vmkis.__version__} installed successfully')"
```

---

## Step 2: Get Your API Credentials (2 minutes)

### For Korea Residents (Real Trading)

1. Go to [KIS Developer Portal](https://developer.kis.co.kr)
2. Sign in with your KIS account
3. Create a new app
4. Copy your **App Key** and **App Secret**
5. Note your **Account Number** (format: `00000000-01`)

### For Testing (Sandbox/Virtual Trading)

Use the sandbox credentials provided by KIS for testing.

---

## Step 3: Configure Your Credentials (1 minute)

### Option A: Environment Variables (Recommended)

```bash
# Linux/macOS
export VMKIS_APP_KEY="your_app_key_here"
export VMKIS_APP_SECRET="your_app_secret_here"
export VMKIS_ACCOUNT_NUMBER="00000000-01"

# Windows PowerShell
$env:VMKIS_APP_KEY="your_app_key_here"
$env:VMKIS_APP_SECRET="your_app_secret_here"
$env:VMKIS_ACCOUNT_NUMBER="00000000-01"
```

```python
from vmkis import VmKis

# Loads credentials from environment
kis = VmKis()
```

### Option B: Configuration File

Create `config.yaml`:

```yaml
kis:
  server: real              # Use "virtual" for sandbox
  app_key: YOUR_APP_KEY
  app_secret: YOUR_APP_SECRET
  account_number: "00000000-01"

# Optional: Logging configuration
logging:
  level: INFO
  json_format: true
```

```python
from vmkis.helpers import load_config
from vmkis import VmKis

config = load_config("config.yaml")
kis = VmKis(**config['kis'])
```

### Option C: Direct Parameters

```python
from vmkis import VmKis

kis = VmKis(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
    account_number="00000000-01",
    server="real"  # or "virtual" for testing
)
```

---

## Step 4: Your First API Call (1 minute)

### Example 1: Get Stock Quote

```python
from vmkis import VmKis

# Initialize client
kis = VmKis()

# Get stock quote (Samsung Electronics: 005930)
samsung = kis.stock("005930")
quote = samsung.quote()

# Print price information
print(f"Symbol: {quote.symbol}")
print(f"Current Price: {quote.price:,} KRW")
print(f"High: {quote.high:,} KRW")
print(f"Low: {quote.low:,} KRW")
print(f"Volume: {quote.volume:,} shares")
print(f"Change Rate: {quote.change_rate:+.2f}%")
```

**Output**:

```text
Symbol: 005930
Current Price: 60,000 KRW
High: 61,500 KRW
Low: 59,800 KRW
Volume: 10,500,000 shares
Change Rate: +2.45%
```

### Example 2: Check Account Balance

```python
# Get account information
account = kis.account()
balance = account.balance()

# Print balance information
print(f"Cash Available: {balance.cash:,} KRW")
print(f"Total Evaluated Amount: {balance.evaluated_amount:,} KRW")
print(f"Profit/Loss: {balance.profit_loss:,} KRW")
print(f"Profit Rate: {balance.profit_rate:+.2f}%")
```

### Example 3: Get Multiple Stock Quotes

```python
import pandas as pd

# Define symbols
symbols = ["005930", "000660", "051910"]  # Samsung, SK Hynix, LG Chemical
names = ["Samsung", "SK Hynix", "LG Chemical"]

# Fetch quotes
data = []
for symbol, name in zip(symbols, names):
    quote = kis.stock(symbol).quote()
    data.append({
        "Name": name,
        "Symbol": symbol,
        "Price": quote.price,
        "Change": f"{quote.change_rate:+.2f}%",
        "Volume": quote.volume
    })

# Create DataFrame
df = pd.DataFrame(data)
print(df)
```

**Output**:

```text
        Name Symbol    Price   Change     Volume
0    Samsung  005930    60000    +2.45%  10500000
1  SK Hynix  000660    85000    +1.23%   5200000
2 LG Chemical 051910    75000    -0.50%   2100000
```

---

## Troubleshooting

### Error: "API key or secret is invalid"

**Solution**:

1. Check your App Key and Secret are correct
2. Ensure credentials are not expired
3. Try regenerating credentials from KIS portal

### Error: "Market is closed"

**Solution**:

1. Check Korean market trading hours: 09:00~15:30 KST
2. Verify the date is not a Korean holiday
3. See [REGIONAL_GUIDES.md](../../../docs/guidelines/REGIONAL_GUIDES.md) for holidays

### Error: "Connection refused"

**Solution**:

1. Check your internet connection
2. Verify firewall allows API access
3. Try again in a few moments (temporary network issue)
4. Check KIS API status page

### Error: "Too many requests" (429)

**Solution**:

1. Wait a few moments before retrying
2. Use the built-in retry mechanism:

   ```python
   from vmkis.utils.retry import with_retry

   @with_retry(max_retries=5)
   def safe_quote_fetch(symbol):
       return kis.stock(symbol).quote()
   ```

---

## Next Steps

### 📚 Learn More

- **Full API Reference**: [API Documentation](./README.md)
- **FAQ**: [Frequently Asked Questions](./FAQ.md)
- **Configuration Guide**: [CONFIGURATION.md](./CONFIGURATION.md)
- **Examples**: [examples/](../../../examples/)

### 🚀 Common Tasks

```python
# Buy stocks
order = kis.stock("005930").buy(quantity=10, price=60000)

# Sell stocks
order = kis.stock("005930").sell(quantity=5, price=61000)

# Cancel an order
kis.stock("005930").cancel(order_id="123456")

# Subscribe to real-time updates
kis.stock("005930").subscribe(on_price_update)

# Get order history
orders = kis.account().orders()
```

### 🔧 Advanced Features

- **Error Handling**: [Handling Different Exceptions](./FAQ.md#error-handling)
- **Retry Logic**: [Auto-Retry with Exponential Backoff](../../../docs/guidelines/MULTILINGUAL_SUPPORT.md)
- **Logging**: [JSON Structured Logging](./README.md#-structured-logging-elk-compatible)
- **Real-Time Updates**: [WebSocket Subscriptions](./README.md#real-time-price-updates-websocket)

---

## Quick Reference

### Stock Codes (Popular)

| Company | Code | Industry |
|---------|------|----------|
| Samsung Electronics | 005930 | Semiconductors |
| SK Hynix | 000660 | Semiconductors |
| LG Electronics | 066570 | Electronics |
| Hyundai Motor | 005380 | Automotive |
| NAVER | 035420 | Internet |
| Kakao | 035720 | Internet |
| Celltrion | 068270 | Biotech |

### Market Hours

```text
Normal Trading: 09:00 ~ 15:30 KST
After-Hours:    15:40 ~ 16:00 KST
Closed:         Weekends & Korean holidays
```

### Important Links

- [KIS API Documentation](https://www.kis.co.kr/api)
- [Korea Exchange (KRX)](http://www.krx.co.kr/)
- [VmKis GitHub](https://github.com/yourusername/vm-stock-kis)

---

## Getting Help

- 💬 **GitHub Issues**: [Report bugs](https://github.com/yourusername/vm-stock-kis/issues)
- 💭 **GitHub Discussions**: [Ask questions](https://github.com/yourusername/vm-stock-kis/discussions)
- 📧 **Email**: <support@vm-stock-kis.org>
- 📚 **Wiki**: [Community documentation](https://github.com/yourusername/vm-stock-kis/wiki)

---

**Happy Trading!** 🚀

---

**Last Updated**: 2025-12-20
**Version**: 2.2.0
**Status**: 🟢 Stable
