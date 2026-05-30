// =============================================================================
// frontend/src/auth/authService.js
// Centralized Unified Authentication Abstraction Layer
// =============================================================================

import { firebaseAuth } from './firebaseAuth';
import { cognitoAuth } from './cognitoAuth';

// Read authentication provider from environment (default to Firebase)
const authProviderType = (import.meta.env.VITE_AUTH_PROVIDER || 'firebase').toLowerCase();

// Expose the active provider dynamically
const activeProvider = authProviderType === 'cognito' ? cognitoAuth : firebaseAuth;

console.info(`[AuthAbstraction] Active Authentication provider bound: [${authProviderType}]`);

export const authService = {
  /**
   * Listen to active session changes
   */
  onAuthStateChanged: (callback) => activeProvider.onAuthStateChanged(callback),

  /**
   * Google sign-in triggers
   */
  loginWithGoogle: () => activeProvider.loginWithGoogle(),

  /**
   * Register standard email pools
   */
  signUpWithEmail: (name, email, password) => activeProvider.signUpWithEmail(name, email, password),

  /**
   * Sign in standard email pools
   */
  signInWithEmail: (email, password) => activeProvider.signInWithEmail(email, password),

  /**
   * Sign out current user session
   */
  logout: () => activeProvider.logout(),

  /**
   * Retrieve valid JWT token string for active session headers
   */
  getCurrentUserToken: () => activeProvider.getCurrentUserToken(),
  
  /**
   * Returns active provider name
   */
  getProviderName: () => authProviderType
};
export default authService;
