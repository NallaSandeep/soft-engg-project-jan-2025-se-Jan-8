"""
Base Model Module
---------------
This module provides the base model class that all other models inherit from.
It implements common functionality like timestamps, CRUD operations, and utility methods.

Key Features:
- Automatic timestamps for created_at and updated_at
- Common CRUD operations (save, delete, update)
- Utility methods for retrieving instances
- SQLAlchemy integration

Usage:
    class MyModel(BaseModel):
        __tablename__ = 'my_table'
        id = db.Column(db.Integer, primary_key=True)
        # ... other fields ...
"""

from datetime import datetime
from .. import db

class BaseModel(db.Model):
    """Base model class that all other models will inherit from."""
    
    __abstract__ = True

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """Save the model instance to the database."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """Delete the model instance from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, **kwargs):
        """Update the model instance with the given kwargs."""
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
        self.save()

    @classmethod
    def get_by_id(cls, id):
        """Get a model instance by its ID."""
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        """Get all instances of the model."""
        return cls.query.all()
