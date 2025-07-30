import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  status: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
}

export interface AnalysisRegion {
  x: number;
  y: number;
  width: number;
  height: number;
  severity: number;
  issue_type: string;
  confidence: number;
}

export interface AnalysisResult {
  project_id: string;
  overall_score: number;
  issues_detected: number;
  analysis_time: string;
  processing_duration: number;
  color_analysis: any;
  coverage_analysis: any;
  texture_analysis: any;
  problem_regions: AnalysisRegion[];
  recommendations: string[];
  visualization_path?: string;
  status: string;
  error?: string;
}

export const apiService = {
  // Project management
  async createProject(project: ProjectCreate): Promise<Project> {
    const response = await api.post('/api/projects', project);
    return response.data;
  },

  async getProjects(): Promise<{ projects: Project[] }> {
    const response = await api.get('/api/projects');
    return response.data;
  },

  // Image upload
  async uploadBeforeImage(projectId: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(
      `/api/projects/${projectId}/upload-before`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  async uploadAfterImage(projectId: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(
      `/api/projects/${projectId}/upload-after`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Analysis
  async analyzeProject(projectId: string): Promise<AnalysisResult> {
    const response = await api.post(`/api/projects/${projectId}/analyze`);
    return response.data;
  },

  async getAnalysisResults(projectId: string): Promise<AnalysisResult> {
    const response = await api.get(`/api/projects/${projectId}/results`);
    return response.data;
  },

  // Utility function to get image URL
  getImageUrl(path: string): string {
    if (path.startsWith('http')) {
      return path;
    }
    return `${API_BASE_URL}/${path}`;
  },
};

export default apiService;