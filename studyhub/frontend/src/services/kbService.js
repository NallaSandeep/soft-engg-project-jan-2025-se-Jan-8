import { personalApi } from './apiService';

// Re-export the personal API methods for Knowledge Base
export const kbApi = {
    // Knowledge Base Management
    getKnowledgeBases: () => personalApi.getKnowledgeBases(),
    createKnowledgeBase: (data) => personalApi.createKnowledgeBase(data),
    getFolderStructure: (kbId) => personalApi.getFolderStructure(kbId),
    createFolder: (kbId, data) => personalApi.createFolder(kbId, data),

    // Document Management
    addDocument: (kbId, data) => personalApi.addDocument(kbId, data),
    updateDocument: (kbId, documentId, data) => personalApi.updateDocument(kbId, documentId, data),
    addRelatedDocuments: (kbId, documentId, data) => personalApi.addRelatedDocuments(kbId, documentId, data),
    removeRelatedDocument: (kbId, documentId, relatedId) => personalApi.removeRelatedDocument(kbId, documentId, relatedId),

    // StudyIndexer Integration
    searchPersonalDocuments: (data) => personalApi.searchPersonalDocuments(data),
    updateIndexerMetadata: (documentId, data) => personalApi.updateIndexerMetadata(documentId, data),
    getRelatedDocuments: (documentId, limit = 5) => personalApi.getRelatedDocuments(documentId, limit)
};

export default kbApi; 