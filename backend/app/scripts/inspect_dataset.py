import sys
import json
from app.data.csv_loader import loader
from app.data.data_quality import assess_data_quality

def main():
    print("=" * 60)
    print(" BenefitBridge AI — Dataset Inspection & Quality Audit")
    print("=" * 60)
    schemes = loader.load_schemes()
    print(f"Total schemes successfully loaded: {len(schemes)}")
    quality = assess_data_quality(schemes)
    print("\nQuality Summary:")
    print(json.dumps(quality, indent=2))

    print("\nSample Scheme Record:")
    sample = schemes[0]
    print(f"ID: {sample.id}")
    print(f"Name: {sample.name}")
    print(f"Level: {sample.level} | State: {sample.state}")
    print(f"Benefit Type: {sample.benefit_type}")
    print(f"Categories: {sample.categories}")
    print(f"Eligibility excerpt: {sample.eligibility_text[:120]}...")
    print(f"Parsed Min Age: {sample.parsed_criteria.min_age}, Max Age: {sample.parsed_criteria.max_age}")
    print(f"Parsed Max Income: {sample.parsed_criteria.max_income}")
    print(f"Official URL: {sample.source_url}")
    print("=" * 60)

if __name__ == "__main__":
    main()
