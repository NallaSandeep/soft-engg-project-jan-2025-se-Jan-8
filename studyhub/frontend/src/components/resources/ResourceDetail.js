import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Box,
    Paper,
    Typography,
    Button,
    IconButton,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Grid,
    CircularProgress,
    Alert
} from '@mui/material';
import {
    Edit as EditIcon,
    Delete as DeleteIcon,
    ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import resourceService from '../../services/resourceService';
import ResourceFileManager from './ResourceFileManager';

const ResourceDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [resource, setResource] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [editedResource, setEditedResource] = useState(null);
    const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
    const [files, setFiles] = useState([]);

    useEffect(() => {
        fetchResource();
        fetchFiles();
    }, [id]);

    const fetchResource = async () => {
        try {
            setLoading(true);
            const data = await resourceService.getResource(id);
            setResource(data);
            setEditedResource(data);
        } catch (err) {
            setError('Failed to fetch resource details');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchFiles = async () => {
        try {
            const data = await resourceService.getResourceFiles(id);
            setFiles(data);
        } catch (err) {
            console.error('Failed to fetch resource files:', err);
        }
    };

    const handleEdit = () => {
        setEditMode(true);
    };

    const handleSave = async () => {
        try {
            const updatedResource = await resourceService.updateResource(id, editedResource);
            setResource(updatedResource);
            setEditMode(false);
        } catch (err) {
            console.error('Failed to update resource:', err);
        }
    };

    const handleCancel = () => {
        setEditedResource(resource);
        setEditMode(false);
    };

    const handleDelete = async () => {
        try {
            await resourceService.deleteResource(id);
            navigate('/resources');
        } catch (err) {
            console.error('Failed to delete resource:', err);
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box p={3}>
                <Alert severity="error">{error}</Alert>
            </Box>
        );
    }

    return (
        <Box>
            <Box display="flex" alignItems="center" mb={3}>
                <IconButton onClick={() => navigate('/resources')} sx={{ mr: 2 }}>
                    <ArrowBackIcon />
                </IconButton>
                <Typography variant="h5" component="h1">
                    {resource.name}
                </Typography>
                <Box ml="auto">
                    <IconButton onClick={handleEdit} color="primary">
                        <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => setOpenDeleteDialog(true)} color="error">
                        <DeleteIcon />
                    </IconButton>
                </Box>
            </Box>

            <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 3 }}>
                        {editMode ? (
                            <>
                                <TextField
                                    fullWidth
                                    label="Name"
                                    value={editedResource.name}
                                    onChange={(e) => setEditedResource({ ...editedResource, name: e.target.value })}
                                    margin="normal"
                                />
                                <TextField
                                    fullWidth
                                    label="Description"
                                    value={editedResource.description}
                                    onChange={(e) => setEditedResource({ ...editedResource, description: e.target.value })}
                                    margin="normal"
                                    multiline
                                    rows={4}
                                />
                                <Box mt={2} display="flex" justifyContent="flex-end" gap={1}>
                                    <Button onClick={handleCancel}>Cancel</Button>
                                    <Button variant="contained" onClick={handleSave}>
                                        Save
                                    </Button>
                                </Box>
                            </>
                        ) : (
                            <>
                                <Typography variant="subtitle1" color="textSecondary" gutterBottom>
                                    {resource.course?.name}
                                </Typography>
                                <Typography variant="body1" paragraph>
                                    {resource.description || 'No description provided'}
                                </Typography>
                            </>
                        )}
                    </Paper>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3 }}>
                        <ResourceFileManager
                            resourceId={id}
                            files={files}
                            onFilesUpdate={setFiles}
                        />
                    </Paper>
                </Grid>
            </Grid>

            <Dialog open={openDeleteDialog} onClose={() => setOpenDeleteDialog(false)}>
                <DialogTitle>Delete Resource</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete this resource? This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
                    <Button onClick={handleDelete} color="error">
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ResourceDetail; 