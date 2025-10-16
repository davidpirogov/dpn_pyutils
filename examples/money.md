# Money Module Documentation

## About

The `dpn_pyutils.money` module provides sophisticated currency formatting utilities designed for financial and market display applications. This module implements conventional market display formatting rules for currency values, automatically handling different scales from micro amounts to trillions.

The module is specifically designed for applications that need to display financial data in a user-friendly, market-standard format, such as financial dashboards, trading platforms, accounting systems, and e-commerce applications.

## Examples

### Basic Currency Formatting

```python
from dpn_pyutils.money import format_currency_market_display_float

# Basic currency formatting
price = 123.45
formatted = format_currency_market_display_float(price)
print(f"Price: {formatted}")  # Output: $123.45

# Different currency symbols
eur_price = format_currency_market_display_float(99.99, "€")
btc_price = format_currency_market_display_float(0.002, "₿")

print(f"EUR Price: {eur_price}")
print(f"BTC Price: {btc_price}")
```

### Large Number Formatting

```python
from dpn_pyutils.money import format_currency_market_display_float

# Thousands
thousands = format_currency_market_display_float(1500)
print(f"Thousands: {thousands}")  # Output: $1.50k

# Millions
millions = format_currency_market_display_float(2500000)
print(f"Millions: {millions}")  # Output: $2.5M

# Billions
billions = format_currency_market_display_float(3500000000)
print(f"Billions: {billions}")  # Output: $3.5B

# Trillions
trillions = format_currency_market_display_float(2500000000000)
print(f"Trillions: {trillions}")  # Output: $2.5T
```

### Fractional and Small Amounts

```python
from dpn_pyutils.money import format_currency_market_display_float

# Fractional amounts
fractional = format_currency_market_display_float(0.25)
print(f"Fractional: {fractional}")  # Output: $0.25

# Very small amounts
micro = format_currency_market_display_float(0.0005)
print(f"Micro: {micro}")  # Output: $0.0005

# Extremely small amounts (below 0.000001)
tiny = format_currency_market_display_float(0.0000001)
print(f"Tiny: {tiny}")  # Output: <$0.000001
```

### Negative Values

```python
from dpn_pyutils.money import format_currency_market_display_float

# Negative amounts at different scales
negative_price = format_currency_market_display_float(-123.45)
negative_thousands = format_currency_market_display_float(-1500)
negative_millions = format_currency_market_display_float(-2500000)

print(f"Negative price: {negative_price}")        # Output: -$123.45
print(f"Negative thousands: {negative_thousands}")  # Output: -$1.50k
print(f"Negative millions: {negative_millions}")    # Output: -$2.5M
```

### Custom Suffixes

```python
from dpn_pyutils.money import format_currency_market_display_float

# Add custom suffixes
price_with_margin = format_currency_market_display_float(100, suffix=" margin")
volume_with_unit = format_currency_market_display_float(1000000, suffix=" shares")

print(f"Price with margin: {price_with_margin}")
print(f"Volume with unit: {volume_with_unit}")
```

### Financial Data Display

```python
from dpn_pyutils.money import format_currency_market_display_float

def display_portfolio_value(portfolio):
    """Display a portfolio with various holding values."""
    print("Portfolio Holdings:")
    print("-" * 30)

    for holding in portfolio:
        name = holding['name']
        value = holding['value']
        formatted_value = format_currency_market_display_float(value)

        print(f"{name"15"} | {formatted_value}")

# Example portfolio data
portfolio = [
    {'name': 'Apple Inc.', 'value': 150000},
    {'name': 'Tesla Inc.', 'value': 2500000},
    {'name': 'Bitcoin', 'value': 0.05},
    {'name': 'Cash', 'value': 50000}
]

display_portfolio_value(portfolio)
```

### Price Comparison and Analysis

```python
from dpn_pyutils.money import format_currency_market_display_float

def compare_prices(prices):
    """Compare and analyze price movements."""
    print("Price Analysis:")
    print("-" * 40)

    for item in prices:
        name = item['name']
        current = item['current']
        previous = item['previous']

        current_fmt = format_currency_market_display_float(current)
        previous_fmt = format_currency_market_display_float(previous)
        change = current - previous
        change_fmt = format_currency_market_display_float(change)

        print(f"{name"15"} | {previous_fmt"8"} -> {current_fmt"8"} | {change_fmt}")

# Example price data
prices = [
    {'name': 'Gold', 'current': 1950.50, 'previous': 1920.25},
    {'name': 'Silver', 'current': 23.45, 'previous': 24.10},
    {'name': 'Oil', 'current': 85.30, 'previous': 82.75}
]

compare_prices(prices)
```

## Architecture

### Design Philosophy

The money module implements market-standard formatting conventions:

1. **Scale-Appropriate Formatting**: Automatically selects appropriate suffixes (K, M, B, T) based on value magnitude
2. **Precision Management**: Adjusts decimal places based on the scale and significance of the amount
3. **Visual Clarity**: Uses formatting that is immediately readable and professionally presented
4. **Market Standards**: Follows conventions used in financial markets and trading platforms

### Formatting Rules

#### Value Ranges and Formatting

| Value Range | Formatting | Example | Suffix |
|-------------|------------|---------|---------|
| $0 - $0.01 | 2 decimal places | $12.34 | None |
| $0.01 - $1.00 | 2 decimal places | $0.25 | None |
| $1.00 - $999.99 | 2 decimal places | $123.45 | None |
| $1,000 - $999,999 | 2 decimal places | $1.50k | k |
| $1,000,000 - $999,999,999 | 1 decimal place | $2.5M | M |
| $1,000,000,000 - $999,999,999,999 | 1 decimal place | $3.5B | B |
| $1,000,000,000,000+ | 1 decimal place | $2.5T | T |

#### Special Cases

- **Micro Amounts** (< $0.000001): Displayed as `<$0.000001`
- **Negative Values**: Always show minus sign prefix
- **Zero Values**: Displayed as `$0.00`

### Implementation Strategy

#### Scale Detection Algorithm
```python
# Determine appropriate scale and formatting
if abs(value) >= 1e12:
    # Trillions
    chopped_value = value / 1e12
    formatted_value = "{:.1f}".format(abs(chopped_value))
    suffix = "T"
elif abs(value) >= 1e9:
    # Billions
    chopped_value = value / 1e9
    formatted_value = "{:.1f}".format(abs(chopped_value))
    suffix = "B"
# ... (similar logic for millions, thousands, etc.)
```

#### Precision Handling
- **Large Values**: Reduced decimal precision to maintain readability
- **Small Values**: Appropriate precision to show meaningful differences
- **Micro Values**: Special handling to indicate extremely small amounts

### Performance Characteristics

- **Lightweight**: Minimal computational overhead for formatting
- **Memory Efficient**: No unnecessary object creation
- **Fast Processing**: Optimized for high-frequency formatting needs
- **Scalable**: Handles extreme value ranges efficiently

### Limitations and Considerations

#### Floating-Point Precision
**Important Warning**: This module uses floating-point numbers for display purposes only. For financial calculations involving precision-sensitive operations, use `decimal.Decimal` or integer arithmetic.

```python
# ❌ Don't use for financial calculations
from dpn_pyutils.money import format_currency_market_display_float

# This might have floating-point precision issues
result = 0.1 + 0.2  # Might be 0.30000000000000004
formatted = format_currency_market_display_float(result)

# ✅ Use decimal for calculations
from decimal import Decimal
result = Decimal('0.1') + Decimal('0.2')  # Exactly 0.3
formatted = format_currency_market_display_float(float(result))
```

#### Display vs. Calculation
- **Display Only**: This module is designed for presentation, not computation
- **Rounding**: Uses standard rounding rules which may not be suitable for all financial contexts
- **Precision Loss**: Large numbers may lose precision in floating-point representation

### Best Practices

1. **Separate Display and Calculation**: Use different data types for calculations vs. display
2. **Precision Awareness**: Be aware of floating-point precision limitations
3. **Context-Appropriate Formatting**: Choose formatting based on your specific use case
4. **Testing**: Test formatting with edge cases and boundary values

### Integration Examples

#### Financial Dashboard

```python
from dpn_pyutils.money import format_currency_market_display_float

class FinancialDashboard:
    def __init__(self):
        self.positions = {}

    def add_position(self, symbol, value):
        self.positions[symbol] = value

    def display_portfolio(self):
        print("Portfolio Summary")
        print("=" * 50)
        total = 0

        for symbol, value in self.positions.items():
            formatted_value = format_currency_market_display_float(value)
            print(f"{symbol"10"} | {formatted_value"12"}")
            total += value

        print("-" * 50)
        total_formatted = format_currency_market_display_float(total)
        print(f"{'TOTAL'"10"} | {total_formatted"12"}")

# Usage
dashboard = FinancialDashboard()
dashboard.add_position("AAPL", 150000)
dashboard.add_position("GOOGL", 2500000)
dashboard.add_position("TSLA", 800000)
dashboard.display_portfolio()
```

#### Price Ticker

```python
from dpn_pyutils.money import format_currency_market_display_float

def format_price_ticker(price_data):
    """Format price data for ticker display."""
    symbol = price_data['symbol']
    price = price_data['price']
    change = price_data['change']

    price_fmt = format_currency_market_display_float(price)
    change_fmt = format_currency_market_display_float(change)

    return f"{symbol}: {price_fmt} ({change_fmt})"

# Example usage
price_data = [
    {'symbol': 'BTC', 'price': 45000, 'change': 500},
    {'symbol': 'ETH', 'price': 3000, 'change': -50},
    {'symbol': 'ADA', 'price': 0.45, 'change': 0.02}
]

for data in price_data:
    ticker = format_price_ticker(data)
    print(ticker)
```

### Market Data Integration

#### Real-time Price Display
```python
import time
from dpn_pyutils.money import format_currency_market_display_float

def display_live_prices(price_feed):
    """Simulate live price display."""
    print("Live Price Feed")
    print("=" * 30)

    for update in price_feed:
        symbol = update['symbol']
        price = update['price']
        volume = update['volume']

        price_fmt = format_currency_market_display_float(price)
        volume_fmt = format_currency_market_display_float(volume, suffix=" vol")

        print(f"{symbol"6"} | {price_fmt"10"} | {volume_fmt}")

        # Simulate real-time updates
        time.sleep(1)
```

#### Historical Price Analysis
```python
from dpn_pyutils.money import format_currency_market_display_float

def analyze_price_history(price_history):
    """Analyze and display historical price data."""
    print("Price History Analysis")
    print("=" * 40)

    for record in price_history:
        date = record['date']
        high = record['high']
        low = record['low']
        close = record['close']

        high_fmt = format_currency_market_display_float(high)
        low_fmt = format_currency_market_display_float(low)
        close_fmt = format_currency_market_display_float(close)

        print(f"{date} | H: {high_fmt} | L: {low_fmt} | C: {close_fmt}")
```

### Testing and Validation

```python
import pytest
from dpn_pyutils.money import format_currency_market_display_float

def test_basic_formatting():
    assert format_currency_market_display_float(123.45) == "$123.45"
    assert format_currency_market_display_float(0) == "$0.00"

def test_large_numbers():
    assert format_currency_market_display_float(1500) == "$1.50k"
    assert format_currency_market_display_float(2500000) == "$2.5M"
    assert format_currency_market_display_float(3500000000) == "$3.5B"

def test_negative_values():
    assert format_currency_market_display_float(-123.45) == "-$123.45"
    assert format_currency_market_display_float(-1500) == "-$1.50k"

def test_fractional_values():
    assert format_currency_market_display_float(0.25) == "$0.25"
    assert format_currency_market_display_float(0.0005) == "$0.0005"

def test_micro_values():
    assert format_currency_market_display_float(0.0000001) == "<$0.000001"
```

This comprehensive currency formatting module provides all the tools needed for professional financial data presentation while maintaining simplicity and performance.
