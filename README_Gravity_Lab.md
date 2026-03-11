# Gravity Lab (Student Version)

This lab lets students run gravity regressions in the browser (Google Colab) with a prebuilt country-pair dataset.
This repository is intentionally restricted to gravity-lab assets only.

## Open in Colab

- [Open Gravity Student Lab](https://colab.research.google.com/github/DTEcon/Teaching_International_Trade_PUBLIC/blob/main/gravity_student_lab_colab.ipynb)

## One-click student flow

1. Open the Colab notebook link.
2. Click `Runtime` -> `Run all`.
3. Use the form cell to choose:
   - estimator (`OLS` or `PPML`),
   - exporter/importer FE on/off,
   - covariates,
   - exporter/importer country filters.
4. Read:
   - coefficient table (clustered SE by country pair),
   - model metadata (`N`, formula, sample composition),
   - FE/collinearity diagnostics.
5. Copy the generated LaTeX block if needed.

## Data used by the notebook

- Default dataset URL target:
  - `data/gravity_2019_student.csv`
- If URL access fails in Colab (for example private repo), the notebook prompts file upload.

## Suggested experiments

1. Run `Naive GDP gravity (no FE)` and compare with `Canonical FE (OLS)`.
2. Add `comcol` or `comlang_ethno` to the canonical specification.
3. Restrict exporters/importers (for example a regional subset) and compare coefficients.

## FE interpretation guide (short)

- Exporter FE absorb exporter-specific determinants common across destinations.
- Importer FE absorb importer-specific determinants common across origins.
- Exporter-only covariates (`*_o`) become collinear when exporter FE are included.
- Importer-only covariates (`*_d`) become collinear when importer FE are included.
- Bilateral covariates (distance, border, language, RTA) remain identified with exporter/importer FE.

## Instructor: regenerate student dataset

Run:

```bash
python scripts/prepare_student_gravity_data.py --trade-file H0_2019.dta --gravity-file Gravity_V202010.dta
```

Outputs:

- `data/gravity_2019_student.csv`
- `data/gravity_2019_student_codebook.csv`
- `data/gravity_2019_student_codebook.md`
- `data/gravity_2019_student_metadata.json`

Note: parquet output is attempted automatically. If `pyarrow` / `fastparquet` is unavailable, the script still writes CSV and codebooks.
