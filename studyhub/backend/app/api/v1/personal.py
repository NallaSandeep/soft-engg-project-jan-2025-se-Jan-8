"""Personal knowledge base API endpoints"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.personal_kb import PersonalKnowledgeBase, KBFolder, KBDocument
from app.services.kb_service import KBService
from app.utils.decorators import user_required
import logging

logger = logging.getLogger(__name__)
personal_bp = Blueprint('personal', __name__)

@personal_bp.route('/kb', methods=['GET'])
@jwt_required()
@user_required
def get_knowledge_bases():
    """Get all knowledge bases for the current user"""
    try:
        user_id = get_jwt_identity()
        
        # Get all active knowledge bases for the user
        knowledge_bases = PersonalKnowledgeBase.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': kb.id,
                'name': kb.name,
                'description': kb.description,
                'document_count': kb.documents.count()
            } for kb in knowledge_bases]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get knowledge bases: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get knowledge bases'
        }), 500

@personal_bp.route('/kb', methods=['POST'])
@jwt_required()
@user_required
def create_knowledge_base():
    """Create a new personal knowledge base"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        kb = KBService.create_knowledge_base(
            user_id=user_id,
            name=data['name'],
            description=data.get('description')
        )
        
        return jsonify({
            'success': True,
            'message': 'Knowledge base created successfully',
            'data': {
                'id': kb.id,
                'name': kb.name,
                'description': kb.description
            }
        }), 201
        
    except KeyError as e:
        return jsonify({
            'success': False,
            'message': f'Missing required field: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Failed to create knowledge base: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create knowledge base'
        }), 500

@personal_bp.route('/kb/<int:kb_id>/folders', methods=['GET'])
@jwt_required()
@user_required
def get_folder_structure(kb_id):
    """Get folder structure for a knowledge base"""
    try:
        user_id = get_jwt_identity()
        
        # Verify ownership
        kb = KBService.get_knowledge_base(kb_id, user_id)
        if not kb:
            return jsonify({
                'success': False,
                'message': 'Knowledge base not found'
            }), 404
        
        # Get folder tree
        folders = KBService.get_folder_tree(kb_id)
        
        return jsonify({
            'success': True,
            'data': folders
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get folder structure: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get folder structure'
        }), 500

@personal_bp.route('/kb/<int:kb_id>/folders', methods=['POST'])
@jwt_required()
@user_required
def create_folder(kb_id):
    """Create a new folder in the knowledge base"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Verify ownership
        kb = KBService.get_knowledge_base(kb_id, user_id)
        if not kb:
            return jsonify({
                'success': False,
                'message': 'Knowledge base not found'
            }), 404
        
        folder = KBService.create_folder(
            kb_id=kb_id,
            name=data['name'],
            parent_id=data.get('parent_id'),
            description=data.get('description')
        )
        
        return jsonify({
            'success': True,
            'message': 'Folder created successfully',
            'data': {
                'id': folder.id,
                'name': folder.name,
                'path': folder.full_path,
                'description': folder.description
            }
        }), 201
        
    except KeyError as e:
        return jsonify({
            'success': False,
            'message': f'Missing required field: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Failed to create folder: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create folder'
        }), 500

@personal_bp.route('/kb/<int:kb_id>/documents', methods=['POST'])
@jwt_required()
@user_required
def add_document(kb_id):
    """Add a document to the knowledge base"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Verify ownership
        kb = KBService.get_knowledge_base(kb_id, user_id)
        if not kb:
            return jsonify({
                'success': False,
                'message': 'Knowledge base not found'
            }), 404
        
        document = KBService.add_document(
            kb_id=kb_id,
            document_id=data['document_id'],
            folder_id=data.get('folder_id'),
            title=data['title'],
            document_type=data['document_type'],
            metadata=data.get('doc_metadata', {})
        )
        
        return jsonify({
            'success': True,
            'message': 'Document added successfully',
            'data': document.to_dict()
        }), 201
        
    except KeyError as e:
        return jsonify({
            'success': False,
            'message': f'Missing required field: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Failed to add document: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to add document'
        }), 500

@personal_bp.route('/kb/<int:kb_id>/documents/<string:document_id>', methods=['PATCH'])
@jwt_required()
@user_required
def update_document(kb_id, document_id):
    """Update document metadata"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Verify ownership
        kb = KBService.get_knowledge_base(kb_id, user_id)
        if not kb:
            return jsonify({
                'success': False,
                'message': 'Knowledge base not found'
            }), 404
        
        # Get document
        document = KBService.get_document(kb_id, document_id)
        if not document:
            return jsonify({
                'success': False,
                'message': 'Document not found'
            }), 404
        
        # Update metadata
        updated_doc = KBService.update_document_metadata(document, data)
        
        return jsonify({
            'success': True,
            'message': 'Document updated successfully',
            'data': updated_doc.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to update document: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update document'
        }), 500

@personal_bp.route('/kb/<int:kb_id>/documents/<string:document_id>/related', methods=['POST'])
@jwt_required()
@user_required
def add_related_documents(kb_id, document_id):
    """Add related documents"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Verify ownership
        kb = KBService.get_knowledge_base(kb_id, user_id)
        if not kb:
            return jsonify({
                'success': False,
                'message': 'Knowledge base not found'
            }), 404
        
        # Get document
        document = KBService.get_document(kb_id, document_id)
        if not document:
            return jsonify({
                'success': False,
                'message': 'Document not found'
            }), 404
        
        # Add related documents
        KBService.add_related_documents(
            document=document,
            related_ids=data['document_ids'],
            relation_type=data.get('relation_type', 'related')
        )
        
        return jsonify({
            'success': True,
            'message': 'Related documents added successfully',
            'data': KBService.get_related_documents(document)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to add related documents: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to add related documents'
        }), 500

@personal_bp.route('/kb/<int:kb_id>/documents/<string:document_id>/related/<string:related_id>', methods=['DELETE'])
@jwt_required()
@user_required
def remove_related_document(kb_id, document_id, related_id):
    """Remove a related document"""
    try:
        user_id = get_jwt_identity()
        
        # Verify ownership
        kb = KBService.get_knowledge_base(kb_id, user_id)
        if not kb:
            return jsonify({
                'success': False,
                'message': 'Knowledge base not found'
            }), 404
        
        # Get document
        document = KBService.get_document(kb_id, document_id)
        if not document:
            return jsonify({
                'success': False,
                'message': 'Document not found'
            }), 404
        
        # Remove related document
        KBService.remove_related_document(document, related_id)
        
        return jsonify({
            'success': True,
            'message': 'Related document removed successfully',
            'data': KBService.get_related_documents(document)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to remove related document: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to remove related document'
        }), 500 