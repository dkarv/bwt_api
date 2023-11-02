import aiohttp
import asyncio
import base64

class BwtApi:
    def __init__(self, host, code):
        self.host = host
        self.code = code
        auth = f"user:{code}"
        base64_auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
        self.headers = {"Authorization": f"Basic {base64_auth}"}
    
    async def get_data(self, endpoint):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"http://{self.host}:8080/api/{endpoint}") as response:

                print("Status:", response.status)
                print("Content-type:", response.headers['content-type'])

                json = await response.json(content_type=None)
                return json

    async def get_current_data(self):
        print(f"Fetching current data from {self.host}")
        return await self.get_data("GetCurrentData")

    async def get_daily_data(self):
        print(f"Fetching daily data from {self.host}")
        return await self.get_data("GetDailyData")

    async def get_monthly_data(self):
        print(f"Fetching monthly data from {self.host}")
        return await self.get_data("GetMonthlyData")

    async def get_yearly_data(self):
        print(f"Fetching yearly data from {self.host}")
        return await self.get_data("GetYearlyData")