from fastapi import FastAPI, HTTPException,Depends, Header
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI(title="SA Compliance API", version="1.0")

class IDRequest(BaseModel):
    id_number: str

# -------------------------
# Helper: Luhn checksum for SA ID
# -------------------------
def luhn_checksum(id_number: str) -> bool:
    digits = [int(d) for d in id_number]
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):  # exclude last digit
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0

# -------------------------
# Endpoint: Verify SA ID
# -------------------------
@app.get("/verify_id")
def verify_id(id_number: str):

    # Basic length check
    if not id_number.isdigit() or len(id_number) != 13:
        raise HTTPException(status_code=400, detail="Invalid ID number format")

    # Validate date of birth
    try:
        dob = datetime.strptime(id_number[:6], "%y%m%d").date()
        today = datetime.today().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date of birth in ID")

    # Gender
    sequence = int(id_number[6:10])
    gender = "Male" if sequence >= 5000 else "Female"

    # Citizenship
    citizen = "SA" if id_number[10] == "0" else "Other"

    # Luhn check
    valid = luhn_checksum(id_number)

    return {
        "valid": valid,
        "id_number": id_number,
        "date_of_birth": str(dob),
        "age": age,
        "gender": gender,
        "citizen": citizen
    }

# -------------------------
# Endpoint: Check API Health
# -------------------------
@app.get("/health")
def health_check():
    return {"status ok"}
