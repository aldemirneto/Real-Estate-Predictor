"""Collect a local JSON catalogue without connecting to or modifying a database."""
import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Transform.DataCleaner import DataCleaner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", nargs="+", default=["LopesLT", "LopesRTG"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    batches, failures = [], {}
    for source in args.sources:
        try:
            cls = getattr(importlib.import_module(f"Extract.{source}Scraper"), f"{source}Scraper")
            rows = cls().scrape()
            if not rows:
                raise RuntimeError("Extração vazia")
            batches.append(rows)
            print(f"{source}: {len(rows)} imóveis", file=sys.stderr)
        except Exception as exc:
            failures[source] = str(exc)
            print(f"{source}: {exc}", file=sys.stderr)
    rows = DataCleaner(batches).validate_data()
    if not rows:
        raise SystemExit("Nenhum resultado; arquivo anterior preservado")
    result = {}
    for row in rows:
        try:
            row["preco"] = float(row["preco"])
            row["area"] = float(row["area"]) if row.get("area") is not None else None
            if row["preco"] <= 0 or (row["area"] is not None and row["area"] <= 0):
                continue
            for key in ["quartos", "banheiros", "vagas"]:
                row[key] = int(row[key]) if row.get(key) is not None else None
            row["imobiliaria"] = row.pop("Imobiliaria")
            row["status"] = row.pop("Status")
            result[row["link"]] = row
        except (ValueError, TypeError, KeyError):
            continue
    if not result:
        raise SystemExit("Nenhum imóvel válido; arquivo anterior preservado")
    # Keep previous records of sources that were not refreshed or failed.
    if args.output.exists():
        old = json.loads(args.output.read_text())
        refreshed = {p["imobiliaria"] for p in result.values()}
        for p in old.get("properties", []):
            if p["imobiliaria"] not in refreshed:
                result.setdefault(p["link"], p)
    now = datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix(".tmp")
    temp.write_text(json.dumps({"last_update": now, "failures": failures, "properties": list(result.values())}, ensure_ascii=False, indent=2, allow_nan=False))
    temp.replace(args.output)
    print(f"Catálogo salvo: {len(result)} imóveis", file=sys.stderr)


if __name__ == "__main__":
    main()
