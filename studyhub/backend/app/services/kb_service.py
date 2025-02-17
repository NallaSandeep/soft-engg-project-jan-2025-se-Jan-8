"""Personal knowledge base service"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from app import db
from app.models.personal_kb import PersonalKnowledgeBase, KBFolder, KBDocument
from app.models.user import User
from config import Config
import logging

logger = logging.getLogger(__name__)

class KBService:
    """Service for managing personal knowledge bases"""

    @staticmethod
    def create_knowledge_base(user_id: int, name: str, description: Optional[str] = None) -> PersonalKnowledgeBase:
        """Create a new personal knowledge base"""
        try:
            kb = PersonalKnowledgeBase(
                user_id=user_id,
                name=name,
                description=description,
                settings={}
            )
            db.session.add(kb)
            db.session.commit()
            return kb
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create knowledge base: {str(e)}")
            raise

    @staticmethod
    def get_knowledge_base(kb_id: int, user_id: int) -> Optional[PersonalKnowledgeBase]:
        """Get a knowledge base by ID"""
        return PersonalKnowledgeBase.query.filter_by(
            id=kb_id,
            user_id=user_id,
            is_active=True
        ).first()

    @staticmethod
    def create_folder(
        kb_id: int,
        name: str,
        parent_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> KBFolder:
        """Create a new folder in the knowledge base"""
        try:
            folder = KBFolder(
                kb_id=kb_id,
                parent_id=parent_id,
                name=name,
                description=description
            )
            db.session.add(folder)
            db.session.commit()
            return folder
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create folder: {str(e)}")
            raise

    @staticmethod
    def get_folder_tree(kb_id: int) -> List[Dict[str, Any]]:
        """Get the folder tree for a knowledge base"""
        def build_tree(parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
            folders = KBFolder.query.filter_by(
                kb_id=kb_id,
                parent_id=parent_id,
                is_active=True
            ).order_by(KBFolder.order, KBFolder.name).all()
            
            return [{
                'id': folder.id,
                'name': folder.name,
                'description': folder.description,
                'path': folder.full_path,
                'document_count': folder.documents.count(),
                'subfolders': build_tree(folder.id)
            } for folder in folders]
        
        return build_tree()

    @staticmethod
    def add_document(
        kb_id: int,
        document_id: str,
        folder_id: Optional[int],
        title: str,
        document_type: str,
        metadata: Dict[str, Any]
    ) -> KBDocument:
        """Add a document to the knowledge base"""
        try:
            doc = KBDocument(
                kb_id=kb_id,
                folder_id=folder_id,
                document_id=document_id,
                title=title,
                document_type=document_type,
                doc_metadata=metadata
            )
            db.session.add(doc)
            db.session.commit()
            return doc
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to add document: {str(e)}")
            raise

    @staticmethod
    def get_document(kb_id: int, document_id: str) -> Optional[KBDocument]:
        """Get a document from the knowledge base"""
        return KBDocument.query.filter_by(
            kb_id=kb_id,
            document_id=document_id
        ).first()

    @staticmethod
    def update_document_metadata(
        document: KBDocument,
        metadata: Dict[str, Any]
    ) -> KBDocument:
        """Update document metadata"""
        try:
            # Update local metadata
            document.title = metadata.get('title', document.title)
            document.description = metadata.get('description', document.description)
            document.is_favorite = metadata.get('is_favorite', document.is_favorite)
            document.importance = metadata.get('importance', document.importance)
            document.source_url = metadata.get('source_url', document.source_url)
            document.tags = metadata.get('tags', document.tags)
            document.doc_metadata = metadata.get('metadata', document.doc_metadata)
            
            # Update folder if path changed
            new_folder_path = metadata.get('folder_path')
            if new_folder_path and (not document.folder or document.folder.full_path != new_folder_path):
                # Find or create folder
                folder = KBService._get_or_create_folder_path(document.kb_id, new_folder_path)
                document.folder_id = folder.id
            
            db.session.commit()
            
            # Update StudyIndexer metadata
            KBService._update_indexer_metadata(document)
            
            return document
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update document metadata: {str(e)}")
            raise

    @staticmethod
    def _get_or_create_folder_path(kb_id: int, path: str) -> KBFolder:
        """Get or create a folder from a path"""
        if not path or path == '/':
            return None
            
        parts = [p for p in path.split('/') if p]
        current_folder = None
        
        for i, name in enumerate(parts):
            parent_id = current_folder.id if current_folder else None
            folder = KBFolder.query.filter_by(
                kb_id=kb_id,
                parent_id=parent_id,
                name=name,
                is_active=True
            ).first()
            
            if not folder:
                folder = KBService.create_folder(
                    kb_id=kb_id,
                    name=name,
                    parent_id=parent_id
                )
            
            current_folder = folder
        
        return current_folder

    @staticmethod
    def _update_indexer_metadata(document: KBDocument) -> None:
        """Update document metadata in StudyIndexer"""
        try:
            # Prepare metadata for StudyIndexer
            metadata = {
                "personal": {
                    "folder_path": document.folder.full_path if document.folder else None,
                    "is_favorite": document.is_favorite,
                    "importance": document.importance,
                    "last_viewed": document.last_viewed.isoformat() if document.last_viewed else None,
                    "source_url": document.source_url,
                    "related_docs": [d.document_id for d in document.related_docs],
                    "custom_fields": document.doc_metadata or {}
                }
            }
            
            # Send update to StudyIndexer
            response = requests.patch(
                f"{Config.INDEXER_SERVICE_URL}/api/v1/personal/documents/{document.document_id}/metadata",
                json=metadata,
                headers={"Authorization": f"Bearer {Config.INDEXER_API_KEY}"}
            )
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Failed to update StudyIndexer metadata: {str(e)}")
            # Don't raise - we don't want to fail the transaction if StudyIndexer update fails
            # The metadata will be eventually consistent

    @staticmethod
    def add_related_documents(
        document: KBDocument,
        related_ids: List[str],
        relation_type: str = 'related'
    ) -> None:
        """Add related documents"""
        try:
            # Find related documents
            related_docs = KBDocument.query.filter(
                KBDocument.document_id.in_(related_ids)
            ).all()
            
            # Add relationships
            for related in related_docs:
                if related not in document.related_docs:
                    document.related_docs.append(related)
            
            db.session.commit()
            
            # Update StudyIndexer metadata
            KBService._update_indexer_metadata(document)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to add related documents: {str(e)}")
            raise

    @staticmethod
    def remove_related_document(
        document: KBDocument,
        related_id: str
    ) -> None:
        """Remove a related document"""
        try:
            related = KBDocument.query.filter_by(document_id=related_id).first()
            if related and related in document.related_docs:
                document.related_docs.remove(related)
                db.session.commit()
                
                # Update StudyIndexer metadata
                KBService._update_indexer_metadata(document)
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to remove related document: {str(e)}")
            raise

    @staticmethod
    def get_related_documents(document: KBDocument) -> List[Dict[str, Any]]:
        """Get related documents with their details"""
        return [doc.to_dict() for doc in document.related_docs] 