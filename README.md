# Paint Quality Analysis App

An AI-powered application that analyzes painting quality by comparing before and after photos of homes (interior and exterior) to detect areas where painting is unequal or inconsistent.

## 🚀 Features

- **📸 Image Upload**: Drag-and-drop interface for before and after photos
- **🤖 AI Analysis**: Advanced computer vision models detect paint inconsistencies
- **📊 Visual Reports**: Interactive charts and highlighted problem areas
- **🎯 Problem Detection**: Identifies uneven coverage, color inconsistencies, and texture variations
- **💡 Smart Recommendations**: Actionable suggestions for paint quality improvement
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🐳 Docker Ready**: Complete containerization for easy deployment

## 🛠 Technology Stack

- **Backend**: Python FastAPI + OpenCV + scikit-image
- **Frontend**: React + TypeScript + Material-UI
- **AI/ML**: Computer vision with color, texture, and coverage analysis
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Docker + Docker Compose

## 🚀 Quick Start

### Option 1: One-Click Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd paint-quality-analysis

# Run the application
./run.sh
```

This will automatically:
- Check for Docker dependencies
- Build the application
- Start all services
- Display access URLs

### Option 2: Manual Setup

#### Prerequisites

- Python 3.9+ 
- Node.js 16+
- Docker & Docker Compose (optional)

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python main.py
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

#### Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Stop services
docker-compose down
```

## 📖 How to Use

### 1. Create a Project
- Visit `http://localhost:3000`
- Click "Start New Analysis"
- Enter a project name and description

### 2. Upload Images
- Upload a "before" photo taken prior to painting
- Upload an "after" photo taken after painting
- Ensure photos are taken from similar angles

### 3. Run Analysis
- Click "Start Analysis" once both images are uploaded
- The AI will process images and detect quality issues
- View detailed results with visual overlays

### 4. Review Results
- Overall quality score (0-100)
- Problem regions highlighted on images
- Detailed recommendations for improvement
- Export report for reference

## 🔍 Analysis Features

### Color Analysis
- Detects color inconsistencies across painted surfaces
- Measures color uniformity and coverage
- Identifies areas with different paint colors

### Coverage Analysis  
- Analyzes paint coverage quality
- Detects areas with insufficient paint application
- Measures surface preparation effectiveness

### Texture Analysis
- Evaluates paint texture consistency
- Identifies brush marks, roller patterns, or spray inconsistencies
- Detects surface preparation issues

### Problem Classification
- **Uneven Coverage**: Areas with insufficient paint
- **Color Inconsistency**: Variations in paint color
- **Over Application**: Areas with too much paint
- **Texture Variation**: Inconsistent surface texture

## 📊 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

- `POST /api/projects` - Create new project
- `POST /api/projects/{id}/upload-before` - Upload before image
- `POST /api/projects/{id}/upload-after` - Upload after image
- `POST /api/projects/{id}/analyze` - Start analysis
- `GET /api/projects/{id}/results` - Get analysis results

## 🏗 Project Structure

```
paint-quality-analysis/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main application file
│   ├── models.py           # Data models and database
│   └── services/           # Analysis services
│       ├── image_processor.py
│       └── paint_analyzer.py
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service
│   │   └── App.tsx         # Main app component
│   └── package.json
├── docker-compose.yml      # Docker orchestration
├── Dockerfile.backend      # Backend container
├── Dockerfile.frontend     # Frontend container
└── run.sh                 # Quick start script
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Backend
DATABASE_URL=sqlite:///./paint_analysis.db
PYTHONPATH=/app

# Frontend  
REACT_APP_API_URL=http://localhost:8000
```

### Production Configuration

For production deployment:

1. Use PostgreSQL database
2. Configure cloud storage (AWS S3, etc.)
3. Set up HTTPS with reverse proxy
4. Enable Redis for caching
5. Configure monitoring and logging

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
pip install -r requirements-dev.txt
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python formatting
black backend/
flake8 backend/

# TypeScript checking
cd frontend
npm run type-check
```

## 📸 Screenshots

### Home Page
- Clean interface with project management
- Feature overview and getting started guide

### Project Upload
- Drag-and-drop image upload
- Progress tracking with visual steps
- Real-time image previews

### Analysis Results
- Overall quality score display
- Interactive charts and visualizations
- Detailed problem region analysis
- Actionable recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

### For Images
- Supported formats: JPG, PNG, WebP
- Recommended resolution: 1920x1080 or higher
- Take photos from similar angles and distances
- Ensure good lighting conditions
- Avoid shadows and reflections

### System Requirements
- **Development**: 4GB RAM, 10GB disk space
- **Production**: 8GB RAM, 50GB disk space
- **Docker**: Docker 20.10+, Docker Compose 2.0+

## 🔒 Security

- Images are processed locally (no external API calls)
- File uploads are validated and sanitized
- SQL injection protection with SQLAlchemy
- CORS configuration for frontend access
- Security headers in Nginx configuration

## 📈 Performance

- Supports images up to 50MB
- Analysis typically completes in 10-30 seconds
- Parallel processing for multiple regions
- Optimized OpenCV operations
- Efficient React rendering with Material-UI

## 🐛 Troubleshooting

### Common Issues

1. **Docker build fails**: Ensure Docker is running and has sufficient memory
2. **Frontend won't load**: Check if backend is running on port 8000
3. **Analysis takes too long**: Reduce image size or check system resources
4. **Upload fails**: Verify file format and size limits

### Getting Help

- Check the logs: `docker-compose logs`
- Verify services: `docker-compose ps`
- Restart services: `docker-compose restart`

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Built with ❤️ for better paint quality analysis**
