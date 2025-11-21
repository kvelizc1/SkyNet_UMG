from app.extensions import db
from datetime import datetime

class Visit(db.Model):
    __tablename__ = "visits"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    scheduled_date = db.Column(db.DateTime, nullable=False)

    check_in_time = db.Column(db.DateTime, nullable=True)
    check_in_lat = db.Column(db.Float, nullable=True)
    check_in_lng = db.Column(db.Float, nullable=True)

    check_out_time = db.Column(db.DateTime, nullable=True)
    check_out_lat = db.Column(db.Float, nullable=True)
    check_out_lng = db.Column(db.Float, nullable=True)

    status = db.Column(db.String(50), default="pendiente")  
    notes = db.Column(db.String(300), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "technician_id": self.technician_id,
            "supervisor_id": self.supervisor_id,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "check_in_time": self.check_in_time.isoformat() if self.check_in_time else None,
            "check_in_lat": self.check_in_lat,
            "check_in_lng": self.check_in_lng,
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
            "check_out_lat": self.check_out_lat,
            "check_out_lng": self.check_out_lng,
            "status": self.status,
            "notes": self.notes
        }
