# Models

This directory contains TypeScript type definitions and interfaces used throughout the application.

## Structure

```
models/
├── index.ts      # Re-exports all models
├── file.ts       # File-related types (FileInfo, FileListResponse, etc.)
├── auth.ts       # Authentication types (LoginResponse, AuthError)
├── chat.ts       # Chat-related types (Message)
└── README.md     # This file
```

## Usage

### Import from specific model file (recommended)
```typescript
import { FileInfo, FileListResponse } from '@/models/file';
import { LoginResponse } from '@/models/auth';
import { Message } from '@/models/chat';
```

### Import from index (alternative)
```typescript
import { FileInfo, LoginResponse, Message } from '@/models';
```

## Model Categories

### File Models (`file.ts`)
- `FileInfo` - Represents a file with metadata
- `FileListResponse` - Paginated list of files
- `UploadResponse` - Response from file upload
- `BulkUploadResponse` - Response from bulk file upload

### Authentication Models (`auth.ts`)
- `LoginResponse` - Response from login endpoint
- `AuthError` - Authentication error structure

### Chat Models (`chat.ts`)
- `Message` - Chat message structure

## Best Practices

1. **Domain Separation**: Keep models organized by domain/feature
2. **Specific Imports**: Import from specific model files rather than the index
3. **Type Safety**: Use strict typing with `Record<string, unknown>` instead of `any`
4. **Documentation**: Add JSDoc comments for complex interfaces
5. **Consistency**: Follow consistent naming conventions across all models
