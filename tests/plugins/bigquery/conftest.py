import os
import json
import uuid
import pytest
from apiclient.discovery import build
from oauth2client.client import GoogleCredentials


# Fixtures


@pytest.fixture
def options(google_credentials_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path
    credentials = GoogleCredentials.get_application_default()
    with open(google_credentials_path) as file:
        return {
            "service": build("bigquery", "v2", credentials=credentials),
            "project": json.load(file)["project_id"],
            "dataset": "python",
            "prefix": "%s_" % uuid.uuid4().hex,
        }
