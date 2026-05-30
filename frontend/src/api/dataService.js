// =============================================================================
// frontend/src/api/dataService.js
// Centralized Data Service Abstraction (Firebase Firestore & SQL PostgreSQL)
// =============================================================================

import axiosInstance from './axiosInstance';
import { 
  collection, 
  addDoc, 
  query, 
  where, 
  getDocs, 
  deleteDoc,
  doc,
  serverTimestamp
} from "firebase/firestore";
import { db } from "../services/firebase";

// Read database engine target from environment (defaults to Firebase for local debugging)
const DB_ENGINE = (import.meta.env.VITE_DB_TYPE || 'firebase').toLowerCase();

console.info(`[DataServiceAbstraction] Database storage engine active: [${DB_ENGINE}]`);

/**
 * Save academic summary analysis metadata to history
 */
export const saveSummary = async (userId, summaryData) => {
  if (DB_ENGINE === 'postgres') {
    try {
      const response = await axiosInstance.post('/api/summaries', summaryData);
      return response.data.id;
    } catch (error) {
      console.error("SQL database save summary failed:", error);
      throw error;
    }
  } else {
    // Firebase Firestore fallback
    if (!db) {
      console.warn("Firestore not initialized. Summary was not persisted.");
      return null;
    }
    try {
      const docRef = await addDoc(collection(db, "summaries"), {
        userId,
        ...summaryData,
        createdAt: serverTimestamp(),
      });
      return docRef.id;
    } catch (error) {
      console.error("Firestore save summary failed:", error);
      throw error;
    }
  }
};

/**
 * Retrieve summary history lists for the active user session
 */
export const getUserSummaries = async (userId) => {
  if (DB_ENGINE === 'postgres') {
    try {
      const response = await axiosInstance.get('/api/summaries');
      
      // Decore and decorate JSON payloads to match Firestore timestamps interfaces
      return response.data.map(item => {
        const seconds = item.createdAt?.seconds || Math.floor(Date.now() / 1000);
        const jsDate = new Date(seconds * 1000);
        
        return {
          ...item,
          createdAt: {
            seconds,
            nanoseconds: 0,
            toDate: () => jsDate
          }
        };
      });
    } catch (error) {
      console.error("SQL database getUserSummaries failed:", error);
      throw error;
    }
  } else {
    // Firebase Firestore fallback
    if (!db) return [];
    try {
      const q = query(
        collection(db, "summaries"),
        where("userId", "==", userId)
      );
      const querySnapshot = await getDocs(q);
      const docs = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      // Sort locally by timestamp descending
      return docs.sort((a, b) => {
        const timeA = a.createdAt?.seconds || 0;
        const timeB = b.createdAt?.seconds || 0;
        return timeB - timeA;
      });
    } catch (error) {
      console.error("Firestore getUserSummaries failed:", error);
      throw error;
    }
  }
};

/**
 * Permanently delete historical summary analysis from library
 */
export const deleteSummary = async (summaryId) => {
  if (DB_ENGINE === 'postgres') {
    try {
      await axiosInstance.delete(`/api/summaries/${summaryId}`);
    } catch (error) {
      console.error("SQL database deleteSummary failed:", error);
      throw error;
    }
  } else {
    // Firebase Firestore fallback
    if (!db) return;
    try {
      const docRef = doc(db, "summaries", summaryId);
      await deleteDoc(docRef);
    } catch (error) {
      console.error("Firestore deleteSummary failed:", error);
      throw error;
    }
  }
};
