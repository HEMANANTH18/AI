import pytest
from app.agents.profile_collector import profile_collector_agent
from app.schemas.profile import CitizenProfile

def test_extract_age_and_income():
    msg = "Hello, I am 32 years old and my annual income is 2.5 lakh."
    res = profile_collector_agent.process_turn(msg)
    assert res.profile.age == 32
    assert res.profile.annual_income == 250000.0
    assert "age" in res.extracted_fields
    assert "annual_income" in res.extracted_fields

def test_state_synonym_normalization():
    msg = "I live in TN."
    res = profile_collector_agent.process_turn(msg)
    assert res.profile.state == "Tamil Nadu"

    msg2 = "Residing in UP, occupation is farming."
    res2 = profile_collector_agent.process_turn(msg2)
    assert res2.profile.state == "Uttar Pradesh"
    assert res2.profile.occupation == "farmer"

def test_clarification_on_missing_fields():
    msg = "I want a scholarship"
    res = profile_collector_agent.process_turn(msg)
    assert res.profile_complete is False
    assert res.clarification_question is not None
    assert "state" in res.missing_fields

def test_multi_turn_profile_accumulation():
    # Turn 1
    t1 = profile_collector_agent.process_turn("I am 24 years old from Gujarat")
    assert t1.profile.age == 24
    assert t1.profile.state == "Gujarat"
    assert t1.profile_complete is False

    # Turn 2
    t2 = profile_collector_agent.process_turn("I am a student with income 80000", current_profile=t1.profile)
    assert t2.profile.age == 24
    assert t2.profile.state == "Gujarat"
    assert t2.profile.occupation == "student"
    assert t2.profile.annual_income == 80000.0
    assert t2.profile_complete is True
