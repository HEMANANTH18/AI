from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

class CitizenProfile(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120, description="Citizen age in years")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual income in INR")
    income_type: Optional[Literal["individual", "household"]] = Field("individual", description="Income type (individual or household)")
    state: Optional[str] = Field(None, description="State of residence (e.g. Tamil Nadu, Gujarat, etc.)")
    district: Optional[str] = Field(None, description="District of residence")
    occupation: Optional[str] = Field(None, description="Occupation (e.g., farmer, student, construction_worker, artisan, self_employed, unemployed, salaried)")
    gender: Optional[str] = Field(None, description="Gender (e.g., Male, Female, Transgender)")
    social_category: Optional[str] = Field(None, description="Social category / Caste group (e.g., General, OBC, SC, ST, Minority)")
    education: Optional[str] = Field(None, description="Education level (e.g., primary, secondary, higher_secondary, graduate, post_graduate)")
    disability: Optional[bool] = Field(None, description="Whether person has disability / physically challenged")
    marital_status: Optional[str] = Field(None, description="Marital status (e.g., single, married, widow, divorced)")
    query_text: Optional[str] = Field(None, description="Citizen's stated primary objective or welfare need")

class ProfileExtractionResult(BaseModel):
    profile: CitizenProfile
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)
    clarification_question: Optional[str] = None
    suggested_options: Optional[List[str]] = None
    profile_complete: bool = False
    next_recommended_field: Optional[str] = None
    acknowledgement_text: Optional[str] = None

class ConversationTurn(BaseModel):
    turn_id: str
    user_message: str
    agent_message: str
    timestamp: str

class ConversationSession(BaseModel):
    session_id: str
    profile: CitizenProfile = Field(default_factory=CitizenProfile)
    history: List[ConversationTurn] = Field(default_factory=list)
    language: str = "en"
    created_at: str
    updated_at: str
