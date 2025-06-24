from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import os
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

load_dotenv()

# Initialize Google Cloud Logging
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
cloud_logging_client = google.cloud.logging.Client(project=project_id)
handler = CloudLoggingHandler(cloud_logging_client, name="agent")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

# Initialize Vertex AI
location = os.environ["GOOGLE_CLOUD_LOCATION"]
app_name = os.environ.get("APP_NAME", "Agent App")
bucket_name = f"gs://{project_id}-bucket"

vertexai.init(
    project=project_id,
    location=location,
    staging_bucket=bucket_name,
)

remote_app = vertexai.agent_engines.get('')
remote_session = remote_app.create_session(user_id="u_457")

def query_agent(question: str) -> str:
    try:

        events = remote_app.stream_query(
            user_id="u_457",
            session_id=remote_session["id"],
            message=question,
        )

        response_text = ""
        for event in events:
            for part in event["content"]["parts"]:
                if "text" in part:
                    response_text += part["text"]
                    logging.info("[remote response] " + response_text)
        return response_text

        raise HTTPException(status_code=500, detail="No response from agent.")
    except Exception as e:
        logging.error(f"Error querying agent: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")