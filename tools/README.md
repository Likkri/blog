# Site Health Check

A dependency-free Python CLI for checking a website without treating every
temporary network error as an outage.

## Usage

```bash
python3 site_health_check.py https://example.com
python3 site_health_check.py https://example.com \
  --contains "Expected heading" \
  --retries 2 \
  --timeout 8 \
  --json
```

Options:

- `--expect-status CODE` accepts an HTTP status and can be repeated.
- `--contains TEXT` verifies UTF-8 response content.
- `--retries N` retries network errors and HTTP 5xx responses.
- `--backoff SECONDS` controls linear retry delay.
- `--json` returns machine-readable output.

Exit codes:

- `0`: healthy
- `1`: check completed but the target was unhealthy
- `2`: invalid configuration

## Tests

The tests start a local HTTP server and do not use the public internet:

```bash
cd tools
python3 -m unittest -v test_site_health_check.py
```

## Design choices

- Uses `GET` so an optional content assertion verifies the actual page.
- Does not retry HTTP 4xx responses, which usually require a configuration fix.
- Records the final URL after redirects.
- Caps the response body at 2 MB to avoid accidentally buffering an unbounded
  download.

The related write-up is available at
[用 Python 写一个不轻易误报的网站健康检查](https://qinkening.me/posts/python-automation-tips/).
