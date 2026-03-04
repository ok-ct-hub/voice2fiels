from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Local Mock for Voice→Salesforce Fields (no LLM)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HUMAN_LABELS = {
    "Description": "Description",
    "Description__c": "Description",
    "Project__c": "Project",
    "Project_description__c": "Project description",
}

def humanize(api_name: str) -> str:
    return HUMAN_LABELS.get(api_name, api_name.replace("__c", "").replace("_", " ").title())

@app.post("/api/voice")
async def mock_voice(
    audio: UploadFile = File(...),
    recordId: str = Form(""),
    objectApiName: str = Form("")
):
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] mock /api/voice recordId={recordId} objectApiName={objectApiName} file={audio.filename}")

    parsed_fields = {}
    obj = (objectApiName or "").strip()

    if obj == "Opportunity":
        parsed_fields["Description__c"] = "Salesforce"
    elif obj in {"Project__c", "Project"}:
        parsed_fields["Project_description__c"] = "Salesforce"
    else:
        parsed_fields["Description__c"] = "Salesforce"

    field_labels = {api: humanize(api) for api in parsed_fields.keys()}

    return {
        "status": "processed",
        "recordId": recordId,
        "objectApiName": objectApiName,
        "parsed_fields": parsed_fields,
        "field_labels": field_labels,
    }
