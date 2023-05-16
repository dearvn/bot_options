import requests,os,redis,time,datetime,json
from . import auth

redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=True)

class TDASession(requests.Session):
    def __init__(self, refresh_token=None, client_id=None):
        super().__init__()
        self._refreshToken = {"token": refresh_token}
        self._accessToken = {
            "token": "",
            "created_at": time.time(),
            "expires_in": -1,
        }  # Set to -1 so that it gets refreshed immediately and its age tracked.
        self._client_id = client_id
        self._headers = {}

    def _set_header_auth(self):
        self._headers.update({"Authorization": "Bearer " + self._accessToken["token"]})

    def request(self, *args, **kwargs):
        self._refresh_token_if_invalid()
        return super().request(headers=self._headers, *args, **kwargs)

    def _refresh_token_if_invalid(self):
        # Expire the token one minute before its expiration time to be safe
        if self._is_token_invalid():
            token = auth.access_token(self._refreshToken["token"], self._client_id)

            token['created_at'] = time.time()
            access_token = {
                "access_token": token['access_token'],
                "expires_in": token['expires_in'],
                "created_at": token['created_at']
            }
            redis_client.set('tda_token', json.dumps(access_token))
            print("******************************************************generate token",
                  datetime.datetime.fromtimestamp(token['created_at']))

            self._set_access_token(token)

    def _is_token_invalid(self):
        self._get_access_token()

        if ( self._accessToken == None or
            not self._accessToken["token"]
            or self._access_token_age_secs() >= self._accessToken["expires_in"] - 60
        ):
            return True
        else:
            return False

    def _get_access_token(self):
        token = redis_client.get('tda_token')
        if token != None:
            self._set_access_token(json.loads(token))

    def _set_access_token(self, token):
        self._accessToken["token"] = token["access_token"]
        self._accessToken["created_at"] = token['created_at']
        self._accessToken["expires_in"] = int(token["expires_in"])
        self._set_header_auth()

    def _access_token_age_secs(self):
        age_secs = time.time() - self._accessToken["created_at"]
        print("******************************************************age_secs:", age_secs)
        return age_secs
