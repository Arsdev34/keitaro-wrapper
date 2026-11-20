from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class CampaignHistory(Base):
    __tablename__ = "campaign_history"
    id = Column(Integer, primary_key=True, index=True)
    keitaro_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    offer_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
