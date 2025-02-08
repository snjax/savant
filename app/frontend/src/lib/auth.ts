import { writable } from 'svelte/store';

export interface User {
  id: string;
  name: string;
  email: string;
  picture?: string;
}

export const user = writable<User | null>(null);
export const isInitialized = writable(false);

declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: GoogleInitializeConfig) => void;
          prompt: (callback?: (notification: PromptNotification) => void) => void;
          renderButton: (element: HTMLElement, config: GoogleButtonConfig) => void;
          disableAutoSelect: () => void;
          storeCredential: (credential: { id: string; password: string }, callback: () => void) => void;
          cancel: () => void;
          revoke: (userId: string, callback: () => void) => void;
        };
      };
    };
  }
}

interface GoogleInitializeConfig {
  client_id: string;
  callback: (response: GoogleCredentialResponse) => void;
  auto_select?: boolean;
  context?: string;
}

interface GoogleButtonConfig {
  theme?: 'outline' | 'filled_blue' | 'filled_black';
  size?: 'large' | 'medium' | 'small';
  text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin';
  shape?: 'rectangular' | 'pill' | 'circle' | 'square';
  logo_alignment?: 'left' | 'center';
  width?: number;
  locale?: string;
}

interface PromptNotification {
  isNotDisplayed: () => boolean;
  isSkippedMoment: () => boolean;
  isDismissedMoment: () => boolean;
  getMomentType: () => string;
  getNotDisplayedReason: () => string;
  getSkippedReason: () => string;
  getDismissedReason: () => string;
}

interface GoogleCredentialResponse {
  credential: string;
  select_by: string;
  clientId: string;
}

function waitForGoogleLoad(): Promise<void> {
  return new Promise((resolve) => {
    if (window.google && window.google.accounts) {
      resolve();
      return;
    }

    const checkGoogle = () => {
      if (window.google && window.google.accounts) {
        resolve();
      } else {
        setTimeout(checkGoogle, 100);
      }
    };

    checkGoogle();
  });
}

export async function initializeAuth() {
  try {
    const response = await fetch('/api/v1/user/me');
    if (response.ok) {
      const userData = await response.json();
      user.set(userData);
      isInitialized.set(true);
      return;
    }

    await waitForGoogleLoad();

    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: handleCredentialResponse,
      auto_select: false,
    });

    // Disable auto-select to prevent automatic popups
    window.google.accounts.id.disableAutoSelect();
    isInitialized.set(true);
  } catch (error) {
    console.error('Failed to initialize auth:', error);
    isInitialized.set(true);
  }
}

async function handleCredentialResponse(response: GoogleCredentialResponse) {
  try {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token: response.credential }),
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.error || 'Login failed');
    }

    const userData = await res.json();
    user.set(userData);
    window.location.href = '/';
  } catch (error) {
    console.error('Login error:', error);
  }
}

export async function logout() {
  try {
    const response = await fetch('/api/v1/auth/logout');
    if (!response.ok) {
      throw new Error('Logout failed');
    }
    user.set(null);
    window.location.href = '/login';
  } catch (error) {
    console.error('Logout error:', error);
  }
} 
