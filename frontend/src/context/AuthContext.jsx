// =============================================================================
// frontend/src/context/AuthContext.jsx
// Refactored Authentication Context utilizing Auth Abstraction Layer
// =============================================================================

import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../auth/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Register the session listener via the abstract Auth Service
    const unsubscribe = authService.onAuthStateChanged((currentUser) => {
      if (currentUser) {
        setUser(currentUser);
        setIsLoggedIn(true);
      } else {
        setUser(null);
        setIsLoggedIn(false);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  /**
   * Google Federated Sign-in Handler
   */
  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      const user = await authService.loginWithGoogle();
      return user;
    } catch (error) {
      console.error("Error signing in with Google:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Email/Password Account Registration
   */
  const signUpWithEmail = async (name, email, password) => {
    try {
      setLoading(true);
      const user = await authService.signUpWithEmail(name, email, password);
      return user;
    } catch (error) {
      console.error("Error in signUpWithEmail:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Email/Password Account Verification
   */
  const signInWithEmail = async (email, password) => {
    try {
      setLoading(true);
      const user = await authService.signInWithEmail(email, password);
      return user;
    } catch (error) {
      console.error("Error in signInWithEmail:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Session Termination
   */
  const logout = async () => {
    try {
      setLoading(true);
      await authService.logout();
    } catch (error) {
      console.error("Error signing out:", error);
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    isLoggedIn,
    loading,
    loginWithGoogle,
    signUpWithEmail,
    signInWithEmail,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
};
