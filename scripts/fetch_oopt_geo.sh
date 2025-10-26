#!/usr/bin/env bash
set -euo pipefail

# активируем venv, если ты не в нём
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

ROSREESTR="./.venv/bin/rosreestr2coord"
if [ ! -x "$ROSREESTR" ]; then
  # fallback: вдруг активировано venv и бинарь в PATH
  ROSREESTR="rosreestr2coord"
fi

LIST="cadastral_list_all.txt"

# A) выгрузка как «Зоны и территории» (тип 5)
$ROSREESTR -l "$LIST" -t 5 -o export_oopt_raw.geojson || true

# B) fallback — попробовать без типа (как участки)
$ROSREESTR -l "$LIST" -o export_oopt_raw_fallback.geojson || true

# C) объединить два geojson без глобального mapshaper — через npx
if [ -f export_oopt_raw_fallback.geojson ]; then
  npx -y mapshaper \
    -i export_oopt_raw.geojson export_oopt_raw_fallback.geojson combine-files \
    -merge-layers force \
    -o export_oopt_raw.geojson
fi

# D) джоин атрибутов (название, категория, район)
python3 join_attrs.py export_oopt_raw.geojson oopt_attrs.csv export.geojson

echo "Готово: export.geojson"
