'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '@/lib/api';
import { FileInfo, UploadResponse, BulkUploadResponse } from '@/models/file';
import { Upload, File, Image, FileText, Check, X, AlertCircle } from 'lucide-react';

interface UploadedFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  result?: FileInfo;
  error?: string;
}

export default function UploadPage() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      file,
      status: 'pending'
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/markdown': ['.md', '.markdown'],
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    },
    maxSize: 4 * 1024 * 1024, // 4MB
  });

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-6 h-6 text-green-500" />;
    } else if (file.type === 'application/pdf') {
      return <FileText className="w-6 h-6 text-red-500" />;
    } else if (file.type.includes('markdown') || file.name.endsWith('.md')) {
      return <File className="w-6 h-6 text-blue-500" />;
    }
    return <File className="w-6 h-6 text-gray-500" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const uploadSingleFile = async (uploadedFile: UploadedFile): Promise<UploadedFile> => {
    try {
      let result: UploadResponse;
      
      if (uploadedFile.file.type.startsWith('image/')) {
        result = await apiService.uploadImage(uploadedFile.file);
      } else if (uploadedFile.file.type === 'application/pdf') {
        result = await apiService.uploadPDF(uploadedFile.file);
      } else {
        result = await apiService.uploadMarkdown(uploadedFile.file);
      }

      return {
        ...uploadedFile,
        status: 'success',
        result: result.file_info
      };
    } catch (error: any) {
      return {
        ...uploadedFile,
        status: 'error',
        error: error.response?.data?.detail || error.message || 'Upload failed'
      };
    }
  };

  const handleUpload = async () => {
    if (uploadedFiles.length === 0) return;

    setIsUploading(true);

    // Update all files to uploading status
    setUploadedFiles(prev => 
      prev.map(file => ({ ...file, status: 'uploading' as const }))
    );

    try {
      if (uploadedFiles.length === 1) {
        // Single file upload
        const result = await uploadSingleFile(uploadedFiles[0]);
        setUploadedFiles([result]);
      } else {
        // Bulk upload
        try {
          const files = uploadedFiles.map(uf => uf.file);
          const bulkResult: BulkUploadResponse = await apiService.bulkUpload(files);
          
          const updatedFiles: UploadedFile[] = uploadedFiles.map((uploadedFile, index) => {
            const successFile = bulkResult.successful_uploads.find(
              sf => sf.title === uploadedFile.file.name.split('.')[0]
            );
            const failedFile = bulkResult.failed_uploads.find(
              ff => ff.filename === uploadedFile.file.name
            );

            if (successFile) {
              return {
                ...uploadedFile,
                status: 'success',
                result: successFile
              };
            } else if (failedFile) {
              return {
                ...uploadedFile,
                status: 'error',
                error: failedFile.error
              };
            } else {
              return {
                ...uploadedFile,
                status: 'error',
                error: 'Unknown error occurred'
              };
            }
          });

          setUploadedFiles(updatedFiles);
        } catch (bulkError: any) {
          // If bulk upload fails, try individual uploads
          const results = await Promise.all(
            uploadedFiles.map(uploadSingleFile)
          );
          setUploadedFiles(results);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setUploadedFiles([]);
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'pending':
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
      case 'uploading':
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'success':
        return <Check className="w-4 h-4 text-green-500" />;
      case 'error':
        return <X className="w-4 h-4 text-red-500" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Upload Files</h1>
          <p className="text-gray-600 mt-1">
            Upload markdown files, images, or PDFs (max 4MB each)
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-blue-600">Drop the files here...</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">
                  Drag & drop files here, or click to select files
                </p>
                <p className="text-sm text-gray-500">
                  Supports: Markdown (.md), Images (.png, .jpg, .gif), PDFs (.pdf)
                </p>
              </div>
            )}
          </div>

          {/* File list */}
          {uploadedFiles.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">
                  Files to Upload ({uploadedFiles.length})
                </h2>
                <div className="flex space-x-2">
                  <button
                    onClick={clearAll}
                    className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
                    disabled={isUploading}
                  >
                    Clear All
                  </button>
                  <button
                    onClick={handleUpload}
                    disabled={isUploading || uploadedFiles.every(f => f.status === 'success')}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    {isUploading ? 'Uploading...' : 'Upload All'}
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                {uploadedFiles.map((uploadedFile, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      {getFileIcon(uploadedFile.file)}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {uploadedFile.file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(uploadedFile.file.size)}
                        </p>
                        {uploadedFile.error && (
                          <p className="text-xs text-red-500 mt-1">
                            {uploadedFile.error}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      {getStatusIcon(uploadedFile.status)}
                      {uploadedFile.status === 'pending' && (
                        <button
                          onClick={() => removeFile(index)}
                          className="p-1 text-gray-400 hover:text-red-500"
                          disabled={isUploading}
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
