// Authentication-related types
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AuthError {
  detail: string;
}
