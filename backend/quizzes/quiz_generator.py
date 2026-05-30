# =============================================================================
# backend/quizzes/quiz_generator.py
# Generates MCQ quizzes modularly WITHOUT any external API.
# =============================================================================

import random
from nltk.tokenize import sent_tokenize

# Import shared extraction helpers from the flashcards package to avoid duplicate code
from flashcards.flashcard_generator import (
    _generate_definition_cards,
    _generate_keyword_cards,
    _clean_answer,
)

def generate_quiz_rulebased(text: str, count: int = 5) -> list[dict]:
    """
    Generate multiple-choice questions without any API.

    Strategy:
    1. Extract definition and keyword sentences -> correct answer is the definition/content
    2. Generate 3 distractor answers from other sentences in the document
    3. Shuffle options and map to A, B, C, D
    """
    sentences = sent_tokenize(text)
    sentences = [s.strip() for s in sentences if len(s.split()) >= 6]

    # Get definition cards and keyword cards as base
    def_cards = _generate_definition_cards(sentences)
    kw_cards = _generate_keyword_cards(text, sentences)

    base_cards = def_cards + kw_cards
    if not base_cards:
        base_cards = [{"question": "What does this passage discuss?",
                       "answer": s} for s in sentences[:count]]

    quiz_questions = []

    for card in base_cards[:count]:
        correct_answer = card["answer"]

        # Generate distractors: other sentences from the text (not the correct one)
        distractors = [
            s.strip() for s in sentences
            if s.strip() != correct_answer
            and len(s.split()) >= 6
            and s.strip()[:40] != correct_answer[:40]
        ]

        # Randomly pick 3 distractors
        random.shuffle(distractors)
        chosen_distractors = distractors[:3]

        if len(chosen_distractors) < 3:
            # Pad with shortened versions if not enough sentences
            chosen_distractors += ["Not mentioned in the text."] * (3 - len(chosen_distractors))

        # Build options
        options_list = [correct_answer] + chosen_distractors[:3]
        random.shuffle(options_list)

        correct_letter = "ABCD"[options_list.index(correct_answer)]
        options = {letter: opt for letter, opt in zip("ABCD", options_list)}

        quiz_questions.append({
            "question":       card["question"],
            "options":        options,
            "correct_answer": correct_letter,
            "explanation":    f"The correct answer is based on the following passage: {correct_answer}",
            "type":           "mcq_rulebased",
        })

    return quiz_questions[:count]


def generate_quiz_questions(text: str, count: int = 5) -> list[dict]:
    """
    Main entry point for MCQ quiz. Drop-in replacement for old services.

    Returns:
        List of {"question", "options", "correct_answer", "explanation"} dicts.
    """
    return generate_quiz_rulebased(text, count)
