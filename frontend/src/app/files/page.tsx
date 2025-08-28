'use client';

import { useState, useEffect } from 'react';
import { apiService } from '@/lib/api';
import { FileInfo, FileListResponse } from '@/models/file';
import { 
  Search, 
  Filter, 
  File, 
  Image, 
  FileText, 
  Eye, 
  Trash2, 
  ChevronLeft, 
  ChevronRight,
  Calendar,
  FileSize
} from 'lucide-react';

export default function FilesPage() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFileType, setSelectedFileType] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const pageSize = 12;

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response: FileListResponse = await apiService.listFiles(
        currentPage,
        pageSize,
        selectedFileType || undefined,
        searchQuery || undefined
      );
      
      setFiles(response.files);
      setTotalPages(response.pagination.total_pages);
      setTotalItems(response.pagination.total_items);
    } catch (error) {
      console.error('Failed to load files:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, [currentPage, selectedFileType]);

  const handleSearch = async () => {
    setCurrentPage(1);
    await loadFiles();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'image':
        return <Image className="w-8 h-8 text-green-500" />;
      case 'pdf':
        return <FileText className="w-8 h-8 text-red-500" />;
      case 'markdown':
        return <File className="w-8 h-8 text-blue-500" />;
      default:
        return <File className="w-8 h-8 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleViewFile = async (file: FileInfo) => {
    try {
      const detailedFile = await apiService.getFileDetail(file.id, file.file_type);
      setSelectedFile(detailedFile);
      setIsModalOpen(true);
    } catch (error) {
      console.error('Failed to load file details:', error);
    }
  };

  const handleDeleteFile = async (file: FileInfo) => {
    if (!confirm(`Are you sure you want to delete "${file.title}"?`)) {
      return;
    }

    try {
      await apiService.deleteFile(file.id, file.file_type);
      await loadFiles(); // Reload the files list
    } catch (error) {
      console.error('Failed to delete file:', error);
      alert('Failed to delete file. Please try again.');
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
  };

  const renderFileContent = (file: FileInfo) => {
    if (file.file_type === 'markdown' && file.content) {
      return (
        <div className="prose max-w-none">
          <pre className="whitespace-pre-wrap font-sans">{file.content}</pre>
        </div>
      );
    }
    
    if (file.file_type === 'image') {
      return (
        <div className="text-center">
          <p className="text-gray-500 mb-4">Image preview not available in this demo</p>
          <p className="text-sm text-gray-400">
            In a full implementation, the image would be displayed here
          </p>
        </div>
      );
    }
    
    if (file.file_type === 'pdf' && file.content) {
      return (
        <div className="prose max-w-none">
          <h3 className="text-lg font-medium mb-4">Extracted Text Content:</h3>
          <pre className="whitespace-pre-wrap font-sans text-sm">{file.content}</pre>
        </div>
      );
    }
    
    return (
      <div className="text-center text-gray-500">
        <p>No preview available for this file type</p>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Files</h1>
          
          {/* Search and Filter */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex gap-2">
              <select
                value={selectedFileType}
                onChange={(e) => setSelectedFileType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Types</option>
                <option value="markdown">Markdown</option>
                <option value="image">Images</option>
                <option value="pdf">PDFs</option>
              </select>
              
              <button
                onClick={handleSearch}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Search className="w-4 h-4" />
                Search
              </button>
            </div>
          </div>
          
          {/* Results info */}
          <div className="mt-4 text-sm text-gray-600">
            Showing {files.length} of {totalItems} files
          </div>
        </div>

        {/* Files Grid */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : files.length === 0 ? (
            <div className="text-center py-12">
              <File className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No files found</h3>
              <p className="text-gray-500">
                {searchQuery || selectedFileType
                  ? 'Try adjusting your search criteria'
                  : 'Upload some files to get started'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    {getFileIcon(file.file_type)}
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleViewFile(file)}
                        className="p-1 text-gray-400 hover:text-blue-500"
                        title="View file"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteFile(file)}
                        className="p-1 text-gray-400 hover:text-red-500"
                        title="Delete file"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  <h3 className="font-medium text-gray-900 truncate mb-2" title={file.title}>
                    {file.title}
                  </h3>
                  
                  <div className="space-y-1 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <FileSize className="w-3 h-3" />
                      {formatFileSize(file.file_size)}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(file.upload_date)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="p-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="p-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* File Detail Modal */}
      {isModalOpen && selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{selectedFile.title}</h2>
                <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                  <span className="capitalize">{selectedFile.file_type}</span>
                  <span>{formatFileSize(selectedFile.file_size)}</span>
                  <span>{formatDate(selectedFile.upload_date)}</span>
                </div>
              </div>
              <button
                onClick={closeModal}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <span className="sr-only">Close</span>
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              {renderFileContent(selectedFile)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
