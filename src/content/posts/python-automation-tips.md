---
title: "用 Python 写一个不轻易误报的网站健康检查"
published: 2026-07-27
description: "从状态码、超时、重试到结构化日志，写一个适合个人站点的最小健康检查脚本。"
tags: ["Python", "可观测性", "运维"]
category: "工程实践"
---

# 一个健康检查脚本需要回答什么

个人网站上线后，最常见的监控方式是定时请求首页，只要返回 `200` 就认为正常。但首页可能被 CDN 缓存，源站已经离线；也可能首页正常，分页或搜索资源却损坏。

一个够用的最小检查器至少要回答：

- DNS 与 TLS 是否能建立连接？
- 关键页面是否返回预期状态码？
- 请求是否在合理时间内完成？
- 短暂抖动是否会被误判成故障？
- 失败记录能否交给其他工具继续处理？

## 检查多个用户路径

下面的脚本只使用 Python 标准库，检查首页、第二页、归档和搜索页。每个地址最多尝试三次，并输出一行 JSON，方便后续接入日志工具。

```python
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


URLS = [
    "https://qinkening.me/",
    "https://qinkening.me/page/2/",
    "https://qinkening.me/archive/",
    "https://qinkening.me/search/",
]


@dataclass
class Result:
    url: str
    ok: bool
    status: int | None
    elapsed_ms: int
    error: str | None


def check(url: str, attempts: int = 3, timeout: float = 8.0) -> Result:
    last_error: str | None = None
    started = time.perf_counter()

    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                url,
                headers={"User-Agent": "qinkening-healthcheck/1.0"},
                method="GET",
            )
            with urlopen(request, timeout=timeout) as response:
                status = response.status
                response.read(256)
                elapsed = int((time.perf_counter() - started) * 1000)
                return Result(url, status == 200, status, elapsed, None)
        except HTTPError as exc:
            last_error = f"HTTP {exc.code}"
        except URLError as exc:
            last_error = str(exc.reason)
        except TimeoutError:
            last_error = "timeout"

        if attempt < attempts:
            time.sleep(attempt)

    elapsed = int((time.perf_counter() - started) * 1000)
    return Result(url, False, None, elapsed, last_error)


def main() -> int:
    results = [check(url) for url in URLS]
    event = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "ok": all(item.ok for item in results),
        "results": [asdict(item) for item in results],
    }
    print(json.dumps(event, ensure_ascii=False))
    return 0 if event["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

## 为什么读取少量响应体

只发 `HEAD` 请求很省流量，但有些应用没有正确实现 `HEAD`，或者 CDN 对 `HEAD` 与 `GET` 使用不同缓存策略。这里发送 `GET`，只读取前 256 字节，兼顾兼容性和资源消耗。

如果需要更强验证，可以检查页面中是否包含稳定标记，例如站点标题。但不要依赖经常变化的完整文案，否则每次更新内容都会触发误报。

## 重试不是无限等待

重试能过滤瞬时网络抖动，也会推迟真正故障的发现。脚本采用递增等待：第一次失败后等一秒，第二次后等两秒。每个请求仍然有独立超时，避免任务永久卡住。

对于个人博客，三次尝试通常足够；支付或认证系统需要更严格的分层监控，不能直接套用这个参数。

## CDN 正常不等于源站正常

如果页面被 CDN 缓存，即使本机源站离线，公开 URL 仍可能暂时返回 `200`。我会额外做两种检查：

1. 请求带随机查询参数的页面，降低命中旧缓存的概率；
2. 查看本机 HTTP 日志，确认请求确实到达源站。

监控的目标不是制造一个绿色图标，而是尽量准确地描述系统状态。

## 定时执行

macOS 上可以用 LaunchAgent 定时运行，Linux 上可以用 systemd timer。无论选择哪一种，都应保留标准输出和错误日志，并确保脚本返回非零退出码时能被观察到。

下一步可以把失败事件发送到邮件、Webhook 或消息机器人，但通知通道应该与被监控服务分离：如果网站和通知都依赖同一台电脑，断电时你不会收到任何消息。
