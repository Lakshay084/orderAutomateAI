from google.oauth2 import service_account
import google.auth.transport.requests
import requests

SCOPES = ["https://www.googleapis.com/auth/generative-language"]

def get_access_token():
    # Path to your service account key file
    credentials = service_account.Credentials.from_service_account_file(
        "/Users/lakshaynagar/Desktop/WEB DEV/orderAutomateAI/backend/config/gen-lang-client-0345715786-6df181b6634a.json",
          scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

if __name__ == "__main__":
    access_token = get_access_token()
    print("Access Token:", access_token)
