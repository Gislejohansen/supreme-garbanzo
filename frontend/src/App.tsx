import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material';
import { PaletteOutlined } from '@mui/icons-material';
import HomePage from './components/HomePage';
import ProjectPage from './components/ProjectPage';
import ResultsPage from './components/ResultsPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <AppBar position="static" sx={{ mb: 4 }}>
          <Toolbar>
            <PaletteOutlined sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Paint Quality Analysis
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="lg">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/project/:projectId" element={<ProjectPage />} />
            <Route path="/results/:projectId" element={<ResultsPage />} />
          </Routes>
        </Container>

        <Box 
          component="footer" 
          sx={{ 
            mt: 8, 
            py: 3, 
            px: 2, 
            backgroundColor: 'primary.main',
            color: 'white',
            textAlign: 'center'
          }}
        >
          <Typography variant="body2">
            AI-Powered Paint Quality Analysis © 2024
          </Typography>
        </Box>
      </div>
    </Router>
  );
}

export default App;