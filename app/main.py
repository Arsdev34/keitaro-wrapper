from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, init_db
from app.keitaro_client import client
from app.models import CampaignHistory
from contextlib import asynccontextmanager
import uuid

@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="create.html")
@app.post("/create-campaign")
async def create_campaign(request: Request, name: str = Form(...),
                          geo: str = Form(...), offer_id: int = Form(...),
                          db: AsyncSession = Depends(get_db)):
    try:
        unique_name = name + "_" + uuid.uuid4().hex[:4]
        c = await client.create_campaign(unique_name, geo)
        if not (isinstance(c, dict) and c.get("id")):
            raise Exception("campaign failed: " + str(c)[:200])
        camp_id = c["id"]
        s1 = await client.create_stream(camp_id, "redirect", geo)
        if not (isinstance(s1, dict) and s1.get("id")):
            raise Exception("redirect stream failed: " + str(s1)[:200])
        s2 = await client.create_stream(camp_id, "offer", geo, offer_id)
        if not (isinstance(s2, dict) and s2.get("id")):
            raise Exception("offer stream failed: " + str(s2)[:200])
        db.add(CampaignHistory(keitaro_id=camp_id, name=unique_name, offer_id=offer_id))
        await db.commit()
        msg = "OK! ID: " + str(camp_id)
        return templates.TemplateResponse(request=request, name="create.html",
                                          context={"message": msg})
    except Exception as e:
        return templates.TemplateResponse(request=request, name="create.html",
                                          context={"error": str(e)[:400]})
@app.get("/api/offers")
async def api_offers():
    try:
        offers = await client.get_offers()
        out = []
        if isinstance(offers, list):
            for o in offers:
                out.append({"id": o.get("id"), "name": o.get("name")})
        return {"status": "ok", "offers": out}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/edit", response_class=HTMLResponse)
async def edit_page(request: Request):
    return templates.TemplateResponse(request=request, name="edit.html")

@app.get("/api/campaigns/{campaign_id}/streams")
async def api_get_streams(campaign_id: int):
    try:
        streams = await client.get_campaign_streams(campaign_id)
        return {"status": "ok", "streams": streams}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/campaigns/{campaign_id}/update-offers")
async def api_update_offers(campaign_id: int, request: Request):
    try:
        data = await request.json()
        if not data.get("stream_id"):
            raise HTTPException(status_code=400, detail="Missing stream_id")
        res = await client.update_stream_offers(data["stream_id"], data.get("offer_ids") or [])
        if isinstance(res, dict) and res.get("id"):
            return {"status": "ok", "message": "Offers updated"}
        return {"status": "error", "message": str(res)[:300]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
