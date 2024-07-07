import aiohttp



class TwitchStreamChecker:
    def __init__(self, TWITCH_USERNAME, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN):
        self.TWITCH_USERNAME = TWITCH_USERNAME
        self.CLIENT_ID = CLIENT_ID
        self.CLIENT_SECRET = CLIENT_SECRET
        self.REFRESH_TOKEN = REFRESH_TOKEN
        self.ACCESS_TOKEN = ACCESS_TOKEN


    async def is_streamer_live(self):
        if any(var is None for var in [self.TWITCH_USERNAME, self.CLIENT_ID, self.CLIENT_SECRET, self.REFRESH_TOKEN, self.ACCESS_TOKEN]):
            return None

        # Get the stream information
        stream_info = await self.get_stream_info()
        if stream_info is None:
            return {
                'is_live': False,
                'title': '',
                'url': '',
                'preview': '',
                'avatar': ''
            }


        user_info = await self.get_user_info()
        if user_info is None:
            return {
                'is_live': True,
                'title': stream_info['title'],
                'url': f'https://www.twitch.tv/{self.TWITCH_USERNAME}',
                'preview': stream_info['thumbnail_url'].format(width=1600, height=900),
                'avatar': 'https://assetsio.gnwcdn.com/twitch-logo-cropped.jpg?width=1200&height=1200&fit=crop&quality=100&format=png&enable=upscale&auto=webp'
            }

        return {
            'is_live': True,
            'title': stream_info['title'],
            'url': f'https://www.twitch.tv/{self.TWITCH_USERNAME}',
            'preview': stream_info['thumbnail_url'].format(width=1600, height=900),
            'avatar': user_info['profile_image_url']
        }


    async def get_stream_info(self):
        url = f'https://api.twitch.tv/helix/streams?user_login={self.TWITCH_USERNAME}'
        headers = {
            'Client-ID': self.CLIENT_ID,
            'Authorization': f'Bearer {self.ACCESS_TOKEN}'
        }

        # Refresh the access token using the refresh token
        new_access_token = await self.refresh_access_token()
        headers['Authorization'] = f'Bearer {new_access_token}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        return data['data'][0]
                    else:
                        return None
                else:
                    return None


    async def get_user_info(self):
        url = f'https://api.twitch.tv/helix/users?login={self.TWITCH_USERNAME}'
        headers = {
            'Client-ID': self.CLIENT_ID,
            'Authorization': f'Bearer {self.ACCESS_TOKEN}'
        }

        # Refresh the access token using the refresh token
        new_access_token = await self.refresh_access_token()
        headers['Authorization'] = f'Bearer {new_access_token}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        return data['data'][0]
                    else:
                        return None
                else:
                    return None


    async def refresh_access_token(self):
        refresh_url = 'https://id.twitch.tv/oauth2/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.REFRESH_TOKEN,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(refresh_url, data=data) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['access_token']
                else:
                    raise Exception('Failed to refresh access token')
