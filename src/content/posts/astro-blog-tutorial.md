---
title: "从零搭建个人博客：Astro + Fuwari 完整教程"
published: 2026-04-17
description: "手把手教你用 Astro 和 Fuwari 主题搭建一个漂亮的个人博客，免费部署到 GitHub Pages"
tags: ["Astro", "博客", "教程"]
image: ""
category: "教程"
---
# 从零搭建个人博客：Astro + Fuwari 完整教程

想要一个自己的博客？不想花钱买服务器？这篇文章教你从零开始，30分钟搞定。

## 为什么选 Astro + Fuwari？

**Astro** 是目前最火的静态网站框架之一：
- 构建速度极快（纯静态 HTML）
- 支持 MDX、Vue、React 等组件
- SEO 友好
- 零 JavaScript 默认加载

**Fuwari** 是一个精美的 Astro 博客主题：
- GitHub 4400+ Stars
- 支持亮色/暗色主题
- 内置标签、分类、搜索
- 响应式设计，手机端也很好看

## 第一步：准备工作

你需要：
- 一个 [GitHub](https://github.com) 账号
- 安装 [Node.js](https://nodejs.org/)（18+）
- 安装 [pnpm](https://pnpm.io/)

```bash
# 安装 pnpm
npm install -g pnpm
```

## 第二步：创建项目

```bash
# 克隆 Fuwari 模板
git clone https://github.com/saicaca/fuwari.git my-blog
cd my-blog

# 安装依赖
pnpm install
```

## 第三步：个性化配置

编辑 `src/config.ts`，修改以下内容：

```typescript
const siteConfig = {
  title: "你的名字的博客",
  subtitle: "你的副标题",
  author: "你的名字",
  avatar: "/images/avatar.png",  // 头像
  language: "zh-CN",  // 中文
  // ...
};
```

### 添加社交链接

```typescript
const navBarConfig = {
  links: [
    { name: "GitHub", url: "https://github.com/yourname" },
    { name: "掘金", url: "https://juejin.cn/user/yourid" },
  ],
};
```

### 修改个人信息

```typescript
const profileConfig = {
  name: "你的名字",
  bio: "一句话介绍自己",
  avatar: "/images/avatar.png",
};
```

## 第四步：写文章

在 `src/content/posts/` 目录下创建 `.md` 文件：

```markdown
---
title: "我的第一篇文章"
published: 2026-04-17
description: "文章简介"
tags: ["标签1", "标签2"]
---

# 标题

文章内容...
```

## 第五步：本地预览

```bash
pnpm dev
```

打开 `http://localhost:4321` 预览效果。

## 第六步：部署到 GitHub Pages

### 1. 创建 GitHub 仓库

在 GitHub 上创建一个名为 `你的用户名.github.io` 的仓库，或者任意名称的仓库。

### 2. 推送代码

```bash
git remote add origin https://github.com/yourname/yourrepo.git
git branch -M main
git push -u origin main
```

### 3. 配置 GitHub Actions

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install
      - run: pnpm build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
```

### 4. 启用 GitHub Pages

在仓库 Settings → Pages 中，Source 选择 "GitHub Actions"。

推送代码后，几分钟内你的博客就会上线！

## 进阶优化

### 自定义域名

1. 买一个域名（推荐 Namesilo、Cloudflare）
2. 在仓库 Settings → Pages → Custom domain 中填写
3. 在域名 DNS 中添加 CNAME 记录指向 `你的用户名.github.io`

### 添加评论系统

推荐 [Giscus](https://giscus.app/)（基于 GitHub Discussions），免费且无广告。

### 添加搜索

Fuwari 内置了 Pagefind 搜索，构建时自动生成索引。

### SEO 优化

- 确保每篇文章都有 `description`
- 使用合适的 `tags` 和 `category`
- 在 `astro.config.mjs` 中设置正确的 `site` URL
- 添加 `robots.txt` 和 `sitemap`（Astro 的 sitemap 插件会自动生成）

## 常见问题

**Q: 构建报错怎么办？**
A: 检查 Node.js 版本是否 >= 18，删除 `node_modules` 重新 `pnpm install`。

**Q: 图片怎么放？**
A: 放在 `public/images/` 目录下，引用时用 `/images/xxx.png`。

**Q: 怎么修改主题颜色？**
A: 编辑 `src/styles/global.css` 中的 CSS 变量。

## 总结

用 Astro + Fuwari 搭建博客的优势：
- ✅ 完全免费
- ✅ 速度快（纯静态）
- ✅ SEO 友好
- ✅ 自动部署
- ✅ 主题美观

30分钟，从零到上线，就是这么简单。

---

*有问题？欢迎在评论区留言，我会一一解答。*
