# RPI Frontend

A Next.js frontend application for the RPI file management and chat system.

## Features

- **Authentication**: Access code-based login with JWT token management
- **Chat Interface**: Home page with a demo chat interface for AI interactions
- **File Upload**: Drag-and-drop file upload supporting:
  - Markdown files (.md)
  - Images (.png, .jpg, .jpeg, .gif, .webp)
  - PDF files (.pdf)
- **File Management**: Browse, search, view, and delete uploaded files
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **HTTP Client**: Axios
- **Authentication**: JWT tokens stored in secure cookies
- **File Handling**: React Dropzone for drag-and-drop uploads
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18 or later
- npm

### Local Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your API URL
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Docker Development

The frontend can be run with Docker using the provided docker-compose configuration:

```bash
# From the project root
docker-compose -f compose.dev.yaml up frontend
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Project Structure

```
src/
├── app/                 # Next.js App Router pages
│   ├── files/          # File management page
│   ├── login/          # Authentication page
│   ├── upload/         # File upload page
│   └── page.tsx        # Home page with chat
├── components/         # Reusable React components
│   ├── AuthGuard.tsx   # Authentication protection
│   ├── ConditionalLayout.tsx  # Layout wrapper
│   └── Navigation.tsx  # Navigation bar
└── lib/               # Utilities and services
    ├── api.ts         # API client and types
    └── auth.ts        # Authentication service
```

## Authentication Flow

1. User enters access code on login page
2. Frontend sends POST request to `/auth/login`
3. Backend validates access code and returns JWT token
4. Token is stored in secure HTTP-only cookie
5. All subsequent API requests include the token in Authorization header
6. AuthGuard component protects routes and redirects to login if unauthorized

## API Integration

The frontend communicates with the backend through REST API endpoints:

- `POST /auth/login` - Authentication
- `GET /files/` - List files with pagination and filtering
- `GET /files/{id}` - Get file details
- `DELETE /files/{id}` - Delete file
- `POST /files/search` - Search files
- `POST /upload/md` - Upload markdown file
- `POST /upload/image` - Upload image file
- `POST /upload/pdf` - Upload PDF file
- `POST /upload/bulk` - Bulk file upload

## Development Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build production bundle
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Building for Production

```bash
npm run build
npm run start
```

## Docker Deployment

The application includes a Dockerfile for containerized deployment:

```bash
docker build -t rpi-frontend .
docker run -p 3000:3000 rpi-frontend
```