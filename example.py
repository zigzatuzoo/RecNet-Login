from recnetlogin import RecNetLogin
import httpx

"""
Barebones example on how to use RecNetLogin.

Make sure you have RN_SESSION_TOKEN in your system environment variables or locally in a .env.secret file.
For more information, read the README https://github.com/Jegarde/RecNet-Login/
"""

rnl = RecNetLogin(env_path=".env.secret")

# Fetch using RecNetLogin's HTTPX client
r = rnl.client.get("https://accounts.rec.net/account/me")

for key, value in r.json().items():
    print(key, value)

# Close the client once done
rnl.close()