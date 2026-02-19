from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class OrionProof(db.Model):
    __tablename__ = 'orion_proofs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    kind = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text)
    payload = db.Column(db.JSON)
    owner = db.Column(db.String(256))
    orion_id = db.Column(db.String(64))
    sha256 = db.Column(db.String(64))
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'kind': self.kind,
            'text': self.text,
            'payload': self.payload,
            'owner': self.owner,
            'orion_id': self.orion_id,
            'sha256': self.sha256
        }

class OrionQuestion(db.Model):
    __tablename__ = 'orion_questions'
    
    id = db.Column(db.String(32), primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    name = db.Column(db.String(128))
    email = db.Column(db.String(256))
    question = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), default='pending')
    answered_at = db.Column(db.DateTime(timezone=True))
    
    answer = db.relationship('OrionAnswer', backref='question_ref', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'name': self.name,
            'email': self.email,
            'question': self.question,
            'status': self.status,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }

class OrionAnswer(db.Model):
    __tablename__ = 'orion_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.String(32), db.ForeignKey('orion_questions.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    answer = db.Column(db.Text, nullable=False)
    analysis_type = db.Column(db.String(32), default='schonungslos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'answer': self.answer,
            'analysis_type': self.analysis_type
        }

class OrionState(db.Model):
    __tablename__ = 'orion_state'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False)
    value = db.Column(db.JSON)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def get(cls, key, default=None):
        record = cls.query.filter_by(key=key).first()
        return record.value if record else default
    
    @classmethod
    def set(cls, key, value):
        record = cls.query.filter_by(key=key).first()
        if record:
            record.value = value
            record.updated_at = datetime.now(timezone.utc)
        else:
            record = cls(key=key, value=value)
            db.session.add(record)
        db.session.commit()
        return record

class ExternalRequest(db.Model):
    __tablename__ = 'external_requests'
    
    id = db.Column(db.String(64), primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    name = db.Column(db.String(128))
    email = db.Column(db.String(256))
    category = db.Column(db.String(64))
    subject = db.Column(db.String(256))
    message = db.Column(db.Text)
    status = db.Column(db.String(32), default='PENDING_EVALUATION')
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'name': self.name,
            'email': self.email,
            'category': self.category,
            'subject': self.subject,
            'message': self.message,
            'status': self.status
        }
