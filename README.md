# RPI Application

A full-stack application consisting of a FastAPI backend and Next.js frontend for file management and chat functionality.

## Project Structure

```
rpi/
├── backend/            # FastAPI backend application
│   ├── src/           # Source code
│   ├── Dockerfile     # Backend Docker configuration
│   └── ...
├── frontend/          # Next.js frontend application
│   ├── src/           # Source code
│   ├── Dockerfile     # Frontend Docker configuration
│   └── ...
├── nginx/             # Nginx configuration
├── compose.dev.yaml   # Development Docker Compose
├── compose.yaml       # Production Docker Compose
└── dev.sh            # Backend development script
```

## Features

### Backend (FastAPI)
- JWT-based authentication with access codes
- File upload API (Markdown, Images, PDFs)
- File management with search and pagination
- Database integration with PostgreSQL
- Comprehensive logging and error handling

### Frontend (Next.js)
- Access code authentication with secure token storage
- Home page with chat interface
- Drag-and-drop file upload
- File browser with search and filtering
- File viewing and deletion
- Responsive design with Tailwind CSS

## Quick Start

### Development with Docker

1. Start the full application stack:
   ```bash
   docker-compose -f compose.dev.yaml up
   ```

2. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Local Development

#### Backend
```bash
cd backend
./dev.sh  # Requires uv package manager
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Authentication

The application uses access code authentication:

1. Navigate to http://localhost:3000
2. You'll be redirected to the login page
3. Enter the access code (configured in backend environment)
4. Upon successful authentication, you'll receive a JWT token
5. The token is stored securely and used for all API requests

## Usage

### File Upload
1. Navigate to the "Upload" page
2. Drag and drop files or click to select
3. Supported formats: Markdown (.md), Images (.png, .jpg, etc.), PDFs (.pdf)
4. Files are processed and stored with metadata extraction

### File Management
1. Navigate to the "Files" page
2. Browse uploaded files with pagination
3. Search by filename or content
4. Filter by file type
5. View file details in a modal
6. Delete files as needed

### Chat Interface
1. The home page features a demo chat interface
2. Currently shows a mock conversation
3. Ready for integration with AI services

## Environment Configuration

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
ACCESS_CODE=your-access-code
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Scripts

- `./dev.sh` - Start backend development server
- `./dev-frontend.sh` - Start frontend development server
- `docker-compose -f compose.dev.yaml up` - Start full stack

## Docker Configuration

The application includes Docker configurations for both development and production:

- **Development**: `compose.dev.yaml` with hot reloading
- **Production**: `compose.yaml` with optimized builds
- **Nginx**: Reverse proxy configuration for production

## API Endpoints

### Authentication
- `POST /auth/login` - Login with access code

### File Management
- `GET /files/` - List files with pagination
- `GET /files/{id}` - Get file details
- `DELETE /files/{id}` - Delete file
- `POST /files/search` - Search files

### File Upload
- `POST /upload/md` - Upload markdown file
- `POST /upload/image` - Upload image file
- `POST /upload/pdf` - Upload PDF file
- `POST /upload/bulk` - Bulk file upload

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **File Processing**: Pillow (images), PyPDF2 (PDFs)
- **Validation**: Pydantic
- **Package Management**: uv

### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **HTTP Client**: Axios
- **File Upload**: React Dropzone
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Development**: Hot reloading for both frontend and backend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]
