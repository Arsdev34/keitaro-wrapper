import json
import subprocess
from app.config import settings

class KeitaroClient:
    def __init__(self):
        self.base_url = settings.keitaro_url
        self.api_key = settings.keitaro_api_key

    async def _request(self, method, endpoint, json_data=None):
        url = self.base_url + "/admin_api/v1/" + endpoint
        cmd = ["curl.exe", "-s", "--max-time", "60", "-X", method, url,
               "-H", "Api-Key: " + self.api_key,
               "-H", "Content-Type: application/json"]
        if json_data:
            cmd.extend(["-d", json.dumps(json_data)])
        r = subprocess.run(cmd, capture_output=True, timeout=65)
        t = r.stdout.decode("utf-8", errors="replace").strip()
        if t:
            try:
                return json.loads(t)
            except Exception:
                pass
        if r.returncode != 0:
            raise Exception("Curl failed, code " + str(r.returncode) + " stderr: " + r.stderr.decode("utf-8", errors="replace")[:200])
        raise Exception("Empty response from Keitaro")
    async def get_offers(self):
        return await self._request("GET", "offers")

    async def get_campaign_streams(self, campaign_id):
        return await self._request("GET", "campaigns/" + str(campaign_id) + "/streams")

    async def get_stream(self, stream_id):
        return await self._request("GET", "streams/" + str(stream_id))

    async def get_group_id(self, group_name="FORTESTS"):
        data = await self._request("GET", "groups?type=campaigns")
        items = data.get("groups", data) if isinstance(data, dict) else data
        for g in items:
            if g.get("name") == group_name:
                return g.get("id")
        return None
    async def create_campaign(self, name, geo):
        final_name = "test_khristoforov_" + name
        gid = await self.get_group_id()
        if gid is None:
            raise Exception("Group FORTESTS not found, create it in Keitaro first")
        payload = {"name": final_name,
                   "alias": final_name.lower().replace(" ", "_"),
                   "type": "position", "state": "active",
                   "cost_type": "CPC", "cost_value": 0,
                   "cost_currency": "USD", "cost_auto": False,
                   "group_id": gid, "traffic_source_id": 836,
                   "domain_id": 1813}
        return await self._request("POST", "campaigns", payload)
    async def create_stream(self, campaign_id, stream_type, geo, offer_id=None):
        geo_upper = geo.upper()
        if stream_type == "redirect":
            gf = {"name": "country", "mode": "allow", "payload": [geo_upper]}
            p = {"campaign_id": campaign_id, "type": "regular",
                 "name": "Redirect to Google", "schema": "redirect",
                 "action_type": "http", "action_payload": "https://google.com",
                 "weight": 100, "filters": [gf]}
        else:
            gf = {"name": "country", "mode": "deny", "payload": [geo_upper]}
            p = {"campaign_id": campaign_id, "type": "regular",
                 "name": "Offer Stream", "schema": "landings",
                 "action_type": "show_html", "landings": [],
                 "offers": [{"offer_id": offer_id, "share": 100}],
                 "weight": 100, "filters": [gf]}
        return await self._request("POST", "streams", p)

    async def update_stream_offers(self, stream_id, offer_ids):
        s = await self.get_stream(stream_id)
        if not isinstance(s, dict) or not s.get("id"):
            raise Exception("get_stream failed: " + str(s)[:200])
        s["offers"] = [{"offer_id": int(i), "share": 100} for i in offer_ids]
        return await self._request("PUT", "streams/" + str(stream_id), s)

client = KeitaroClient()
