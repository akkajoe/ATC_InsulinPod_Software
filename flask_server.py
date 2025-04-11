import requests
import webbrowser
from flask import Flask, request

client_id = "Vk6D8gjzH6qZzJS82eLsKUU9tVEykYs0"
redirect_uri = "http://127.0.0.1:5000/callback"
client_secret = "lUqYT88FMB9nCDgs"

app = Flask(__name__)
access_token = None  

@app.route("/callback")
def callback():
    global access_token

    auth_code = request.args.get("code")
    if request.args.get("error"):
        return f"Authorization failed: {request.args.get('error')}", 400

    print(f"\nAuthorization Code Received: {auth_code}")

    token_url = "https://sandbox-api.dexcom.com/v2/oauth2/token"
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    token_response = requests.post(token_url, data=payload, headers=headers)
    if token_response.status_code != 200:
        return f"Token exchange failed: {token_response.text}", 500

    tokens = token_response.json()
    access_token = tokens["access_token"]  # Save for next request

    return f"""
    <h2>Auth Success</h2>
    <a href="/egvs" target="_blank">Click here to fetch EGV data</a>
    """

@app.route("/egvs")
def egvs():
    global access_token

    if not access_token:
        return "No access token found. Please authenticate first.", 403

    url = "https://sandbox-api.dexcom.com/v2/users/self/egvs"

    # Replace these with real dates once you confirm the account has data!
    params = {
        "startDate": "2023-01-01T09:00:00",
        "endDate": "2023-01-01T10:00:00"
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return f"EGV request failed: {response.text}", 500

    data = response.json()
    return f"<h2>EGV Data</h2><pre>{data}</pre>"

# Open Dexcom Auth URL
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(port=5000)).start()

    auth_url = (
        f"https://sandbox-api.dexcom.com/v2/oauth2/login"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=offline_access"
    )
    webbrowser.open(auth_url)
