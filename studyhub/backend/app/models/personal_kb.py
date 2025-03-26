"""NOT USED"""
"""Personal knowledge base models"""
from datetime import datetime
from app import db
from .base import BaseModel
from sqlalchemy import JSON

class PersonalKnowledgeBase(BaseModel):
    """Model for managing personal knowledge bases"""
    __tablename__ = 'personal_knowledge_bases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    settings = db.Column(JSON)  # User preferences and settings

    # Relationships
    user = db.relationship('User', back_populates='knowledge_bases')
    folders = db.relationship('KBFolder', back_populates='knowledge_base', lazy='dynamic')
    documents = db.relationship('KBDocument', back_populates='knowledge_base', lazy='dynamic')

    def __repr__(self):
        return f'<PersonalKB {self.name} (User: {self.user_id})>'

class KBFolder(BaseModel):
    """Model for organizing documents in folders"""
    __tablename__ = 'kb_folders'

    id = db.Column(db.Integer, primary_key=True)
    kb_id = db.Column(db.Integer, db.ForeignKey('personal_knowledge_bases.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('kb_folders.id'))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)  # For manual ordering
    folder_metadata = db.Column(JSON)  # Additional folder metadata

    # Relationships
    knowledge_base = db.relationship('PersonalKnowledgeBase', back_populates='folders')
    parent = db.relationship('KBFolder', remote_side=[id], backref=db.backref('subfolders', lazy='dynamic'))
    documents = db.relationship('KBDocument', back_populates='folder', lazy='dynamic')

    def __repr__(self):
        return f'<KBFolder {self.name} (KB: {self.kb_id})>'

    @property
    def full_path(self):
        """Get the full path of the folder"""
        path = [self.name]
        current = self.parent
        while current:
            path.append(current.name)
            current = current.parent
        return '/' + '/'.join(reversed(path))

class KBDocument(BaseModel):
    """Model for tracking documents in personal knowledge base"""
    __tablename__ = 'kb_documents'

    id = db.Column(db.Integer, primary_key=True)
    kb_id = db.Column(db.Integer, db.ForeignKey('personal_knowledge_bases.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('kb_folders.id'))
    document_id = db.Column(db.String(36), nullable=False)  # UUID from StudyIndexer
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    document_type = db.Column(db.String(50), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    importance = db.Column(db.Integer, default=1)  # 1-5 scale
    last_viewed = db.Column(db.DateTime)
    view_count = db.Column(db.Integer, default=0)
    source_url = db.Column(db.String(500))
    tags = db.Column(JSON)  # Array of tags
    doc_metadata = db.Column(JSON)  # Additional document metadata

    # Relationships
    knowledge_base = db.relationship('PersonalKnowledgeBase', back_populates='documents')
    folder = db.relationship('KBFolder', back_populates='documents')
    related_docs = db.relationship(
        'KBDocument',
        secondary='kb_document_relations',
        primaryjoin='KBDocument.id == kb_document_relations.c.source_doc_id',
        secondaryjoin='KBDocument.id == kb_document_relations.c.target_doc_id',
        backref=db.backref('related_by', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<KBDocument {self.title} (ID: {self.document_id})>'

    def to_dict(self):
        """Convert document to dictionary representation"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'title': self.title,
            'description': self.description,
            'document_type': self.document_type,
            'folder_path': self.folder.full_path if self.folder else None,
            'is_favorite': self.is_favorite,
            'importance': self.importance,
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None,
            'view_count': self.view_count,
            'source_url': self.source_url,
            'tags': self.tags or [],
            'metadata': self.doc_metadata or {},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update_view_stats(self):
        """Update document view statistics"""
        self.last_viewed = datetime.utcnow()
        self.view_count += 1
        db.session.commit()

# Association table for document relationships
kb_document_relations = db.Table(
    'kb_document_relations',
    db.Column('source_doc_id', db.Integer, db.ForeignKey('kb_documents.id'), primary_key=True),
    db.Column('target_doc_id', db.Integer, db.ForeignKey('kb_documents.id'), primary_key=True),
    db.Column('relation_type', db.String(50)),  # e.g., 'reference', 'similar', 'prerequisite'
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('relation_metadata', JSON)  # Additional relationship metadata
) 