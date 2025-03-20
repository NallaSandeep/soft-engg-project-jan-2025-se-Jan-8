import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Button,
    IconButton,
    Menu,
    MenuItem,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField
} from '@mui/material';
import {
    Add as AddIcon,
    MoreVert as MoreVertIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Folder as FolderIcon
} from '@mui/icons-material';
import resourceService from '../../services/resourceService';

const ResourceList = ({ courseId }) => {
    const [resources, setResources] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [anchorEl, setAnchorEl] = useState(null);
    const [selectedResource, setSelectedResource] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [newResource, setNewResource] = useState({
        name: '',
        description: '',
        course_id: courseId
    });

    useEffect(() => {
        fetchResources();
    }, [courseId]);

    const fetchResources = async () => {
        try {
            setLoading(true);
            const data = await resourceService.getResources(courseId);
            setResources(data);
        } catch (err) {
            setError('Failed to fetch resources');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleMenuClick = (event, resource) => {
        setAnchorEl(event.currentTarget);
        setSelectedResource(resource);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedResource(null);
    };

    const handleDelete = async () => {
        if (!selectedResource) return;
        
        try {
            await resourceService.deleteResource(selectedResource.id);
            setResources(resources.filter(r => r.id !== selectedResource.id));
        } catch (err) {
            console.error('Failed to delete resource:', err);
        }
        handleMenuClose();
    };

    const handleCreateResource = async () => {
        try {
            const resource = await resourceService.createResource(newResource);
            setResources([...resources, resource]);
            setOpenDialog(false);
            setNewResource({ name: '', description: '', course_id: courseId });
        } catch (err) {
            console.error('Failed to create resource:', err);
        }
    };

    if (loading) return <Typography>Loading...</Typography>;
    if (error) return <Typography color="error">{error}</Typography>;

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Personal Resources</Typography>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => setOpenDialog(true)}
                >
                    New Resource
                </Button>
            </Box>

            <Grid container spacing={3}>
                {resources.map((resource) => (
                    <Grid item xs={12} sm={6} md={4} key={resource.id}>
                        <Card>
                            <CardContent>
                                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                                    <Box>
                                        <Typography variant="h6" component={Link} to={`/resources/${resource.id}`}>
                                            {resource.name}
                                        </Typography>
                                        <Typography color="textSecondary" gutterBottom>
                                            {resource.course?.name}
                                        </Typography>
                                        <Typography variant="body2" color="textSecondary">
                                            {resource.description || 'No description'}
                                        </Typography>
                                    </Box>
                                    <IconButton onClick={(e) => handleMenuClick(e, resource)}>
                                        <MoreVertIcon />
                                    </IconButton>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
            >
                <MenuItem component={Link} to={`/resources/${selectedResource?.id}/edit`}>
                    <EditIcon /> Edit
                </MenuItem>
                <MenuItem onClick={handleDelete}>
                    <DeleteIcon /> Delete
                </MenuItem>
            </Menu>

            <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
                <DialogTitle>Create New Resource</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Name"
                        fullWidth
                        value={newResource.name}
                        onChange={(e) => setNewResource({ ...newResource, name: e.target.value })}
                    />
                    <TextField
                        margin="dense"
                        label="Description"
                        fullWidth
                        multiline
                        rows={4}
                        value={newResource.description}
                        onChange={(e) => setNewResource({ ...newResource, description: e.target.value })}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
                    <Button onClick={handleCreateResource} color="primary">
                        Create
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ResourceList; 