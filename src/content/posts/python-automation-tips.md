---
title: "Python 自动化实战：10个让你效率翻倍的脚本"
published: 2026-04-17
description: "分享10个实用的 Python 自动化脚本，涵盖文件处理、网页抓取、Excel 操作等日常场景"
tags: ["Python", "自动化", "效率"]
image: ""
category: "技术"
---
# Python 自动化实战：10个让你效率翻倍的脚本

Python 不只是用来写 Web 应用和数据分析的。在日常工作中，很多重复性任务都可以用 Python 脚本自动化。

这里分享 10 个我常用的自动化脚本，每个都能在 5 分钟内用起来。

## 1. 批量重命名文件

```python
import os
from pathlib import Path

def batch_rename(directory, pattern, replacement):
    """批量重命名文件"""
    for filepath in Path(directory).glob(pattern):
        new_name = filepath.name.replace(old_text, new_text)
        filepath.rename(filepath.parent / new_name)

# 使用：把所有 .txt 文件中的 "old" 替换为 "new"
batch_rename("./documents", "*.txt", "old", "new")
```

## 2. 自动整理下载文件夹

```python
import shutil
from pathlib import Path

def organize_downloads(download_dir):
    """按文件类型整理下载文件夹"""
    categories = {
        "图片": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "文档": [".pdf", ".doc", ".docx", ".txt", ".md"],
        "视频": [".mp4", ".mkv", ".avi", ".mov"],
        "压缩包": [".zip", ".rar", ".7z", ".tar.gz"],
        "代码": [".py", ".js", ".ts", ".html", ".css"],
    }
    
    for file in Path(download_dir).iterdir():
        if not file.is_file():
            continue
        for category, extensions in categories.items():
            if file.suffix.lower() in extensions:
                dest = Path(download_dir) / category
                dest.mkdir(exist_ok=True)
                shutil.move(str(file), dest / file.name)
                break

organize_downloads("~/Downloads")
```

## 3. Excel 数据处理

```python
import openpyxl

def merge_excel_files(file_paths, output_path):
    """合并多个 Excel 文件"""
    merged = openpyxl.Workbook()
    merged.remove(merged.active)
    
    for path in file_paths:
        wb = openpyxl.load_workbook(path)
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            new_sheet = merged.create_sheet(sheet_name)
            for row in sheet.iter_rows(values_only=True):
                new_sheet.append(row)
    
    merged.save(output_path)

merge_excel_files(["data1.xlsx", "data2.xlsx"], "merged.xlsx")
```

## 4. 网页内容抓取

```python
import requests
from bs4 import BeautifulSoup

def scrape_article(url):
    """抓取网页文章内容"""
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # 提取标题
    title = soup.find("h1").get_text(strip=True)
    
    # 提取正文
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    content = "\n\n".join(paragraphs)
    
    return title, content

title, content = scrape_article("https://example.com/article")
print(f"标题: {title}")
print(f"内容: {content[:200]}...")
```

## 5. 自动发送邮件

```python
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_addr):
    """发送邮件（需配置 SMTP）"""
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = "your@email.com"
    msg["To"] = to_addr
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your@email.com", "app_password")
        server.send_message(msg)

send_email("日报", "今天完成了XX功能...", "boss@company.com")
```

## 6. 图片批量压缩

```python
from PIL import Image
from pathlib import Path

def compress_images(directory, quality=85, max_size=1920):
    """批量压缩图片"""
    for img_path in Path(directory).rglob("*.[jp][pn]g"):
        img = Image.open(img_path)
        
        # 等比缩放
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size))
        
        # 压缩保存
        img.save(img_path, quality=quality, optimize=True)
        print(f"压缩: {img_path.name}")

compress_images("./images")
```

## 7. 自动备份文件

```python
import shutil
from datetime import datetime
from pathlib import Path

def backup_files(source, backup_dir):
    """自动备份文件到带日期的文件夹"""
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path(backup_dir) / f"backup_{date_str}"
    dest.mkdir(parents=True, exist_ok=True)
    
    for item in Path(source).rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(source)
            target = dest / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
    
    print(f"备份完成: {dest}")

backup_files("./important_files", "./backups")
```

## 8. 监控网站状态

```python
import requests
import time

def monitor_website(url, check_interval=60):
    """监控网站可用性"""
    while True:
        try:
            resp = requests.get(url, timeout=10)
            status = "✅ 正常" if resp.status_code == 200 else f"⚠️ 异常 ({resp.status_code})"
        except Exception as e:
            status = f"❌ 无法访问: {e}"
        
        print(f"[{time.strftime('%H:%M:%S')}] {url} - {status}")
        time.sleep(check_interval)

monitor_website("https://your-website.com")
```

## 9. JSON 数据处理

```python
import json
from pathlib import Path

def process_json_files(directory, key_to_extract):
    """从多个 JSON 文件中提取特定字段"""
    results = []
    for json_file in Path(directory).glob("*.json"):
        data = json.loads(json_file.read_text())
        if key_to_extract in data:
            results.append({
                "file": json_file.name,
                "value": data[key_to_extract]
            })
    
    # 输出为新的 JSON 文件
    Path(directory / "extracted.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2)
    )
    return results

process_json_files("./data", "username")
```

## 10. 自动生成日报

```python
from datetime import datetime, timedelta

def generate_daily_report(tasks):
    """生成工作日报"""
    date = datetime.now().strftime("%Y年%m月%d日")
    
    report = f"""# 工作日报 - {date}

## 今日完成
"""
    for i, task in enumerate(tasks, 1):
        report += f"{i}. {task}\n"
    
    report += f"""
## 明日计划
1. （待填写）

## 备注
无
"""
    return report

tasks = [
    "完成用户登录模块开发",
    "修复订单列表分页 bug",
    "参加项目周会",
    "代码审查 3 个 PR",
]

report = generate_daily_report(tasks)
print(report)
```

## 进阶：用 cron 定时执行

在 Linux/Mac 上，用 `crontab -e` 添加定时任务：

```bash
# 每天早上 9 点自动整理下载文件夹
0 9 * * * python3 /path/to/organize_downloads.py

# 每小时检查网站状态
0 * * * * python3 /path/to/monitor_website.py

# 每天晚上 10 点自动备份
0 22 * * * python3 /path/to/backup_files.py
```

## 总结

这些脚本都很简单，但能帮你省下大量重复劳动的时间。关键是**识别哪些任务是重复性的**，然后用脚本自动化。

Python 的优势在于：
- 语法简洁，学习成本低
- 标准库丰富，不需要装太多第三方包
- 生态完善，几乎什么都能做

**记住：程序员的价值不在于写代码，而在于用代码解决问题。**

---

*你有其他想自动化的场景？欢迎留言讨论。*
