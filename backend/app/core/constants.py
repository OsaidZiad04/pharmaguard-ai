LOW_CONFIDENCE_THRESHOLD = 0.75

REQUIRED_PATIENT_CONTEXT_FIELDS = (
    "age",
    "pregnancy_status",
    "allergies",
    "current_medications",
)

SAFETY_BOUNDARY_MESSAGE = (
    "Draft support only. A licensed pharmacist must verify the prescription, "
    "patient context, and counseling content before any patient-facing use."
)
