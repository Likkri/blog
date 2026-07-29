# 覃科宁的博客

[![Website](https://img.shields.io/badge/website-qinkening.me-0ea5e9)](https://qinkening.me)
[![Astro](https://img.shields.io/badge/Astro-5-ff5d01?logo=astro)](https://astro.build/)
[![License](https://img.shields.io/badge/content-CC_BY--NC--SA_4.0-22c55e)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

这是我的公开技术笔记与项目复盘，Base 广西南宁，关注 AI 应用、全栈开发、个人基础设施和开源协作。

站点不是只有主题外壳：每篇文章都尽量记录真实背景、工程取舍、可复现步骤、验证方法与失败经验。

## 内容方向

- AI 辅助开发：如何约束任务、验证输出并保留可维护性。
- 本机基础设施：Cloudflare Tunnel、静态站点、自启动与监控。
- Web 工程：Astro 内容建模、静态生成、搜索与部署。
- 开源协作：从最小复现到高质量 issue 和可审查 PR。

## 可复用工具

仓库包含一个只依赖 Python 标准库的网站健康检查 CLI：

```bash
python3 tools/site_health_check.py https://qinkening.me \
  --contains "覃科宁的博客" \
  --retries 2 \
  --json
```

它会检查状态码、响应内容、延迟和最终跳转地址，并通过退出码接入 cron、
launchd 或 CI。完整说明见 [`tools/README.md`](tools/README.md)。

## 本地开发

需要 Node.js 20+ 与 pnpm 9+：

```bash
pnpm install
pnpm dev
```

生产构建：

```bash
pnpm check
pnpm build
```

构建结果位于 `dist/`。

## 目录

```text
src/config.ts           站点与个人资料
src/content/spec/       关于页面
src/content/posts/      Markdown 文章
src/assets/             由构建器处理的资源
public/                 原样复制的静态资源
tools/                  可单独复用的运维工具与测试
```

## 内容许可与主题来源

文章内容采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)；站点代码沿用仓库中的 MIT License。界面基于 [Fuwari](https://github.com/saicaca/fuwari) 定制。
