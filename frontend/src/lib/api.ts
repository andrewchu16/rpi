import axios, { AxiosResponse } from 'axios';
import {
  FileInfo,
  FileListResponse,
  UploadResponse,
  BulkUploadResponse
} from '@/models/file';

// Create axios instance for server routes
const api = axios.create({
  baseURL: '/api',
});

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on auth error
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions
export const apiService = {
  // File operations
  async listFiles(
    page: number = 1,
    pageSize: number = 10,
    fileType?: string,
    search?: string
  ): Promise<FileListResponse> {
    const params: Record<string, string | number> = {
      page,
      page_size: pageSize,
    };
    
    if (fileType) params.file_type = fileType;
    if (search) params.search = search;
    
    const response: AxiosResponse<FileListResponse> = await api.get('/files', { params });
    return response.data;
  },

  async getFileDetail(fileId: string, fileType?: string): Promise<FileInfo> {
    const params: Record<string, string> = {};
    if (fileType) params.file_type = fileType;
    
    const response: AxiosResponse<{ file: FileInfo }> = await api.get(`/files/${fileId}`, { params });
    return response.data.file;
  },

  async deleteFile(fileId: string, fileType?: string): Promise<void> {
    const params: Record<string, string> = {};
    if (fileType) params.file_type = fileType;
    
    await api.delete(`/files/${fileId}`, { params });
  },

  async searchFiles(query: string, fileType?: string, page: number = 1, pageSize: number = 10): Promise<FileListResponse> {
    const response: AxiosResponse<FileListResponse> = await api.post('/files/search', {
      query,
      file_type: fileType,
      page,
      page_size: pageSize
    });
    return response.data;
  },

  // Upload operations
  async uploadMarkdown(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response: AxiosResponse<UploadResponse> = await api.post('/upload/md', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response: AxiosResponse<UploadResponse> = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async uploadPDF(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response: AxiosResponse<UploadResponse> = await api.post('/upload/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async bulkUpload(files: File[]): Promise<BulkUploadResponse> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    const response: AxiosResponse<BulkUploadResponse> = await api.post('/upload/bulk', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getSupportedFileTypes(): Promise<{ supported_types: string[], description: string }> {
    const response = await api.get('/files/types/supported');
    return response.data;
  }
};

export default api;
