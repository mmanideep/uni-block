from sqlalchemy.exc import SQLAlchemyError

from crypto_predict.app import db
from crypto_predict.models.custom_exception import ValidationError


class BaseModel(db.Model):
    """
        Abstract model containing default fields id, created_at, updated_at
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    is_deleted = db.Column(db.Boolean, default=False)

    query = db.session.query_property()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self):
        session = db.session.begin_nested()
        try:
            db.session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValidationError(str(e))

    def destroy(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValidationError(str(e))

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        session = db.session.begin_nested()
        try:
            db.session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise ValidationError(str(e))
