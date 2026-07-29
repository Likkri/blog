---
title: "把一台 Mac 变成个人网站源站：Cloudflare Tunnel 实战复盘"
published: 2026-07-30
description: "记录 qinkening.me 从云服务器切换到本机静态源站的架构、自动启动、DNS、验证与风险边界。"
tags: ["Cloudflare Tunnel", "macOS", "自托管"]
category: "个人基础设施"
---

# 为什么把网站放回自己的电脑

个人静态博客对算力要求很低，却常常需要一整台云服务器来承载。为了更方便地直接维护文件，我把 `qinkening.me` 的源站切换到日常使用的 Mac，再通过 Cloudflare Tunnel 暴露到公网。

最终链路是：

```text
访客浏览器
    ↓ HTTPS
Cloudflare 边缘网络
    ↓ 加密 Tunnel
本机 cloudflared
    ↓ HTTP 127.0.0.1:8765
静态文件服务
```

路由器不需要开放入站端口，本机服务也只监听回环地址。但这并不意味着“电脑关机网站仍然可用”：Tunnel 解决的是连接方式，不是高可用。

## 本地服务只监听回环地址

静态目录可以用 Python 标准库快速提供服务：

```bash
python3 -m http.server 8765 \
  --bind 127.0.0.1 \
  --directory /path/to/site
```

监听 `127.0.0.1` 能避免同一局域网中的其他设备直接访问该端口。公网请求必须经过 Tunnel，TLS、域名和边缘策略都留在 Cloudflare 一侧。

生产环境中我把这条命令放进 macOS LaunchAgent，并启用 `RunAtLoad` 与 `KeepAlive`。这样用户登录后服务会启动，进程意外退出时也会被拉起。

## Tunnel 配置

命名 Tunnel 的配置可以保持很小：

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /secure/path/tunnel-credentials.json

ingress:
  - hostname: qinkening.me
    service: http://127.0.0.1:8765
  - hostname: www.qinkening.me
    service: http://127.0.0.1:8765
  - service: http_status:404
```

最后一条兜底规则很重要。没有它时，未匹配的主机名可能得到难以理解的行为；明确返回 `404` 更容易观察和排错。

凭据文件只用于这一条 Tunnel，权限应限制为当前用户读取。用于创建 DNS 路由的账户级证书在操作完成后可以移除，避免长期保留权限更高的认证材料。

## 一次 525 错误教会我的事

切换过程中，主页可以打开，但分页出现 Cloudflare `525 SSL handshake failed`。问题不在分页代码，而在 DNS 仍有旧记录：不同请求被送往原云服务器，Cloudflare 与旧源站的 TLS 握手失败。

修复过程不是继续改前端，而是：

1. 核对根域名和 `www` 的每一条 DNS 记录；
2. 删除冲突的旧 A 记录；
3. 将两个主机名都绑定到同一个 Tunnel；
4. 等待边缘配置生效后逐页验证。

这个案例提醒我：浏览器里看到的页面错误不一定来自页面。先判断故障发生在浏览器、边缘、DNS、Tunnel 还是源站，能节省大量无效修改。

## 验证不能只看首页

我选择了几条关键路径：

```text
/
/page/2/
/archive/
/search/
/about/
```

每条路径都要从公网返回 `200`。随后重启静态服务和 `cloudflared`，再次请求带随机查询参数的页面，并查看本机日志是否出现对应记录。

这样可以同时验证：

- DNS 已指向新入口；
- Cloudflare 边缘证书正常；
- Tunnel 已注册连接；
- 请求确实抵达本机，而不是只命中旧缓存；
- LaunchAgent 能在进程退出后恢复。

## 合盖与睡眠

Mac 作为源站时，最容易忽略的是电源状态。普通的“屏幕关闭”与“系统睡眠”不同；系统睡眠后，CPU、网络和 Tunnel 都不会持续工作。

当前方案在接电时关闭系统与磁盘空闲睡眠，并使用防休眠工具处理合盖场景。即便如此，机器仍应保持：

- 连接电源；
- 用户已登录；
- 网络稳定；
- 放在通风表面；
- 不放入包内或覆盖散热口。

如果这是商业服务，我不会把日常笔记本当作唯一源站。更稳妥的方案是独立小主机、云存储静态托管或多源站切换。

## 回退比上线更重要

切 DNS 前，我记录了旧记录类型、IP 和代理状态。出现无法快速定位的问题时，可以恢复旧入口并停止 Tunnel，而不是在生产故障中继续试错。

一个完整部署至少包含四份信息：当前架构、启动方式、日志位置和回退步骤。把这些写下来，才算真正拥有自己的基础设施。
