import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.scheme import Scheme, ParsedCriteria
from app.data.schema_mapping import clean_text, split_items, extract_criteria_from_text

class SchemeDataLoader:
    _instance: Optional["SchemeDataLoader"] = None
    _schemes: List[Scheme] = []
    _schemes_by_id: Dict[str, Scheme] = {}
    _is_loaded: bool = False

    @classmethod
    def get_instance(cls) -> "SchemeDataLoader":
        if cls._instance is None:
            cls._instance = SchemeDataLoader()
        return cls._instance

    def load_schemes(self, force_reload: bool = False) -> List[Scheme]:
        """Loads and parses schemes from CSV into canonical Scheme instances."""
        if self._is_loaded and not force_reload:
            return self._schemes

        csv_path = settings.get_valid_csv_path()
        logger.info(f"Loading schemes dataset from: {csv_path}")

        try:
            df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
        except Exception as e:
            logger.error(f"Error reading CSV file with utf-8: {e}. Retrying with latin1 fallback.")
            df = pd.read_csv(csv_path, encoding="latin1", on_bad_lines="skip")

        logger.info(f"CSV read successfully: {len(df)} rows detected.")

        schemes: List[Scheme] = []
        schemes_by_id: Dict[str, Scheme] = {}

        for _, row in df.iterrows():
            slug = str(row.get("slug", "")).strip().lower()
            if not slug or slug == "nan":
                continue

            name = clean_text(str(row.get("scheme_name", "")))
            short_title = clean_text(str(row.get("short_title", "")))
            level = clean_text(str(row.get("level", "Central")))
            raw_state = row.get("state")
            state_val = clean_text(str(raw_state)) if pd.notna(raw_state) else None
            if level.lower() == "central" and not state_val:
                state_val = "All India"

            ministry = clean_text(str(row.get("ministry", ""))) if pd.notna(row.get("ministry")) else None
            department = clean_text(str(row.get("department", ""))) if pd.notna(row.get("department")) else None
            beneficiary_type = clean_text(str(row.get("beneficiary_type", ""))) if pd.notna(row.get("beneficiary_type")) else None
            target_beneficiaries = clean_text(str(row.get("target_beneficiaries", ""))) if pd.notna(row.get("target_beneficiaries")) else None
            benefit_type = clean_text(str(row.get("benefit_type", "Composite")))
            
            categories = split_items(str(row.get("categories", "")))
            sub_categories = split_items(str(row.get("sub_categories", "")))
            tags = split_items(str(row.get("tags", "")))
            
            brief_desc = clean_text(str(row.get("brief_description", "")))
            detailed_desc = clean_text(str(row.get("detailed_description", "")))
            benefits = split_items(str(row.get("benefits", "")), delimiters="|;\n")
            eligibility_text = clean_text(str(row.get("eligibility", "")))
            exclusions = clean_text(str(row.get("exclusions", ""))) if pd.notna(row.get("exclusions")) else None
            
            app_mode = clean_text(str(row.get("application_mode", "Offline")))
            app_steps = split_items(str(row.get("application_process", "")), delimiters="|;\n")
            docs_required = split_items(str(row.get("documents_required", "")), delimiters=";\n")
            refs = split_items(str(row.get("references", "")), delimiters=";\n")
            
            dbt_val = str(row.get("dbt_scheme", "False")).strip().lower() in ("true", "1", "yes")
            source_url = clean_text(str(row.get("source_url", f"https://www.myscheme.gov.in/schemes/{slug}")))

            # Deterministic criteria parsing
            parsed_criteria = extract_criteria_from_text(eligibility_text, level, state_val)

            # Build semantic search text
            search_parts = [
                f"Scheme Name: {name}",
                f"Level: {level}",
                f"State: {state_val or 'All India'}",
                f"Categories: {', '.join(categories)}",
                f"Target: {target_beneficiaries or beneficiary_type or ''}",
                f"Brief: {brief_desc}",
                f"Eligibility: {eligibility_text}",
                f"Benefits: {' '.join(benefits[:3])}",
                f"Tags: {', '.join(tags[:5])}"
            ]
            searchable_text = " | ".join(p for p in search_parts if p)

            scheme_obj = Scheme(
                id=slug,
                name=name,
                short_title=short_title,
                level=level,
                state=state_val,
                ministry=ministry,
                department=department,
                beneficiary_type=beneficiary_type,
                target_beneficiaries=target_beneficiaries,
                benefit_type=benefit_type,
                categories=categories,
                sub_categories=sub_categories,
                tags=tags,
                brief_description=brief_desc,
                detailed_description=detailed_desc,
                benefits=benefits,
                eligibility_text=eligibility_text,
                exclusions=exclusions,
                application_mode=app_mode,
                application_steps=app_steps,
                documents_required=docs_required,
                references=refs,
                dbt_scheme=dbt_val,
                source_url=source_url,
                parsed_criteria=parsed_criteria,
                searchable_text=searchable_text,
            )

            schemes.append(scheme_obj)
            schemes_by_id[slug] = scheme_obj

        self._schemes = schemes
        self._schemes_by_id = schemes_by_id
        self._is_loaded = True
        logger.info(f"Successfully loaded and structured {len(schemes)} welfare schemes.")
        return self._schemes

    def get_all(self) -> List[Scheme]:
        if not self._is_loaded:
            return self.load_schemes()
        return self._schemes

    def get_by_id(self, scheme_id: str) -> Optional[Scheme]:
        if not self._is_loaded:
            self.load_schemes()
        return self._schemes_by_id.get(scheme_id.strip().lower())

loader = SchemeDataLoader.get_instance()
