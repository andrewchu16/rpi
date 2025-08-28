import { NextRequest } from 'next/server';

const API_BASE_URL = process.env.BACKEND_API_URL || 'http://api:8000';

export async function makeAuthenticatedRequest(
  request: NextRequest,
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = request.cookies.get('access_token')?.value;
  
  if (!token) {
    throw new Error('No authentication token found');
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  return fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
}

export function getAuthToken(request: NextRequest): string | undefined {
  return request.cookies.get('access_token')?.value;
}
