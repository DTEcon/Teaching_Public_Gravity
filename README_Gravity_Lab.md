# Gravity Lab (Student Version)

This lab lets students run gravity regressions in the browser (Google Colab) with a prebuilt country-pair dataset.
This repository is intentionally restricted to gravity-lab assets only.

## Open in Colab

- Full notebook (all code visible):  
  [Open Gravity Student Lab - Full](https://colab.research.google.com/github/DTEcon/Teaching_International_Trade_PUBLIC/blob/main/gravity_student_lab_colab.ipynb)
- Minimal notebook (frontend-style; code hidden by default):  
  [Open Gravity Student Lab - Minimal](https://colab.research.google.com/github/DTEcon/Teaching_International_Trade_PUBLIC/blob/main/gravity_student_lab_colab_minimal.ipynb)

## One-click student flow

1. Open the Colab notebook link.
2. Click `Runtime` -> `Run all`.
3. Use the form cell to choose:
   - estimator (`OLS` or `PPML`),
   - one FE toggle (`include_fe`) that jointly controls exporter and importer FE,
   - covariates via checkbox groups (bilateral, exporter-only, importer-only),
   - exporter/importer country filters.
4. Read:
   - coefficient table (clustered SE by country pair),
   - model metadata (`N`, formula, sample composition),
   - FE/collinearity diagnostics.

## Control logic (important)

- `preset_spec` is the master selector.
- If `preset_spec` is not `Custom`, the notebook applies preset values for:
  - estimator,
  - `include_fe`,
  - covariate checkbox selection.
- To manually set estimator/FE/covariates yourself, choose `preset_spec = Custom`.
- Country filters use ISO3 lists:
  - `ALL` keeps all countries,
  - comma-separated values (e.g., `PER,NGA`) restrict the sample.

## Available covariates in this version

- Bilateral:
  - baseline: `ln_dist`, `contig`, `comlang_off`, `rta`
  - additional: `dist`, `distcap`, `distwces`, `rta_coverage`, `rta_type`, `comlang_ethno`, `comcol`, `col45`, `comleg_pretrans`, `comleg_posttrans`, `sibling`, `col_dep`
- Exporter-only:
  - `ln_gdp_o`, `gdp_o`, `ln_pop_o`, `pop_o`, `ln_gdpcap_o`, `gdpcap_o`, `gatt_o`, `wto_o`, `eu_o`
- Importer-only:
  - `ln_gdp_d`, `gdp_d`, `ln_pop_d`, `pop_d`, `ln_gdpcap_d`, `gdpcap_d`, `gatt_d`, `wto_d`, `eu_d`

Note: `comcur` is not available in `Gravity_V202010.dta`, so it is not offered in the notebook controls.

## Data used by the notebook

- Default dataset URL target:
  - `data/gravity_2019_student.csv`
- If URL access fails in Colab (for example private repo), the notebook prompts file upload.

## Suggested experiments

1. Run `Naive GDP gravity (no FE)` and compare with `Canonical FE (OLS)`.
2. Switch to `Custom`, add one extra bilateral covariate (for example `comleg_pretrans`), and inspect coefficient changes.
3. Toggle `include_fe` off/on with the same covariates and compare interpretation.
4. Restrict exporters/importers (for example a regional subset) and compare coefficients.

## FE interpretation guide (short)

- With `include_fe = True`, exporter and importer FE are included jointly.
- Exporter FE absorb exporter-specific determinants common across destinations.
- Importer FE absorb importer-specific determinants common across origins.
- Exporter-only covariates (`*_o`) and importer-only covariates (`*_d`) can be collinear with FE.
- Bilateral covariates (distance, border, language, RTA-related controls) remain identified with FE.

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
