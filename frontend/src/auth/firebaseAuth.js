// =============================================================================
// frontend/src/auth/firebaseAuth.js
// Firebase Authentication Adapter Module
// =============================================================================

import { 
  onAuthStateChanged, 
  signInWithPopup, 
  signOut,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  updateProfile
} from "firebase/auth";
import { doc, setDoc, serverTimestamp } from "firebase/firestore";
import { auth, db, googleProvider } from "../services/firebase";

export const firebaseAuth = {
  /**
   * Listen to active session changes and mapping Firebase attributes
   */
  onAuthStateChanged: (callback) => {
    if (!auth) {
      callback(null);
      return () => {};
    }
    return onAuthStateChanged(auth, async (currentUser) => {
      if (currentUser) {
        callback({
          uid: currentUser.uid,
          name: currentUser.displayName,
          email: currentUser.email,
          photoURL: currentUser.photoURL
        });
      } else {
        callback(null);
      }
    });
  },

  /**
   * Google Sign-in Popup and sync basic profile details to Firestore
   */
  loginWithGoogle: async () => {
    if (!auth) throw new Error("Firebase auth not initialized");
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    
    if (db) {
      await setDoc(doc(db, "users", user.uid), {
        uid: user.uid,
        name: user.displayName,
        email: user.email,
        photoURL: user.photoURL,
        lastLogin: serverTimestamp()
      }, { merge: true });
    }
    return user;
  },

  /**
   * Register standard email profiles
   */
  signUpWithEmail: async (name, email, password) => {
    if (!auth) throw new Error("Firebase auth not initialized");
    const result = await createUserWithEmailAndPassword(auth, email, password);
    const user = result.user;

    await updateProfile(user, { displayName: name });

    if (db) {
      await setDoc(doc(db, "users", user.uid), {
        uid: user.uid,
        name: name,
        email: email,
        createdAt: serverTimestamp(),
        lastLogin: serverTimestamp()
      });
    }
    return user;
  },

  /**
   * Sign in standard email profiles
   */
  signInWithEmail: async (email, password) => {
    if (!auth) throw new Error("Firebase auth not initialized");
    const result = await signInWithEmailAndPassword(auth, email, password);
    const user = result.user;

    if (db) {
      await setDoc(doc(db, "users", user.uid), {
        lastLogin: serverTimestamp()
      }, { merge: true });
    }
    return user;
  },

  /**
   * Sign out current user session
   */
  logout: async () => {
    if (!auth) return;
    await signOut(auth);
  },

  /**
   * Retrieve valid JWT token string for the current active session
   */
  getCurrentUserToken: async () => {
    if (!auth || !auth.currentUser) return null;
    return await auth.currentUser.getIdToken(true);
  }
};
