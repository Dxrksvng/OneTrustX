# Data Quality Report

2026-09-12T23:46:29.921985+00:00

Source observations, not airport deployment claims. Missing percentages cover business fields; provenance fields excluded. Duplicate rates are within each source extract; revisions across CAAT extracts are retained with lineage and resolved in API aggregates.

| Dataset | Records | Period | Geography | Missing % | Duplicate % |
|---|---:|---|---|---:|---:|
| airport_master | 145 | None — None | GLOBAL | 27.441 | 0.0 |
| bts_flights | 504,884 | 2025-02-01 — 2025-02-28 | US DOMESTIC | 17.816 | 0.0 |
| caat_daily-2025-04-23 | 342 | 2024-04-01 — 2025-04-23 | TH | 2.522 | 0.0 |
| caat_history-12 | 234 | 2023-11-01 — 2024-11-23 | TH | 0.0 | 0.0 |
| caat_history-15 | 234 | 2023-10-01 — 2024-10-18 | TH | 0.0 | 0.0 |
| caat_history-18 | 234 | 2023-09-01 — 2024-09-17 | TH | 0.0 | 0.0 |
| caat_history-3 | 342 | 2024-01-01 — 2025-02-12 | TH | 0.0 | 0.0 |
| caat_history-6 | 342 | 2024-01-01 — 2025-02-04 | TH | 0.0 | 0.0 |
| caat_history-9 | 234 | 2024-01-01 — 2025-01-02 | TH | 0.0 | 0.0 |
| cbp_JFK_2025-01 | 2,427 | 2025-01-01 — 2025-01-31 | US / JFK | 0.0 | 0.0 |
| cbp_JFK_2025-02 | 2,151 | 2025-02-01 — 2025-02-28 | US / JFK | 0.0 | 0.0 |
| cbp_JFK_2025-03 | 2,380 | 2025-03-01 — 2025-03-31 | US / JFK | 0.0 | 0.0 |
| cbp_LAX_2025-01 | 883 | 2025-01-01 — 2025-01-31 | US / LAX | 0.0 | 0.0 |
| cbp_LAX_2025-02 | 794 | 2025-02-01 — 2025-02-28 | US / LAX | 0.0 | 0.0 |
| cbp_LAX_2025-03 | 872 | 2025-03-01 — 2025-03-31 | US / LAX | 0.0 | 0.0 |
| cbp_SFO_2025-01 | 925 | 2025-01-01 — 2025-01-31 | US / SFO | 0.0 | 0.0 |
| cbp_SFO_2025-02 | 825 | 2025-02-01 — 2025-02-28 | US / SFO | 0.0 | 0.0 |
| cbp_SFO_2025-03 | 929 | 2025-03-01 — 2025-03-31 | US / SFO | 0.0 | 0.0 |
| uk_caa_Table_01_Size_of_UK_Airports | 50 | 2025 — 2025 | UK | 0.0 | 0.0 |
| uk_caa_Table_03_1_Aircraft_Movements | 57 | 2025 — 2025 | UK | 0.0 | 0.0 |
| uk_caa_Table_09_Terminal_and_Transit_Passengers | 51 | 2025 — 2025 | UK | 3.309 | 0.0 |
| weather_hourly | 8,760 | 2025-01-01T00:00 — 2025-12-31T23:00 | TH / BKK | 0.0 | 0.0 |

## Source lineage

- airport_master: https://davidmegginson.github.io/ourairports-data/airports.csv · retrieved 2026-09-12T22:35:50.547774+00:00 · SHA256 `8c9ccbdf132213042cb7b4ed64d3383ea29541972584c2878a4e17fd111843c2`

- bts_flights: https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_2.zip · retrieved 2026-09-12T22:36:05.313117+00:00 · SHA256 `12dc8dbdb3c8b3c20d4c00a8b188196ae202f781a8760871ae502a9c733d0ecd`

- caat_daily-2025-04-23: https://www.caat.or.th/wp-content/uploads/2025/07/Air-Transport-Daily-23-Apr-25.xlsx · retrieved 2026-09-12T23:30:08.166430+00:00 · SHA256 `f490058abcd9308828a7c2058c126bfb14e0029e06fef12a3647f854baae9da8`

- caat_history-12: https://www.caat.or.th/wp-content/uploads/2024/11/Air-Transport-Daily-23-Nov-24.xlsx · retrieved 2026-09-12T23:44:23.780389+00:00 · SHA256 `d98ac7ec1b19af1518ad84063a77ba2ba41c2596f72a9b2399563b9d9ce718fc`

- caat_history-15: https://www.caat.or.th/wp-content/uploads/2024/10/Air-Transport-Daily-18-Oct-24.xlsx · retrieved 2026-09-12T23:44:27.594562+00:00 · SHA256 `19bfa65785d63e1f84c2a620048490fec5f448fd6a51e43e9e2eadb97b3516d4`

- caat_history-18: https://www.caat.or.th/wp-content/uploads/2024/09/Air-Transport-Statistics-Daily-17-Sep-24.xlsx · retrieved 2026-09-12T23:44:31.157770+00:00 · SHA256 `f634836e8712efb378f0af76290b1144d693ebe09b694f8dd6784c585207054c`

- caat_history-3: https://www.caat.or.th/wp-content/uploads/2025/02/Air-Transport-Daily-12-Feb-25.xlsx · retrieved 2026-09-12T23:44:12.208132+00:00 · SHA256 `9c1baa90b46fa930fc209c28a982426623e1be7778bbe9f259a6c51344d3ebaf`

- caat_history-6: https://www.caat.or.th/wp-content/uploads/2025/02/Air-Transport-Daily-4-Feb-25.xlsx · retrieved 2026-09-12T23:44:15.799835+00:00 · SHA256 `d72da7b6dbd362a7e4845eb68e9c0e9e21eaa645aca7967349bd6c006bc86cba`

- caat_history-9: https://www.caat.or.th/wp-content/uploads/2025/01/Air-Transport-Daily-2-Jan-25.xlsx · retrieved 2026-09-12T23:44:19.849288+00:00 · SHA256 `ca5601a4c0eb4d99f8c24aa340b1cc9a8796684e3722012e984df28f71a75fab`

- cbp_JFK_2025-01: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:15.583937+00:00 · SHA256 `38bae96b4de0aba55b3a9ad65c0cb78a559efcaa14495c3a83de4f76eb41377c`

- cbp_JFK_2025-02: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:19.324237+00:00 · SHA256 `729e597a646366a6937a73a59cbc36a9cb03ef9e5861140a594714dbe54b1892`

- cbp_JFK_2025-03: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:21.622872+00:00 · SHA256 `53b8fc5fa0a6d269bba5c53c9fd75b53831991c4765db2713842e628c83ce136`

- cbp_LAX_2025-01: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:24.350091+00:00 · SHA256 `1fc85e7e911be8b00bd5f17a056bf9a5dcbc73783909b1d6f860b23ca673a35c`

- cbp_LAX_2025-02: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:26.610234+00:00 · SHA256 `e6e456e81685e94965ce45bd48f26ca3e3240f2dc04d106a3adada7b4642950e`

- cbp_LAX_2025-03: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:29.111441+00:00 · SHA256 `c759d61d29904f4f4501bbf675e7feb99cae680bf30350b7c4d77646dc4892ed`

- cbp_SFO_2025-01: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:31.044485+00:00 · SHA256 `c44f00e99aa31c2024aad4127560e8fac8e5e278bd321fdfc352756109935753`

- cbp_SFO_2025-02: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:32.909342+00:00 · SHA256 `f8c093765b539afdca9ecb0c2590155bfc30d07563d8c6d1e7584253af9e215a`

- cbp_SFO_2025-03: https://awt.cbp.gov/api/waitTime · retrieved 2026-09-12T23:30:34.873413+00:00 · SHA256 `9851caa7e6250f8455c5e0f500929303f3e575c9130b7d16693bc2bf9ebcf3af`

- uk_caa_Table_01_Size_of_UK_Airports: https://www.caa.co.uk/Documents/Download/24007/87fb7670-4e10-4aeb-942d-509238aa25a1/17532 · retrieved 2026-09-12T23:30:08.781932+00:00 · SHA256 `9653cc5313e72deac7502570a5f89f76e7b24365a4427fd67b1c2d1f9d05042b`

- uk_caa_Table_03_1_Aircraft_Movements: https://www.caa.co.uk/Documents/Download/24007/87fb7670-4e10-4aeb-942d-509238aa25a1/17535 · retrieved 2026-09-12T23:30:11.829785+00:00 · SHA256 `bb40d29bdd34c790c39cc96e580ae1e586eb4a5fd80d4c67688c74755f601388`

- uk_caa_Table_09_Terminal_and_Transit_Passengers: https://www.caa.co.uk/Documents/Download/24007/87fb7670-4e10-4aeb-942d-509238aa25a1/17551 · retrieved 2026-09-12T23:30:13.656581+00:00 · SHA256 `0b96d31d7b51ecf7f1159516c3984aa6b91f99e66603a86b2d8b6333689d417e`

- weather_hourly: https://archive-api.open-meteo.com/v1/archive?latitude=13.6811&longitude=100.747002&start_date=2025-01-01&end_date=2025-12-31&hourly=temperature_2m%2Crelative_humidity_2m%2Cprecipitation%2Crain%2Cweather_code%2Cpressure_msl%2Ccloud_cover%2Cwind_speed_10m%2Cwind_direction_10m%2Cwind_gusts_10m&timezone=Asia%2FBangkok · retrieved 2026-09-12T22:36:01.977110+00:00 · SHA256 `7ba99256649ad57430efa799e471646566b03c0740bce85fdaa671f5f0739ddd`

## Limitations
- Weather is historical model/reanalysis data from Open-Meteo, not an airport METAR sensor observation.
- CBP is US immigration; it cannot validate BKK security service rates directly.
- BTS US flights are never shown as BKK schedules.
- CAAT daily workbook values are preliminary. Missing dashes stay missing; monthly template dates are normalized to month starts.
- No production BKK checkpoint telemetry is available in this repository.
- TSA endpoint returned HTTP 403; no TSA observations are fabricated.
- CAAT current SharePoint export requires access; historic public workbooks are used instead.

## Effective coverage after resolving CAAT releases

188 distinct national daily totals; 19 national monthly totals; 3 non-missing BKK daily totals. The latest imported BKK date is 2025-04-23. Coverage has gaps and must not be described as 12 months of BKK daily telemetry.

AOT: reports were explored but the annual PDF request returned 404; inline dashboard totals were quarantined because they did not reconcile. TSA: HTTP 403. EUROCONTROL ADRR: future research source, not connected. No substitute REAL_PUBLIC rows were created.
