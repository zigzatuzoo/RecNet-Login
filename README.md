![rnl](https://github.com/Jegarde/RecNet-Login/assets/13438202/5d25fa39-6d8f-4717-82c8-619574036817)
This is a Python package that allows you to acquire your [RecNet](https://rec.net/) access token and more with your cookie! 🍪

# Features
- Automatically renewing token
- Supports 2FA accounts
- Decoding the bearer token
- Detailed exceptions

# Installation
Download the recnetlogin folder and place it in your project.

pip installation once this is stable.

# Setup
### Gathering your session token
1. Login to [RecNet](https://rec.net/). While logging in, make sure you toggle on "Remember me / my machine".
2. Open your browser's DevTools (Inspect Element)
3. Open the `Storage` or `Application` tab on the top
4. Locate `Cookies` > `https://rec.net` on the directory
5. Search for `__Secure-next-auth.session-token` by filtering the cookies
6. Double click the value and copy it 
![image](https://github.com/Jegarde/RecNet-Login/assets/13438202/0fba154d-031e-4c57-87ab-e4d5ae9c0fe1)

### Option 1/2: Storing it in your environment variables (Windows)
1. Search for environment variables and open the first result

![image](https://github.com/Jegarde/RecNet-Login/assets/13438202/c35ebeb9-de31-46ba-a264-f02138560321)

2. Click `Environment Variables...`

![image](https://github.com/Jegarde/RecNet-Login/assets/13438202/dd341365-fa90-4145-82aa-94a12f91019a)

3. Click `New` under System Variables

![image](https://github.com/Jegarde/RecNet-Login/assets/13438202/2d098f6f-145c-4232-b9ed-86000622a077)

4. Name the variable `RN_COOKIE` and paste the copied value

![image](https://github.com/Jegarde/RecNet-Login/assets/13438202/d792c266-b348-459c-b74f-dc765efc1f41)


5. Press OK on all the opened tabs

6. Restart your computer for it to take effect

### Option 2/2: Storing it in a .env.secret file
1. Make a new file named `.env.secret` in your project's directory
2. Type `RN_SESSION_TOKEN=` in the file and paste the copied value

![image](https://github.com/Jegarde/RecNet-Login/assets/13438202/8a9025ed-cb13-43d8-adaf-07a600766fca)


3. If the file is not in your project's directory, make sure to specify it
```py
rnl = RecNetLogin(env_path=".env.secret")  # Env path defaults to local directory
```

### New Auth Workaround
A month ago (as of 03/13/25) Rec Room added DDoS protection to their auth endpoints causing issues for this library.
To get around it we can use FlareSolverr which is a proxy that gets around cloudflare DDoS protection.

## FlareSolverr Setup

### Option 1/2 Host one with Docker
If you already know about docker then please skip to the for Docker X section
If you don't already have docker, install it by using the following:
for windows: https://docs.docker.com/desktop/setup/install/windows-install/
for mac: https://docs.docker.com/desktop/setup/install/mac-install/
for linux: https://docs.docker.com/engine/install/ubuntu/

#### For Docker Engine (Linux)
1. Copy/download the file flaresolverr.docker-compose.yml from the repo
2. Move into the directory that contains the docker-compose file and run:
`docker compose -f <Insert filename> up -d`

#### For Docker Desktop (Windows/Mac)
Use this stack overflow answer ... never touched Docker Desktop
https://stackoverflow.com/a/66071384

### Option 2/2 Using Someone Elses
For the time being I'll host a public Flaresolverr instance with a pretty hard rate limit on one of my vps's. It should be enough to do a couple logins per minute but this should only be used for testing with an alt account.
##### PLEASE DON'T TRUST RANDOM PUBLIC PROXIES WITH YOUR AUTH TOKENS

Now that being said ... the instance will be hosted at `https://flaresolverr.apps.zigzatuzoo.xyz` so your .env file will look like this `FLARESOLVERR_INSTANCE="https://flaresolverr.apps.zigzatuzoo.xyz/v1"`

#### Inserting Your Instance
3. Same way as setting up your `RN_SESSION_TOKEN`
If you are using a .env file then write in it `FLARESOLVERR_INSTANCE="http://<InsertInstanceDomain&Port>/v1"`
So if you are running the FlareSolverr instance on the same system then it will look like this `FLARESOLVERR_INSTANCE="http://localhost:8191/v1"`

# Usage

### Getting your token
```py
from RecNetLogin import RecNetLogin

rnl = RecNetLogin()
token = rnl.get_token()
decoded_token = rnl.get_decoded_token()  # JWT decoded
print(token, decoded_token)
```

### Making authorized calls
```py
from recnetlogin import RecNetLogin

rnl = RecNetLogin(env_path=".env.secret")

# Fetch using RecNetLogin's HTTPX client
r = rnl.client.get("https://accounts.rec.net/account/me")

for key, value in r.json().items():
    print(key, value)

# Close the client once done
rnl.close()
```
