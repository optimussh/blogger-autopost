from google_auth_oauthlib.flow import InstalledAppFlow
import json

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/blogger']
)

creds = flow.run_local_server(port=0)

print("\n=== Refresh Token 생성 완료! ===")
print("G_REFRESH_TOKEN:")
print(creds.refresh_token)

# token.json으로 저장 (나중에 필요할 수 있음)
with open('token.json', 'w') as f:
    json.dump({
        'refresh_token': creds.refresh_token,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret
    }, f, indent=2)