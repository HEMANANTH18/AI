# Dataset Profile: Government Welfare Schemes (schemes.csv)

## 1. Overview and Source Context
The primary dataset for **BenefitBridge AI** is stored in `schemes.csv`. This dataset is derived from India's official citizen welfare portal (**myScheme.gov.in**) and represents a comprehensive registry of Central, State, and Union Territory welfare programs across India.

- **File Path**: `schemes.csv`
- **File Size**: 19,535,968 bytes (~18.63 MB)
- **Total Rows**: 4,670 scheme records (plus 1 header row)
- **Total Columns**: 27
- **Unique Primary Keys (`slug`)**: 4,670 (100% unique, zero nulls)
- **Character Encoding**: UTF-8 containing Unicode characters (e.g., Indian Rupee `₹` U+20B9, right single quotation `’` U+2019) and standard HTML entities (`&amp;`, `&quot;`).

---

## 2. Actual Dataset Schema & Data Types

| # | Column Name | Non-Null Count | Missing Values | Inferred Type | Description & Example |
|---|-------------|----------------|----------------|---------------|-----------------------|
| 1 | `slug` | 4,670 | 0 | String (Unique ID) | Unique URL slug identifier, e.g. `108easuk`, `pm-kisan` |
| 2 | `scheme_name` | 4,670 | 0 | String | Full official scheme title |
| 3 | `short_title` | 4,670 | 0 | String | Abbreviation/short code, e.g. `108EASUK`, `PM-KISAN` |
| 4 | `level` | 4,670 | 0 | String | Jurisdictional level: `State/ UT` (3,224), `State` (797), `Central` (649) |
| 5 | `state` | 4,021 | 649 | String / Null | Applicable State/UT. Note: Exactly 649 Central schemes have `null` state (applicable pan-India) |
| 6 | `ministry` | 649 | 4,021 | String / Null | Central Ministry (populated primarily for Central schemes) |
| 7 | `department` | 4,422 | 248 | String / Null | Implementing government department |
| 8 | `beneficiary_type` | 4,625 | 45 | String / Null | e.g. `Individual`, `Group`, `Enterprise` |
| 9 | `target_beneficiaries`| 4,614 | 56 | String / Null | Target audience description |
| 10 | `benefit_type` | 4,670 | 0 | String | `Cash` (3,240), `In Kind` (781), `Composite` (649) |
| 11 | `categories` | 4,670 | 0 | String | Primary welfare category, e.g. `Education & Learning`, `Agriculture,Rural & Environment` |
| 12 | `sub_categories` | 4,234 | 436 | String / Null | Specific focus area, e.g. `Emergency medical assistance`, `Scholarship` |
| 13 | `tags` | 4,670 | 0 | String | Semicolon-separated thematic keywords |
| 14 | `brief_description` | 4,670 | 0 | String | One or two sentence summary of the scheme |
| 15 | `detailed_description`| 4,670 | 0 | String | In-depth operational and background details |
| 16 | `benefits` | 4,407 | 263 | String / Null | Bullet-separated or pipe-separated benefit items, subsidies, cash amounts |
| 17 | `eligibility` | 4,670 | 0 | String | Semicolon-separated eligibility criteria (age, residency, income, caste, etc.) |
| 18 | `exclusions` | 654 | 4,016 | String / Null | Ineligibility rules and disqualification criteria |
| 19 | `application_mode` | 4,670 | 0 | String | `Offline` (2,294), `Online` (1,858), `Online; Offline` (225), CSC modes |
| 20 | `application_process` | 4,407 | 263 | String / Null | Step-by-step procedural guidelines for citizen application |
| 21 | `documents_required` | 4,256 | 414 | String / Null | Semicolon-separated list of mandatory documentation |
| 22 | `references` | 4,665 | 5 | String / Null | Official government orders, guidelines, and departmental URLs |
| 23 | `scheme_open_date` | 1,050 | 3,620 | String / Null | Scheme launch or window opening date |
| 24 | `scheme_close_date` | 56 | 4,614 | String / Null | Scheme expiration or deadline date |
| 25 | `dbt_scheme` | 4,670 | 0 | Boolean | Direct Benefit Transfer indicator (`True`/`False`) |
| 26 | `faq_count` | 4,670 | 0 | Integer | Number of frequently asked questions available |
| 27 | `source_url` | 4,670 | 0 | String | Direct official portal link: `https://www.myscheme.gov.in/schemes/<slug>` |

---

## 3. Key Observations & Findings

1. **Primary Key & Identity**:
   - `slug` serves as the authoritative unique record identifier across all 4,670 rows.
   - `scheme_name` has only 1 duplicate name (`free-ug-students-only` vs `freeship-ug-students-only`), which represent distinct targeted schemes with separate slugs.
   
2. **Geographic Coverage**:
   - 649 Central schemes apply nationwide (pan-India).
   - 4,021 schemes belong to specific States or Union Territories. The top states represented are Gujarat (641), Uttarakhand (446), Madhya Pradesh (288), Puducherry (270), Goa (269), Haryana (247), Tamil Nadu (234), Rajasthan (157), and Bihar (113).

3. **Eligibility Condition Richness**:
   - All 4,670 rows (100%) have structured or semi-structured `eligibility` text.
   - Age criteria are explicitly present in 2,527 schemes (54.1%).
   - Income criteria are explicitly present in 1,726 schemes (37.0%).
   - Gender/women/widow criteria are mentioned in 1,868 schemes (40.0%).
   - Social caste/category (SC/ST/OBC/Minority/General) is mentioned in 4,314 schemes (92.4%).

4. **Benefits & Guidance Information**:
   - 94.4% of schemes have explicit `benefits` descriptions.
   - 94.4% of schemes describe `application_process`.
   - 91.1% of schemes enumerate `documents_required`.
   - 100% of schemes have direct official portal links in `source_url`.
   - 99.9% of schemes list official reference links or Government Orders in `references`.

5. **Data Quality & Hygiene Considerations**:
   - **HTML Entities**: Raw text contains unescaped HTML entities such as `&amp;` (4,660 occurrences) and `&quot;` (4,763 occurrences). A deterministic cleaning step with `html.unescape` is required.
   - **Unicode & Punctuation**: Contains Indian Rupee signs (`₹`), right single quotes (`’`), em-dashes, and bullet markers (`-`, `|`, `;`). Handled via UTF-8 normalization without stripping meaningful currency or delimiters.
   - **Missing Exclusions**: `exclusions` is null in 86.0% of rows; absence of an exclusion must never be treated as an exclusion rule failure.
   - **Central Scheme State Nulls**: In queries where a user resides in "Tamil Nadu", all Tamil Nadu state schemes AND all Central schemes (state is null / "All India") are candidates.

---

## 4. Canonical Internal Scheme Model Mapping

| Canonical Field | Source Column(s) | Processing / Transformation |
|-----------------|------------------|-----------------------------|
| `id` | `slug` | Lowercase trimmed string (canonical primary key) |
| `name` | `scheme_name` | HTML unescaped, whitespace normalized |
| `short_title` | `short_title` | Fallback to initials if empty |
| `level` | `level` | Normalized: `Central`, `State`, or `State/ UT` |
| `state` | `state`, `level` | If `level == 'Central'` and `state` is null, maps to `"All India"` |
| `ministry` | `ministry` | Unescaped string or `None` |
| `department` | `department` | Unescaped string or `None` |
| `categories` | `categories` | Semicolon-split list of category strings |
| `sub_categories`| `sub_categories`| Semicolon-split list or empty list |
| `tags` | `tags` | Semicolon-split list of trimmed keyword tags |
| `brief_description` | `brief_description` | HTML unescaped clean string |
| `detailed_description` | `detailed_description` | HTML unescaped clean string |
| `benefits` | `benefits` | Split on `|` or `;` into clean benefit bullet points |
| `eligibility_text` | `eligibility` | Semicolon-split into distinct condition clauses |
| `parsed_criteria` | Derived via regex/logic | Structured `{min_age, max_age, max_income, states, genders, categories, occupations}` |
| `documents` | `documents_required` | Semicolon-split into distinct document requirements |
| `application_mode` | `application_mode` | Normalized: `Online`, `Offline`, `CSC`, `Hybrid` |
| `application_steps` | `application_process` | Bullet/number parsed sequential steps |
| `official_url` | `source_url` | Validated HTTPS URL to official portal |
| `references` | `references` | Semicolon-separated verified government URLs |
| `dbt_scheme` | `dbt_scheme` | Boolean |

This schema forms the factual foundation for deterministic filtering, SentenceTransformers vector indexing, and grounded multi-agent generation.
