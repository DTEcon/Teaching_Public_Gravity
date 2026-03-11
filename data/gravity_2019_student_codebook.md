# Gravity Student Dataset Codebook

| column | role | description |
|---|---|---|
| year | metadata | Cross-section year used for the student dataset. |
| iso3_o | identifier | Exporter ISO3 code (origin country i). |
| iso3_d | identifier | Importer ISO3 code (destination country j). |
| pair_cluster | identifier | Country-pair identifier (i_j) for clustered standard errors. |
| trade_value | dependent_variable | Total bilateral trade flow X_ij in USD levels (Atlas aggregated to pair-year). |
| dist | bilateral_covariate | Simple bilateral distance from CEPII (km). |
| distw | bilateral_covariate | Population-weighted bilateral distance from CEPII (km). |
| ln_dist | bilateral_covariate | Natural log of distw. |
| contig | bilateral_covariate | Indicator =1 if countries share a border. |
| comlang_off | bilateral_covariate | Indicator =1 if countries share an official language. |
| rta | bilateral_covariate | Indicator =1 if a regional trade agreement / FTA is in force. |
| comcol | bilateral_covariate | Indicator =1 if countries had a colonial relationship. |
| comleg_posttrans | bilateral_covariate | Indicator =1 if common legal origin after transition episodes. |
| gdp_o | exporter_covariate | Exporter GDP (current USD, CEPII source fields). |
| gdp_d | importer_covariate | Importer GDP (current USD, CEPII source fields). |
| ln_gdp_o | exporter_covariate | Natural log of exporter GDP. |
| ln_gdp_d | importer_covariate | Natural log of importer GDP. |
| pop_o | exporter_covariate | Exporter population. |
| pop_d | importer_covariate | Importer population. |
| ln_pop_o | exporter_covariate | Natural log of exporter population. |
| ln_pop_d | importer_covariate | Natural log of importer population. |
| gdpcap_o | exporter_covariate | Exporter GDP per capita. |
| gdpcap_d | importer_covariate | Importer GDP per capita. |
| ln_gdpcap_o | exporter_covariate | Natural log of exporter GDP per capita. |
| ln_gdpcap_d | importer_covariate | Natural log of importer GDP per capita. |
| wto_o | exporter_covariate | Indicator =1 if exporter is WTO member. |
| wto_d | importer_covariate | Indicator =1 if importer is WTO member. |
| eu_o | exporter_covariate | Indicator =1 if exporter is EU member. |
| eu_d | importer_covariate | Indicator =1 if importer is EU member. |
