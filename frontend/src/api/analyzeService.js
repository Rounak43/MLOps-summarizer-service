// =============================================================================
// frontend/src/api/analyzeService.js
// Centralized API Service wrappers for NLP and Summarization
// =============================================================================

import axiosInstance from './axiosInstance';

/**
 * Summarize raw text input directly (pasted text)
 */
export async function analyzeContent(input) {
  try {
    const response = await axiosInstance.post('/api/summarize-text', {
      text: input,
      summary_mode: 'medium'
    });
    
    return {
      ...response.data,
      topics: response.data.keywords || [],
    };
  } catch (error) {
    console.error('Analysis failed:', error);
    throw new Error(error.response?.data?.error || 'Failed to analyze text content');
  }
}

/**
 * Execute full PDF/DOCX multi-pipeline (Summary + MCQ + Flashcards)
 */
export async function analyzeFull(file, options = {}) {
  const formData = new FormData();
  formData.append('file', file);
  if (options.mode) formData.append('summary_mode', options.mode);
  if (options.flashcardCount) formData.append('flashcard_count', options.flashcardCount);
  if (options.quizCount) formData.append('quiz_count', options.quizCount);

  try {
    const response = await axiosInstance.post('/api/full', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  } catch (error) {
    console.error('Full analysis failed:', error);
    throw new Error(error.response?.data?.error || 'Failed to analyze document');
  }
}

/**
 * Execute full raw text multi-pipeline (Summary + MCQ + Flashcards)
 */
export async function analyzeFullText(text, options = {}) {
  try {
    const response = await axiosInstance.post('/api/full-text', {
      text,
      summary_mode: options.mode || 'medium',
      flashcard_count: options.flashcardCount || 10,
      quiz_count: options.quizCount || 5
    });
    return response.data;
  } catch (error) {
    console.error('Full text analysis failed:', error);
    throw new Error(error.response?.data?.error || 'Failed to analyze text content');
  }
}

/**
 * Summarize file only
 */
export async function analyzeFile(file, options = {}) {
  const formData = new FormData();
  formData.append('file', file);
  if (options.mode) formData.append('summary_mode', options.mode);
  if (options.ratio) formData.append('summary_ratio', options.ratio);
  if (options.useAbstractive) formData.append('use_abstractive_refinement', options.useAbstractive);

  try {
    const response = await axiosInstance.post('/api/summarize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  } catch (error) {
    console.error('File summarization failed:', error);
    throw new Error(error.response?.data?.error || 'Failed to summarize file');
  }
}

/**
 * Generate active recall flashcards only
 */
export async function generateFlashcards(file, count = 10, useTransformer = false) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('count', count);
  formData.append('use_transformer', useTransformer);

  try {
    const response = await axiosInstance.post('/api/flashcards', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  } catch (error) {
    console.error('Flashcard generation failed:', error);
    throw new Error(error.response?.data?.error || 'Failed to generate flashcards');
  }
}

/**
 * Generate multiple choice quiz only
 */
export async function generateQuiz(file, count = 5) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('count', count);

  try {
    const response = await axiosInstance.post('/api/quiz', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  } catch (error) {
    console.error('Quiz generation failed:', error);
    throw new Error(error.response?.data?.error || 'Failed to generate quiz');
  }
}
