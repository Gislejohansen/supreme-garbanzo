import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  IconButton,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Divider,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Lightbulb as LightbulbIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import apiService, { AnalysisResult, AnalysisRegion } from '../services/api';

const ResultsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      loadResults();
    }
  }, [projectId]);

  const loadResults = async () => {
    if (!projectId) return;

    try {
      setLoading(true);
      setError(null);
      const analysisResults = await apiService.getAnalysisResults(projectId);
      setResults(analysisResults);
    } catch (err) {
      setError('Failed to load analysis results');
      console.error('Error loading results:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#4caf50'; // Green
    if (score >= 60) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const getScoreLevel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  const getSeverityIcon = (severity: number) => {
    if (severity < 0.3) return <CheckCircleIcon color="success" />;
    if (severity < 0.7) return <WarningIcon color="warning" />;
    return <ErrorIcon color="error" />;
  };

  const getSeverityLabel = (severity: number) => {
    if (severity < 0.3) return 'Minor';
    if (severity < 0.7) return 'Moderate';
    return 'Severe';
  };

  const getSeverityColor = (severity: number) => {
    if (severity < 0.3) return 'success';
    if (severity < 0.7) return 'warning';
    return 'error';
  };

  const formatIssueType = (issueType: string) => {
    return issueType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)} seconds`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  };

  // Chart data
  const issueTypeData = results?.problem_regions.reduce((acc: any[], region: AnalysisRegion) => {
    const existingType = acc.find(item => item.name === formatIssueType(region.issue_type));
    if (existingType) {
      existingType.value += 1;
    } else {
      acc.push({ name: formatIssueType(region.issue_type), value: 1 });
    }
    return acc;
  }, []) || [];

  const severityData = results?.problem_regions.reduce((acc: any[], region: AnalysisRegion) => {
    const severity = getSeverityLabel(region.severity);
    const existing = acc.find(item => item.name === severity);
    if (existing) {
      existing.value += 1;
    } else {
      acc.push({ name: severity, value: 1 });
    }
    return acc;
  }, []) || [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading analysis results...
        </Typography>
      </Box>
    );
  }

  if (error || !results) {
    return (
      <Box>
        <Box display="flex" alignItems="center" mb={4}>
          <IconButton onClick={() => navigate('/')} sx={{ mr: 2 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1">
            Analysis Results
          </Typography>
        </Box>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={loadResults}>
            <RefreshIcon sx={{ mr: 1 }} />
            Retry
          </Button>
        }>
          {error || 'No results available'}
        </Alert>
      </Box>
    );
  }

  if (results.status === 'error') {
    return (
      <Box>
        <Box display="flex" alignItems="center" mb={4}>
          <IconButton onClick={() => navigate('/')} sx={{ mr: 2 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1">
            Analysis Results
          </Typography>
        </Box>
        <Alert severity="error">
          Analysis failed: {results.error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={4}>
        <Box display="flex" alignItems="center">
          <IconButton onClick={() => navigate('/')} sx={{ mr: 2 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1">
            Analysis Results
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={() => window.print()}
        >
          Export Report
        </Button>
      </Box>

      {/* Overall Score */}
      <Card className="analysis-card" sx={{ mb: 4 }}>
        <CardContent sx={{ textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Overall Paint Quality Score
          </Typography>
          <Box 
            className="score-display"
            sx={{ 
              backgroundColor: getScoreColor(results.overall_score),
              color: 'white',
              borderRadius: 2,
              p: 3,
              mb: 2
            }}
          >
            <Typography variant="h2" component="div">
              {results.overall_score.toFixed(1)}
            </Typography>
            <Typography variant="h6">
              {getScoreLevel(results.overall_score)}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Analysis completed in {formatDuration(results.processing_duration)}
          </Typography>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <AssessmentIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" color="primary">
                {results.issues_detected}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Issues Detected
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Color Consistency
              </Typography>
              <Typography variant="h4" color={results.color_analysis.change_percentage > 15 ? 'error' : 'success'}>
                {(100 - results.color_analysis.change_percentage).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Uniform Coverage
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Texture Quality
              </Typography>
              <Typography variant="h4" color={results.texture_analysis.texture_consistency_score > 0.7 ? 'success' : 'error'}>
                {(results.texture_analysis.texture_consistency_score * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Consistency Score
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      {results.problem_regions.length > 0 && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Issues by Type
                </Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={issueTypeData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={(entry) => entry.name}
                    >
                      {issueTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Issues by Severity
                </Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={severityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Problem Regions */}
      {results.problem_regions.length > 0 && (
        <Card className="analysis-card" sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Detected Issues
            </Typography>
            <Grid container spacing={2}>
              {results.problem_regions.map((region, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Paper sx={{ p: 2, border: 1, borderColor: 'divider' }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                      <Typography variant="subtitle1">
                        Issue #{index + 1}
                      </Typography>
                      <Chip
                        icon={getSeverityIcon(region.severity)}
                        label={getSeverityLabel(region.severity)}
                        color={getSeverityColor(region.severity) as any}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Type: {formatIssueType(region.issue_type)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Location: ({region.x}, {region.y}) - {region.width}x{region.height}px
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Confidence: {(region.confidence * 100).toFixed(1)}%
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      <Card className="analysis-card" sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <LightbulbIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Recommendations
          </Typography>
          <List>
            {results.recommendations.map((recommendation, index) => (
              <ListItem key={index} sx={{ pl: 0 }}>
                <ListItemIcon>
                  <CheckCircleIcon color="primary" />
                </ListItemIcon>
                <ListItemText primary={recommendation} />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Technical Details */}
      <Card className="analysis-card">
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Technical Analysis Details
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Color Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Mean Color Difference: {results.color_analysis.mean_color_difference?.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Color Change: {results.color_analysis.change_percentage?.toFixed(1)}%
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Coverage Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Mean Intensity Change: {results.coverage_analysis.mean_intensity_change?.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Poor Coverage: {results.coverage_analysis.poor_coverage_percentage?.toFixed(1)}%
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Texture Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Consistency Score: {(results.texture_analysis.texture_consistency_score * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Mean Difference: {results.texture_analysis.mean_texture_difference?.toFixed(2)}
              </Typography>
            </Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Analysis completed on {new Date(results.analysis_time).toLocaleString()}
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ResultsPage;