import Cookies from 'js-cookie';
import axios from 'axios';
import { LoginResponse, AuthError } from '@/models/auth';

class AuthService {
  private static readonly TOKEN_KEY = 'access_token';
  
  async login(accessCode: string): Promise<LoginResponse> {
    try {
      const response = await axios.post<LoginResponse>('/api/auth/login', {
        password: accessCode
      });
      
      // Store the token in cookies
      this.setToken(response.data.access_token);
      
      return response.data;
    } catch (error: any) {
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Login failed');
    }
  }
  
  setToken(token: string): void {
    Cookies.set(AuthService.TOKEN_KEY, token, { 
      expires: 7, // 7 days
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict'
    });
  }
  
  getToken(): string | undefined {
    return Cookies.get(AuthService.TOKEN_KEY);
  }
  
  removeToken(): void {
    Cookies.remove(AuthService.TOKEN_KEY);
  }
  
  isAuthenticated(): boolean {
    return !!this.getToken();
  }
  
  logout(): void {
    this.removeToken();
  }
  
  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }
}

export const authService = new AuthService();
