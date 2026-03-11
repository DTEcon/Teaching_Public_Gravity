#!/usr/bin/env python3
"""
Prepare a student-ready gravity dataset for Lecture 7.

This script aggregates Atlas HS6 bilateral flows to country-pair totals for one year,
merges with CEPII gravity covariates, and writes compact outputs intended for student
regression labs (Colab / local notebooks).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_TRADE_FILE = Path("H0_2019.dta")
DEFAULT_GRAVITY_FILE = Path("Gravity_V202010.dta")
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data"

STUDENT_GRAVITY_COLUMNS = [
    "year",
    "iso3_o",
    "iso3_d",
    "dist",
    "distw",
    "distcap",
    "distwces",
    "contig",
    "comlang_off",
    "rta",
    "rta_coverage",
    "rta_type",
    "comlang_ethno",
    "comcol",
    "col45",
    "comleg_pretrans",
    "comleg_posttrans",
    "sibling",
    "col_dep",
    "gdp_o",
    "gdp_d",
    "pop_o",
    "pop_d",
    "gdpcap_o",
    "gdpcap_d",
    "gatt_o",
    "gatt_d",
    "wto_o",
    "wto_d",
    "eu_o",
    "eu_d",
]

BASE_REQUIRED_COLUMNS = ["distw", "contig", "comlang_off", "rta"]
NUMERIC_COLUMNS = [
    "trade_value",
    "dist",
    "distw",
    "distcap",
    "distwces",
    "contig",
    "comlang_off",
    "rta",
    "rta_coverage",
    "rta_type",
    "comlang_ethno",
    "comcol",
    "col45",
    "comleg_pretrans",
    "comleg_posttrans",
    "sibling",
    "col_dep",
    "gdp_o",
    "gdp_d",
    "pop_o",
    "pop_d",
    "gdpcap_o",
    "gdpcap_d",
    "gatt_o",
    "gatt_d",
    "wto_o",
    "wto_d",
    "eu_o",
    "eu_d",
]

DESCRIPTION = {
    "year": "Cross-section year used for the student dataset.",
    "iso3_o": "Exporter ISO3 code (origin country i).",
    "iso3_d": "Importer ISO3 code (destination country j).",
    "pair_cluster": "Country-pair identifier (i_j) for clustered standard errors.",
    "trade_value": "Total bilateral trade flow X_ij in USD levels (Atlas aggregated to pair-year).",
    "dist": "Simple bilateral distance from CEPII (km).",
    "distw": "Population-weighted bilateral distance from CEPII (km).",
    "distcap": "Distance between capital cities from CEPII (km).",
    "distwces": "Weighted distance based on city economic sizes from CEPII (km).",
    "ln_dist": "Natural log of distw.",
    "contig": "Indicator =1 if countries share a border.",
    "comlang_off": "Indicator =1 if countries share an official language.",
    "rta": "Indicator =1 if a regional trade agreement / FTA is in force.",
    "rta_coverage": "Coverage measure for the regional trade agreement.",
    "rta_type": "Type indicator for the regional trade agreement.",
    "comlang_ethno": "Indicator =1 if countries share an ethnic language.",
    "comcol": "Indicator =1 if countries had a colonial relationship.",
    "col45": "Indicator =1 if colonial relationship after 1945.",
    "comleg_pretrans": "Indicator =1 if common legal origin before transition episodes.",
    "comleg_posttrans": "Indicator =1 if common legal origin after transition episodes.",
    "sibling": "Indicator =1 if both countries share a historical parent state relationship.",
    "col_dep": "Indicator =1 if one country is/was a colonial dependency of the other.",
    "gdp_o": "Exporter GDP (current USD, CEPII source fields).",
    "gdp_d": "Importer GDP (current USD, CEPII source fields).",
    "pop_o": "Exporter population.",
    "pop_d": "Importer population.",
    "gdpcap_o": "Exporter GDP per capita.",
    "gdpcap_d": "Importer GDP per capita.",
    "ln_gdp_o": "Natural log of exporter GDP.",
    "ln_gdp_d": "Natural log of importer GDP.",
    "ln_pop_o": "Natural log of exporter population.",
    "ln_pop_d": "Natural log of importer population.",
    "ln_gdpcap_o": "Natural log of exporter GDP per capita.",
    "ln_gdpcap_d": "Natural log of importer GDP per capita.",
    "gatt_o": "Indicator =1 if exporter is GATT member.",
    "gatt_d": "Indicator =1 if importer is GATT member.",
    "wto_o": "Indicator =1 if exporter is WTO member.",
    "wto_d": "Indicator =1 if importer is WTO member.",
    "eu_o": "Indicator =1 if exporter is EU member.",
    "eu_d": "Indicator =1 if importer is EU member.",
}


def _safe_log(series: pd.Series) -> pd.Series:
    return np.where(series > 0, np.log(series), np.nan)


def load_trade_for_year(trade_file: Path, year: int, chunksize: int) -> pd.DataFrame:
    series_agg: pd.Series | None = None
    reader = pd.read_stata(
        trade_file,
        columns=["year", "exporter", "importer", "value_final"],
        chunksize=chunksize,
        convert_categoricals=False,
    )

    for chunk in reader:
        chunk = chunk.loc[chunk["year"] == year, ["exporter", "importer", "value_final"]]
        chunk = chunk.dropna(subset=["exporter", "importer", "value_final"])
        grouped = chunk.groupby(["exporter", "importer"])["value_final"].sum()
        if series_agg is None:
            series_agg = grouped
        else:
            series_agg = series_agg.add(grouped, fill_value=0.0)

    if series_agg is None:
        raise RuntimeError(f"No trade rows found for year={year} in {trade_file}.")

    trade = series_agg.reset_index()
    trade.columns = ["iso3_o", "iso3_d", "trade_value"]
    trade["iso3_o"] = trade["iso3_o"].astype(str)
    trade["iso3_d"] = trade["iso3_d"].astype(str)
    trade["trade_value"] = trade["trade_value"].astype(float)
    return trade


def load_gravity_for_year(
    gravity_file: Path,
    year: int,
    chunksize: int,
    gravity_columns: Iterable[str],
) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    reader = pd.read_stata(
        gravity_file,
        columns=list(gravity_columns),
        chunksize=chunksize,
        convert_categoricals=False,
    )
    for chunk in reader:
        subset = chunk.loc[chunk["year"] == year, [c for c in gravity_columns if c != "year"]]
        if not subset.empty:
            parts.append(subset)

    if not parts:
        raise RuntimeError(f"No CEPII gravity rows found for year={year} in {gravity_file}.")

    gravity = pd.concat(parts, ignore_index=True)
    gravity = gravity.drop_duplicates(subset=["iso3_o", "iso3_d"], keep="first")
    gravity["iso3_o"] = gravity["iso3_o"].astype(str)
    gravity["iso3_d"] = gravity["iso3_d"].astype(str)
    return gravity


def prepare_student_dataset(trade: pd.DataFrame, gravity: pd.DataFrame, year: int) -> pd.DataFrame:
    data = gravity.merge(trade, on=["iso3_o", "iso3_d"], how="left")
    data["trade_value"] = data["trade_value"].fillna(0.0)
    data = data.loc[data["iso3_o"] != data["iso3_d"]].copy()

    for col in NUMERIC_COLUMNS:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    required_now = [c for c in BASE_REQUIRED_COLUMNS if c in data.columns]
    data = data.dropna(subset=required_now)
    data = data.loc[data["distw"] > 0].copy()

    data["ln_dist"] = _safe_log(data["distw"])
    if "gdp_o" in data.columns:
        data["ln_gdp_o"] = _safe_log(data["gdp_o"])
    if "gdp_d" in data.columns:
        data["ln_gdp_d"] = _safe_log(data["gdp_d"])
    if "pop_o" in data.columns:
        data["ln_pop_o"] = _safe_log(data["pop_o"])
    if "pop_d" in data.columns:
        data["ln_pop_d"] = _safe_log(data["pop_d"])
    if "gdpcap_o" in data.columns:
        data["ln_gdpcap_o"] = _safe_log(data["gdpcap_o"])
    if "gdpcap_d" in data.columns:
        data["ln_gdpcap_d"] = _safe_log(data["gdpcap_d"])

    data = data.replace([np.inf, -np.inf], np.nan)
    data["pair_cluster"] = data["iso3_o"] + "_" + data["iso3_d"]
    data["year"] = year

    column_order = [
        "year",
        "iso3_o",
        "iso3_d",
        "pair_cluster",
        "trade_value",
        "dist",
        "distw",
        "distcap",
        "distwces",
        "ln_dist",
        "contig",
        "comlang_off",
        "rta",
        "rta_coverage",
        "rta_type",
        "comlang_ethno",
        "comcol",
        "col45",
        "comleg_pretrans",
        "comleg_posttrans",
        "sibling",
        "col_dep",
        "gdp_o",
        "gdp_d",
        "ln_gdp_o",
        "ln_gdp_d",
        "pop_o",
        "pop_d",
        "ln_pop_o",
        "ln_pop_d",
        "gdpcap_o",
        "gdpcap_d",
        "ln_gdpcap_o",
        "ln_gdpcap_d",
        "gatt_o",
        "gatt_d",
        "wto_o",
        "wto_d",
        "eu_o",
        "eu_d",
    ]
    existing_order = [col for col in column_order if col in data.columns]
    data = data[existing_order].sort_values(["iso3_o", "iso3_d"]).reset_index(drop=True)
    return data


def infer_role(column: str) -> str:
    if column in {"iso3_o", "iso3_d", "pair_cluster"}:
        return "identifier"
    if column == "trade_value":
        return "dependent_variable"
    if column in {"year"}:
        return "metadata"
    if column in {
        "dist",
        "distw",
        "distcap",
        "distwces",
        "ln_dist",
        "contig",
        "comlang_off",
        "rta",
        "rta_coverage",
        "rta_type",
        "comlang_ethno",
        "comcol",
        "col45",
        "comleg_pretrans",
        "comleg_posttrans",
        "sibling",
        "col_dep",
    }:
        return "bilateral_covariate"
    if column.endswith("_o"):
        return "exporter_covariate"
    if column.endswith("_d"):
        return "importer_covariate"
    return "other"


def build_codebook(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in data.columns:
        rows.append(
            {
                "column": col,
                "role": infer_role(col),
                "description": DESCRIPTION.get(col, ""),
            }
        )
    return pd.DataFrame(rows)


def write_codebook_markdown(codebook: pd.DataFrame, markdown_path: Path) -> None:
    lines = [
        "# Gravity Student Dataset Codebook",
        "",
        "| column | role | description |",
        "|---|---|---|",
    ]
    for _, row in codebook.iterrows():
        desc = str(row["description"]).replace("|", "\\|")
        lines.append(f"| {row['column']} | {row['role']} | {desc} |")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare student-ready merged gravity dataset.")
    parser.add_argument("--trade-file", type=Path, default=DEFAULT_TRADE_FILE)
    parser.add_argument("--gravity-file", type=Path, default=DEFAULT_GRAVITY_FILE)
    parser.add_argument("--year", type=int, default=2019)
    parser.add_argument("--chunksize", type=int, default=1_000_000)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--no-csv-backup",
        action="store_true",
        help="Skip writing CSV backup and only write parquet/codebook outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading trade data from: {args.trade_file}")
    trade = load_trade_for_year(args.trade_file, year=args.year, chunksize=args.chunksize)
    print(f"Trade pairs (positive in source): {trade.shape[0]:,}")

    print(f"Loading gravity covariates from: {args.gravity_file}")
    gravity = load_gravity_for_year(
        args.gravity_file,
        year=args.year,
        chunksize=args.chunksize,
        gravity_columns=STUDENT_GRAVITY_COLUMNS,
    )
    print(f"Gravity pairs: {gravity.shape[0]:,}")

    data = prepare_student_dataset(trade, gravity, year=args.year)
    print(f"Final student dataset rows: {data.shape[0]:,}")

    parquet_path = args.output_dir / f"gravity_{args.year}_student.parquet"
    csv_path = args.output_dir / f"gravity_{args.year}_student.csv"
    codebook_csv_path = args.output_dir / f"gravity_{args.year}_student_codebook.csv"
    codebook_md_path = args.output_dir / f"gravity_{args.year}_student_codebook.md"
    metadata_path = args.output_dir / f"gravity_{args.year}_student_metadata.json"

    parquet_error = None
    try:
        data.to_parquet(parquet_path, index=False)
        print(f"Wrote parquet: {parquet_path}")
    except Exception as exc:  # noqa: BLE001
        parquet_error = str(exc)
        print("WARNING: Could not write parquet (install pyarrow or fastparquet to enable parquet output).")
        print(f"         Error: {exc}")

    if not args.no_csv_backup:
        data.to_csv(csv_path, index=False)
        print(f"Wrote CSV backup: {csv_path}")

    codebook = build_codebook(data)
    codebook.to_csv(codebook_csv_path, index=False)
    write_codebook_markdown(codebook, codebook_md_path)
    print(f"Wrote codebook CSV: {codebook_csv_path}")
    print(f"Wrote codebook MD:  {codebook_md_path}")

    metadata = {
        "year": args.year,
        "rows": int(data.shape[0]),
        "columns": list(data.columns),
        "positive_trade_rows": int((data["trade_value"] > 0).sum()),
        "zero_trade_rows": int((data["trade_value"] == 0).sum()),
        "parquet_written": parquet_error is None,
        "parquet_error": parquet_error,
        "csv_written": not args.no_csv_backup,
        "trade_file": str(args.trade_file),
        "gravity_file": str(args.gravity_file),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote metadata JSON: {metadata_path}")


if __name__ == "__main__":
    main()
