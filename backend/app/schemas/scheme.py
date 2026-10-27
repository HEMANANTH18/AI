from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ParsedCriteria(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    max_income: Optional[float] = None
    allowed_states: List[str] = Field(default_factory=list)
    allowed_genders: List[str] = Field(default_factory=list)
    allowed_categories: List[str] = Field(default_factory=list)
    target_occupations: List[str] = Field(default_factory=list)
    requires_disability: Optional[bool] = None
    requires_widow: Optional[bool] = None
    is_central: bool = False

class Scheme(BaseModel):
    id: str = Field(..., description="Unique scheme slug identifier")
    name: str = Field(..., description="Official scheme name")
    short_title: str = Field("", description="Short title or acronym")
    level: str = Field(..., description="Central, State, or State/ UT")
    state: Optional[str] = Field(None, description="Applicable state, or All India for Central")
    ministry: Optional[str] = None
    department: Optional[str] = None
    beneficiary_type: Optional[str] = None
    target_beneficiaries: Optional[str] = None
    benefit_type: str = Field("Composite", description="Cash, In Kind, or Composite")
    categories: List[str] = Field(default_factory=list)
    sub_categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    brief_description: str = Field("")
    detailed_description: str = Field("")
    benefits: List[str] = Field(default_factory=list)
    eligibility_text: str = Field("")
    exclusions: Optional[str] = None
    application_mode: str = Field("Offline")
    application_steps: List[str] = Field(default_factory=list)
    documents_required: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    dbt_scheme: bool = False
    source_url: str = Field(...)
    parsed_criteria: ParsedCriteria = Field(default_factory=ParsedCriteria)
    searchable_text: str = Field("")
