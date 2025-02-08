import { writable } from 'svelte/store';

export interface User {
  id: string;
  name: string;
  email: string;
  picture?: string;
}

export const user = writable<User | null>(null);

declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          prompt: (callback?: any) => void;
          renderButton: (element: HTMLElement, config: any) => void;
        };
      };
    };
  }
}

export async function initializeAuth() {
  const response = await fetch('/api/v1/user/me');
  if (response.ok) {
    const userData = await response.json();
    user.set(userData);
    return;
  }

  window.google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: handleCredentialResponse,
  });
}

async function handleCredentialResponse(response: any) {
  try {
    const res = await fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token: response.credential }),
    });

    if (res.ok) {
      window.location.href = '/';
    } else {
      console.error('Login failed');
    }
  } catch (error) {
    console.error('Login error:', error);
  }
} 
