import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Skip middleware for login page and auth API
  if (request.nextUrl.pathname === '/login' || 
      request.nextUrl.pathname.startsWith('/api/auth/')) {
    return NextResponse.next();
  }

  // Check for authentication token in cookies
  const token = request.cookies.get('access_token');
  
  // If no token and trying to access protected routes, redirect to login
  if (!token && !request.nextUrl.pathname.startsWith('/api/')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // For API routes that need authentication, check token
  if (request.nextUrl.pathname.startsWith('/api/') && 
      !request.nextUrl.pathname.startsWith('/api/auth/')) {
    if (!token) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
