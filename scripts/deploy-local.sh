#!/bin/zsh

set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"
site_dir="${HOME}/Sites/qinkening.me"

cd "$project_dir"
ASTRO_TELEMETRY_DISABLED=1 corepack pnpm build

if [[ ! -f "$project_dir/dist/index.html" ]]; then
  print -u2 "构建失败：dist/index.html 不存在"
  exit 1
fi

mkdir -p "$site_dir"
/usr/bin/rsync -a --delete "$project_dir/dist/" "$site_dir/"

print "部署完成：https://qinkening.me"
