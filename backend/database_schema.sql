-- Database schema for the RPI backend application

-- Create markdown_documents table
CREATE TABLE IF NOT EXISTS markdown_documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create image_documents table
CREATE TABLE IF NOT EXISTS image_documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create pdf_documents table
CREATE TABLE IF NOT EXISTS pdf_documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_markdown_documents_created_at ON markdown_documents(created_at);
CREATE INDEX IF NOT EXISTS idx_image_documents_created_at ON image_documents(created_at);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_created_at ON pdf_documents(created_at);
