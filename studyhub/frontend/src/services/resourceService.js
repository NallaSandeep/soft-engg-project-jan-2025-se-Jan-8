import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';

class ResourceService {
    constructor() {
        this.baseUrl = `${API_URL}/personal-resources`;
    }

    async getResources(courseId = null) {
        try {
            const url = courseId ? `${this.baseUrl}?course_id=${courseId}` : this.baseUrl;
            const response = await axios.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching resources:', error);
            throw error;
        }
    }

    async getResource(resourceId) {
        try {
            const response = await axios.get(`${this.baseUrl}/${resourceId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching resource:', error);
            throw error;
        }
    }

    async createResource(data) {
        try {
            const response = await axios.post(this.baseUrl, data);
            return response.data;
        } catch (error) {
            console.error('Error creating resource:', error);
            throw error;
        }
    }

    async updateResource(resourceId, data) {
        try {
            const response = await axios.put(`${this.baseUrl}/${resourceId}`, data);
            return response.data;
        } catch (error) {
            console.error('Error updating resource:', error);
            throw error;
        }
    }

    async deleteResource(resourceId) {
        try {
            await axios.delete(`${this.baseUrl}/${resourceId}`);
        } catch (error) {
            console.error('Error deleting resource:', error);
            throw error;
        }
    }

    async getResourceFiles(resourceId) {
        try {
            const response = await axios.get(`${this.baseUrl}/${resourceId}/files`);
            return response.data;
        } catch (error) {
            console.error('Error fetching resource files:', error);
            throw error;
        }
    }

    async addFile(resourceId, fileData) {
        try {
            const formData = new FormData();
            if (fileData instanceof File) {
                formData.append('file', fileData);
            } else {
                formData.append('file', JSON.stringify(fileData));
            }
            
            const response = await axios.post(
                `${this.baseUrl}/${resourceId}/files`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Error adding file:', error);
            throw error;
        }
    }

    async deleteFile(resourceId, fileId) {
        try {
            await axios.delete(`${this.baseUrl}/${resourceId}/files/${fileId}`);
        } catch (error) {
            console.error('Error deleting file:', error);
            throw error;
        }
    }
}

export default new ResourceService(); 