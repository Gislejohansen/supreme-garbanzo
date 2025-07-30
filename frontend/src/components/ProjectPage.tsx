import React, { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Paper,
  IconButton,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  Analytics as AnalyticsIcon,
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import apiService from '../services/api';

const ProjectPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [beforeImage, setBeforeImage] = useState<File | null>(null);
  const [afterImage, setAfterImage] = useState<File | null>(null);
  const [beforeImageUrl, setBeforeImageUrl] = useState<string | null>(null);
  const [afterImageUrl, setAfterImageUrl] = useState<string | null>(null);
  
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [activeStep, setActiveStep] = useState(0);

  const steps = ['Upload Before Image', 'Upload After Image', 'Analyze Paint Quality'];

  const onBeforeImageDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setBeforeImage(file);
      setBeforeImageUrl(URL.createObjectURL(file));
      setError(null);
    }
  }, []);

  const onAfterImageDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setAfterImage(file);
      setAfterImageUrl(URL.createObjectURL(file));
      setError(null);
    }
  }, []);

  const {
    getRootProps: getBeforeRootProps,
    getInputProps: getBeforeInputProps,
    isDragActive: isBeforeDragActive,
  } = useDropzone({
    onDrop: onBeforeImageDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
  });

  const {
    getRootProps: getAfterRootProps,
    getInputProps: getAfterInputProps,
    isDragActive: isAfterDragActive,
  } = useDropzone({
    onDrop: onAfterImageDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
  });

  const uploadBeforeImage = async () => {
    if (!beforeImage || !projectId) return;

    try {
      setUploading(true);
      setError(null);
      await apiService.uploadBeforeImage(projectId, beforeImage);
      setSuccess('Before image uploaded successfully!');
      setActiveStep(1);
    } catch (err) {
      setError('Failed to upload before image');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const uploadAfterImage = async () => {
    if (!afterImage || !projectId) return;

    try {
      setUploading(true);
      setError(null);
      await apiService.uploadAfterImage(projectId, afterImage);
      setSuccess('After image uploaded successfully!');
      setActiveStep(2);
    } catch (err) {
      setError('Failed to upload after image');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const startAnalysis = async () => {
    if (!projectId) return;

    try {
      setAnalyzing(true);
      setError(null);
      await apiService.analyzeProject(projectId);
      setSuccess('Analysis completed successfully!');
      navigate(`/results/${projectId}`);
    } catch (err) {
      setError('Failed to analyze project');
      console.error('Analysis error:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const removeBeforeImage = () => {
    setBeforeImage(null);
    setBeforeImageUrl(null);
    if (activeStep > 0) setActiveStep(0);
  };

  const removeAfterImage = () => {
    setAfterImage(null);
    setAfterImageUrl(null);
    if (activeStep > 1) setActiveStep(1);
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={4}>
        <IconButton onClick={() => navigate('/')} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          Paint Analysis Project
        </Typography>
      </Box>

      {/* Progress Stepper */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label, index) => (
            <Step key={label} completed={activeStep > index}>
              <StepLabel>
                {activeStep > index && <CheckCircleIcon color="success" sx={{ mr: 1 }} />}
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Error and Success Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      {/* Upload Sections */}
      <Grid container spacing={4}>
        {/* Before Image Section */}
        <Grid item xs={12} md={6}>
          <Card className="analysis-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Before Image
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Upload a photo taken before painting
              </Typography>

              {!beforeImageUrl ? (
                <Box
                  {...getBeforeRootProps()}
                  className={`upload-zone ${isBeforeDragActive ? 'dragover' : ''}`}
                  sx={{ mb: 2 }}
                >
                  <input {...getBeforeInputProps()} />
                  <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="body1" gutterBottom>
                    {isBeforeDragActive
                      ? 'Drop the image here...'
                      : 'Drag & drop an image here, or click to select'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supports JPG, PNG, WebP
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ position: 'relative', mb: 2 }}>
                  <img
                    src={beforeImageUrl}
                    alt="Before painting"
                    className="image-preview"
                    style={{ width: '100%', height: 'auto' }}
                  />
                  <IconButton
                    onClick={removeBeforeImage}
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      backgroundColor: 'rgba(255,255,255,0.8)',
                      '&:hover': { backgroundColor: 'rgba(255,255,255,0.9)' }
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              )}

              {beforeImage && activeStep === 0 && (
                <Button
                  variant="contained"
                  fullWidth
                  onClick={uploadBeforeImage}
                  disabled={uploading}
                  startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
                >
                  {uploading ? 'Uploading...' : 'Upload Before Image'}
                </Button>
              )}

              {activeStep > 0 && (
                <Alert severity="success" icon={<CheckCircleIcon />}>
                  Before image uploaded successfully
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* After Image Section */}
        <Grid item xs={12} md={6}>
          <Card className="analysis-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                After Image
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Upload a photo taken after painting
              </Typography>

              {!afterImageUrl ? (
                <Box
                  {...getAfterRootProps()}
                  className={`upload-zone ${isAfterDragActive ? 'dragover' : ''}`}
                  sx={{ mb: 2 }}
                >
                  <input {...getAfterInputProps()} />
                  <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="body1" gutterBottom>
                    {isAfterDragActive
                      ? 'Drop the image here...'
                      : 'Drag & drop an image here, or click to select'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supports JPG, PNG, WebP
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ position: 'relative', mb: 2 }}>
                  <img
                    src={afterImageUrl}
                    alt="After painting"
                    className="image-preview"
                    style={{ width: '100%', height: 'auto' }}
                  />
                  <IconButton
                    onClick={removeAfterImage}
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      backgroundColor: 'rgba(255,255,255,0.8)',
                      '&:hover': { backgroundColor: 'rgba(255,255,255,0.9)' }
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              )}

              {afterImage && activeStep === 1 && (
                <Button
                  variant="contained"
                  fullWidth
                  onClick={uploadAfterImage}
                  disabled={uploading || activeStep < 1}
                  startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
                >
                  {uploading ? 'Uploading...' : 'Upload After Image'}
                </Button>
              )}

              {activeStep > 1 && (
                <Alert severity="success" icon={<CheckCircleIcon />}>
                  After image uploaded successfully
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Analysis Section */}
      {activeStep >= 2 && (
        <Card className="analysis-card" sx={{ mt: 4 }}>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <AnalyticsIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Ready for Analysis
            </Typography>
            <Typography variant="body1" color="text.secondary" mb={4}>
              Both images have been uploaded. Click the button below to start the AI-powered paint quality analysis.
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={startAnalysis}
              disabled={analyzing}
              startIcon={analyzing ? <CircularProgress size={20} /> : <AnalyticsIcon />}
            >
              {analyzing ? 'Analyzing...' : 'Start Analysis'}
            </Button>
            {analyzing && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                This may take a few moments...
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card sx={{ mt: 4, backgroundColor: 'background.default' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Tips for Best Results
          </Typography>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            <li>Take photos from the same angle and distance</li>
            <li>Ensure good lighting conditions</li>
            <li>Include the entire painted surface in both photos</li>
            <li>Avoid shadows or reflections</li>
            <li>Use high-resolution images for better analysis</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ProjectPage;