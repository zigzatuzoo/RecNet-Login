import httpx
import os
import jwt
import datetime
from typing import Optional
from urllib.parse import urlparse, parse_qs
from dotenv import dotenv_values
from json import loads
from .exceptions import *

class RecNetLogin:
    def __init__(self, env_path: str = None):
        """RecNetLogin, used for getting your RecNet bearer token with ease.

        Args:
            env_path (str, optional): Path to an .env.secret file if you stored your cookie there. Defaults to None.

        Attrs:
            client (httpx.Client): HTTPX client used to fetch the token. Can be reused.

        Raises:
            CookieMissing: Raises when the cookie cannot be found from either a .env.secret file or your system variables.
            InvalidFlareSolverInstance: Raises when the FlareSolver instance is cannot be found from either the specified .env file or your system variables.
        """

        # Prioritize local .env.secret files
        env = dotenv_values(env_path if env_path else ".env.secret")

        # Gotten from .env.secret or system variables?
        self.is_local: bool = False

        # Get identity cookie
        key = "RN_SESSION_TOKEN"
        if key in env:
            cookie = env[key]
            self.is_local = True
        else:
            # If no local .env.secret file, look for globals
            if key in os.environ:
                cookie = os.getenv(key)
            else:
                raise CookieMissing
            
        key = 'FLARESOLVERR_INSTANCE'
        if key in env:
            self.flaresolverr_instance = env[key]
        else:
            raise InvalidFlareSolverrInstance

        # Initialize attributes
        
        #httpx doesn't like my LetsEncrypt ssl cert for some reason
        if 'flaresolverr.apps.zigzatuzoo.xyz' in self.flaresolverr_instance.lower():
            self.cient: httpx.Client = httpx.Client(verify=False)
        else:
            self.client: httpx.Client = httpx.Client()
        self.acookies = {}

        # Get CSRF token
        # As of 03/13/25 not required, if this breaks again first try to uncomment the next line
        #self.acookies["__Host-next-auth.csrf-token"] = self.get_csrf_token()
        
        # Include session token
        self.acookies["__Secure-next-auth.session-token"] = cookie

        # Fetch tokens
        self.__token: str = ""
        self.decoded_token: dict = {}

        self.get_token()
        self.get_decoded_token()

        # Update client headers
        self.client.headers = {
            "Authorization": f"Bearer {self.__token}" 
        }


    def get_flaresolverr(self, url, cookies: None|dict = None):
        headers = {"Content-Type": "application/json"}
        data = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": 5000
            }

        if cookies:
            rcook = []
            for key in cookies.keys():
                rcook.append({"name": key, "value": cookies[key]})
            data['cookies'] = rcook

        resp = self.client.post(self.flaresolverr_instance,json=data,headers=headers)

        data = resp.json()
        
        data = data['solution']['response']
        start = data.find('{')
        end = data.rfind('}')

        info = data[start:end+1]
        data = loads(info)
        return data

    def get_csrf_token(self) -> str:
        
        data = self.get_flaresolverr("https://rec.net/api/auth/csrf/")

        rvar = data['csrfToken']
        return rvar

    def get_decoded_token(self) -> Optional[dict]:
        """Returns a decoded bearer token

        Returns:
            Optional[dict]: A decoded token if one exists
        """
        return self.decoded_token

    def get_token(self, include_bearer: bool = False) -> str:
        """Returns and automatically renews your bearer token.

        Args:
            include_bearer (bool, optional): Whether to include the Bearer prefix to the token. Defaults to False.

        Raises:
            InvalidLocalCookie: Raises if your .env.secret cookie is invalid or has expired.
            InvalidSystemCookie: Raises if your system variable cookie is invalid or has expired.

        Returns:
            str: A bearer token.
        """

        # Check if the token has at least 15 minutes of lifetime left
        if int((datetime.datetime.now() + datetime.timedelta(minutes=15)).timestamp()) > self.decoded_token.get("exp", 0):
            # Less than 15 minutes, renew the token

            # Get with cookie
            auth_url = "https://rec.net/api/auth/session"
            
            data = self.get_flaresolverr(auth_url,self.acookies)

            try:
                self.__token = data["accessToken"]
            except KeyError:
                # The cookie has expired or is invalid
                raise InvalidLocalCookie if self.is_local else InvalidSystemCookie

            # Decode it for later
            self.decoded_token = self.__decode_token(self.__token)

        return f"Bearer {self.__token}" if include_bearer else self.__token
    
    def close(self) -> None:
        """Closes the HTTPX client."""
        self.client.close()

    def __decode_token(self, token: str) -> dict:
        """Decodes bearer tokens

        Args:
            token (str): A bearer token

        Returns:
            dict: Decoded bearer token
        """
        
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded


if __name__ == "__main__":
    rnl = RecNetLogin()

    r = httpx.get(
        url="https://accounts.rec.net/account/me", 
        headers={
            # Always run the "get_token" method when using your token!
            # RecNetLogin will automatically renew the token if it has expired.
            "Authorization": rnl.get_token(include_bearer=True)  
        }
    )

    for key, value in r.json().items():
        print(f"{key} = {value}")

    rnl.close()
