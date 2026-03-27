# Save this as get_token.py
# Install needed libs: pip install google_auth_oauthlib google-api-python-client
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes needed for Blogger
SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_refresh_token():
    # Point this to the file you downloaded from Cloud Console
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    print("\n--- COPY THESE VALUES ---")
    print(f"REFRESH_TOKEN: {creds.refresh_token}")
    print(f"CLIENT_ID: {creds.client_id}")
    print(f"CLIENT_SECRET: {creds.client_secret}")

if __name__ == '__main__':
    get_refresh_token()