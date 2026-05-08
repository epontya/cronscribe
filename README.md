# cronscribe

Convert human-readable schedule descriptions into valid cron expressions with validation and previews.

---

## Installation

```bash
pip install cronscribe
```

---

## Usage

```python
from cronscribe import CronScribe

cs = CronScribe()

# Convert a human-readable description to a cron expression
expression = cs.to_cron("every day at 9am")
print(expression)  # Output: 0 9 * * *

# Preview the next scheduled runs
preview = cs.preview("every Monday at noon", count=3)
for run in preview:
    print(run)
# 2024-01-15 12:00:00
# 2024-01-22 12:00:00
# 2024-01-29 12:00:00

# Validate an existing cron expression
is_valid = cs.validate("0 9 * * 1-5")
print(is_valid)  # True
```

**Supported description formats:**

- `"every hour"`
- `"every weekday at 8:30am"`
- `"every 15 minutes"`
- `"on the 1st of every month at midnight"`

---

## Features

- Natural language parsing for common schedule patterns
- Built-in cron expression validation
- Human-friendly preview of upcoming scheduled times
- Lightweight with minimal dependencies

---

## License

This project is licensed under the [MIT License](LICENSE).