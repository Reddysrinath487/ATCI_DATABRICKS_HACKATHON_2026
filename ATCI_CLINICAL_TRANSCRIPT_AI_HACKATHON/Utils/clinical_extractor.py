import re

def extract_clinical_fields(text):
    """
    Extract structured clinical data from raw clinical note text.
    """

    if not text:
        return {
            "patient_name": None,
            "mrn": None,
            "dob": None,
            "visit_date": None,
            "provider": None,
            "reason": None,
            "subjective": None,
            "objective": None,
            "bp_systolic": None,
            "bp_diastolic": None,
            "heart_rate": None,
            "assessment_plan": None
        }

    def extract(pattern, group=1):
        match = re.search(pattern, text, re.DOTALL)
        return match.group(group).strip() if match else None

    # ---- Basic fields ----
    result = {
        "patient_name": extract(r"PATIENT:\s*(.*?)\s*\("),
        "mrn": extract(r"MRN:\s*(\d+)"),
        "dob": extract(r"DOB:\s*([\d-]+)"),
        "visit_date": extract(r"DATE:\s*([\d-]+)"),
        "provider": extract(r"PROVIDER:\s*([^\r\n]*)"),
        "reason": extract(r"REASON:\s*(.*?)(?=\nSUBJECTIVE:)"),
        "subjective": extract(r"SUBJECTIVE:\s*(.*?)(?:\n\s*\n|OBJECTIVE:)"),
        "objective": extract(r"OBJECTIVE:\s*(.*?)(?:\n\s*\n|ASSESSMENT:|ASSESSMENT & PLAN:)")
    }

    # ---- Extract BP & HR ----
    if result["objective"]:
        bp_match = re.search(r"BP\s*(\d{2,3})/(\d{2,3})", result["objective"])
        hr_match = re.search(r"HR\s*(\d{2,3})", result["objective"])

        result["bp_systolic"] = int(bp_match.group(1)) if bp_match else None
        result["bp_diastolic"] = int(bp_match.group(2)) if bp_match else None
        result["heart_rate"] = int(hr_match.group(1)) if hr_match else None
    else:
        result["bp_systolic"] = None
        result["bp_diastolic"] = None
        result["heart_rate"] = None

    # ---- Assessment & Plan ----
    plan_match = re.search(r"ASSESSMENT\s*&\s*PLAN:\s*(.*?)(?=\nKEY:)", text, re.DOTALL)
    if plan_match:
        result["assessment_plan"] = re.findall(
            r"\d+\.\s*(.*)", plan_match.group(1)
        )
    else:
        result["assessment_plan"] = None

    return result
