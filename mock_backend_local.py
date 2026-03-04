# mock_backend_local.py
# Run with: uvicorn mock_backend_local:app --reload --port 8000

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# 1) Create the FastAPI app FIRST (so decorators can see 'app')
app = FastAPI(title="Local Mock for Voiceв†’Salesforce Fields (no LLM)")

# 2) CORS: allow Lightning and localhost during testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Optional: label overrides for friendlier UI names
HUMAN_LABELS = {
    "Description": "Description",
    "Description__c": "Description",
    "Project__c": "Project",
}

def humanize(api_name: str) -> str:
    return HUMAN_LABELS.get(
        api_name,
        api_name.replace("__c", "").replace("_", " ").title()
    )

# 4) Route (AFTER the 'app' is defined)
@app.post("/api/voice")
async def mock_voice(
    audio: UploadFile = File(...),
    recordId: str = Form(""),
    objectApiName: str = Form("")
):
    """
    Minimal mock that ignores audio and returns a deterministic response
    suitable for the LWC. It considers recordId and objectApiName and
    always pretends the user said: "Description for this record is Salesforce".

    Logic (per your requirement):
    - If objectApiName == 'Opportunity': return ONLY Description__c
    - If objectApiName in {'Project__c','Project'}: return Project_description__c
    - Otherwise: return Description__c as a generic long text field
    """
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] mock /api/voice recordId={recordId} objectApiName={objectApiName} file={audio.filename}")

    parsed_fields = {}
    obj = (objectApiName or "").strip()

    if obj == "Opportunity":
        # Per your note: Opportunity should update only Description__c
        parsed_fields["Description__c"] = "Salesforce"
        parsed_fields["NextStep"] = "Working on SOWs signing"
        parsed_fields["SharePointLink__c"] = "Public"
        parsed_fields["LinkToProposal__c"] = "http://www.google.com"
        parsed_fields["Competitive_Status__c"] = "Open and Competitive"
        parsed_fields["Red_Flags__c"] = "Client budget approval still pending from HQ."
    elif obj in {"Project__c", "Project"}:
        parsed_fields["Customer_description__c"] = "Global healthcare company with a central purpose to help people live their healthiest possible lives."
        parsed_fields["JiraProjectKey__c"] = "SFDX"
        parsed_fields["Project_description__c"] = "Salesforce"
    else:
        parsed_fields["Description__c"] = "Salesforce"  # fallback

    field_labels = {api: humanize(api) for api in parsed_fields.keys()}

    return {
        "status": "processed",
        "recordId": recordId,
        "objectApiName": objectApiName,
        "parsed_fields": parsed_fields,
        "field_labels": field_labels,
    }

# 5) Windows-friendly entry point (optional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
