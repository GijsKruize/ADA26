import re
from typing import List, Dict, Any

def run_deterministic_grader(answer_text: str, rubric: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Implements the deterministic grader algorithm for LearnSphere.
    """
    word_count = len(re.findall(r'\w+', answer_text))
    
    if word_count >= 80:
        length_bonus = 1.0
    elif word_count >= 40:
        length_bonus = 0.8
    else:
        length_bonus = 0.6
        
    criterion_results = []
    total_max_score = 0
    total_score = 0.0
    
    mastered_concepts = set()
    weak_concepts = set()
    
    for criterion in rubric:
        name = criterion["name"]
        max_points = criterion["max_points"]
        keywords = criterion.get("keywords", [])
        concepts = criterion.get("concepts", [])
        
        total_max_score += max_points
        
        matched_keywords_count = 0
        if keywords:
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', answer_text, re.IGNORECASE):
                    matched_keywords_count += 1
            keyword_ratio = matched_keywords_count / len(keywords)
        else:
            keyword_ratio = 0.0
            
        criterion_score = max_points * ((0.8 * keyword_ratio) + (0.2 * length_bonus))
        criterion_score = round(criterion_score, 1)
        total_score += criterion_score
        
        score_ratio = criterion_score / max_points if max_points > 0 else 0
        
        if score_ratio >= 0.75:
            for concept in concepts:
                mastered_concepts.add(concept)
        elif score_ratio < 0.60:
            for concept in concepts:
                weak_concepts.add(concept)
                
        criterion_results.append({
            "criterion": name,
            "score": criterion_score,
            "max_points": max_points,
            "reason": f"Matched {matched_keywords_count}/{len(keywords)} keywords. Length bonus applied: {length_bonus}."
        })
        
    # Feedback generation
    if criterion_results:
        sorted_results = sorted(criterion_results, key=lambda x: x["score"] / x["max_points"] if x["max_points"] > 0 else 0)
        strongest = sorted_results[-1]
        weakest = sorted_results[0]
        feedback = (f"Strongest area: {strongest['criterion']} (Score: {strongest['score']}/{strongest['max_points']}). "
                    f"Weakest area: {weakest['criterion']} (Score: {weakest['score']}/{weakest['max_points']}).")
    else:
        feedback = "No rubric criteria provided for grading."
        
    return {
        "score": round(total_score, 1),
        "max_score": total_max_score,
        "feedback": feedback,
        "criteria_scores": criterion_results,
        "mastered_concepts": list(mastered_concepts),
        "weak_concepts": list(weak_concepts),
        "trace": {
            "llm_provider": "deterministic-fallback",
            "word_count": word_count,
            "length_bonus": length_bonus
        }
    }
