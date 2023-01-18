from datetime import datetime

from sqlalchemy.orm import registry
from sqlalchemy import Column

from sqlalchemy.orm import registry
from sqlalchemy.types import Integer, Boolean, String, DateTime, LargeBinary, JSON

mapping_registry = registry() 
Base = mapping_registry.generate_base()

class OCRRequest(Base):
    __tablename__ = "ocr_request"
    id = Column(Integer, primary_key=True)
    user = Column(String)
    image_blob = Column(LargeBinary, nullable=False)
    status = Column(String, nullable=False, default='waiting')
    result = Column(JSON)

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime)

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'result': self.result
        }