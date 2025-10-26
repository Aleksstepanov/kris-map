#!/usr/bin/env python3
import sys, json, csv

if len(sys.argv) < 4:
    print("Usage: join_attrs.py input.geojson attrs.csv output.geojson")
    sys.exit(1)

inp, attrs_csv, outp = sys.argv[1], sys.argv[2], sys.argv[3]

# Считываем словарь атрибутов по кадастровому номеру
attrs_by_cad = {}
with open(attrs_csv, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cad = (row.get("cadastral") or "").strip()
        if cad:
            attrs_by_cad[cad] = {
                "name": row.get("name"),
                "category": row.get("category"),
                "profile": row.get("profile"),
                "district": row.get("district"),
            }

# Загружаем GeoJSON
with open(inp, encoding='utf-8') as f:
    gj = json.load(f)

def get_cad(props):
    # В разных выдачах свойство может называться по-разному,
    # но чаще всего 'cn' (кадастровый номер).
    for key in ("cn", "cadastral", "CADNOMER", "cad_num"):
        v = props.get(key)
        if v:
            return str(v).strip()
    # Иногда встречаются вложенные структуры — оставим попытку простой.
    return None

for feat in gj.get("features", []):
    props = feat.setdefault("properties", {})
    cad = get_cad(props)
    if cad and cad in attrs_by_cad:
        props.update(attrs_by_cad[cad])
    # Нормализуем тип объекта для карты
    if "category" in props and isinstance(props["category"], str):
        if "памятник" in props["category"].lower():
            props.setdefault("type", "Памятник природы")
        elif "заказник" in props["category"].lower():
            props.setdefault("type", "Заказник")
        elif "парк" in props["category"].lower():
            props.setdefault("type", "Парк/ООПТ")
        else:
            props.setdefault("type", "ООПТ")

with open(outp, "w", encoding="utf-8") as f:
    json.dump(gj, f, ensure_ascii=False)
print("Saved", outp)
