from . import mcp_client
from .models import Recommendation, RecommendResponse
from typing import List, Dict, Any

async def get_recommendations(learner_id: str, course_id: str) -> RecommendResponse:
    # 1. Get learner profile via T7
    profile = await mcp_client.get_learning_profile(learner_id)
    weak_concepts = profile.get("weak_concepts", [])
    
    # 3. Get materials for the course via T6
    materials = await mcp_client.list_materials(course_id)
    # Get modules to sort by module order
    modules = await mcp_client.list_modules(course_id)
    
    # Create a map for module orders
    module_order_map = {m["module_id"]: m["order"] for m in modules}
    
    # Sort materials by module.order then material.order
    def sort_key(mat):
        return (module_order_map.get(mat["module_id"], 999), mat.get("order", 0))
    
    sorted_materials = sorted(materials, key=sort_key)
    
    recommendation = None
    reason = ""
    
    # 2. If weak_concepts is non-empty, take the first weak concept
    if weak_concepts:
        first_weak_concept = weak_concepts[0]
        # 4. Return the first material (sorted by module.order then material.order) 
        # whose concepts list contains the weak concept
        for mat in sorted_materials:
            if first_weak_concept in mat.get("concepts", []):
                recommendation = mat
                reason = f"Based on your weak concept: {first_weak_concept}"
                break
    
    # 5. If no match, return the first material by module.order then material.order
    if not recommendation and sorted_materials:
        recommendation = sorted_materials[0]
        reason = "Following the course sequence"
        
    recommendations = []
    if recommendation:
        recommendations.append(Recommendation(
            material_id=recommendation["material_id"],
            module_id=recommendation["module_id"],
            title=recommendation["title"],
            reason=reason,
            concepts=recommendation.get("concepts", [])
        ))
        
    return RecommendResponse(
        learner_id=learner_id,
        course_id=course_id,
        recommendations=recommendations
    )
