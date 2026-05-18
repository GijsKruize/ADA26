import pytest
from unittest.mock import patch, AsyncMock
from agents.recommender_agent.app.recommender import get_recommendations

@pytest.mark.asyncio
@patch("agents.recommender_agent.app.mcp_client.get_learning_profile")
@patch("agents.recommender_agent.app.mcp_client.list_materials")
@patch("agents.recommender_agent.app.mcp_client.list_modules")
async def test_recommender_weak_concept(mock_list_modules, mock_list_materials, mock_get_profile):
    # Case 1: Given a profile with weak_concepts: ["pubsub"] 
    # and a material list with one material having concepts: ["pubsub"], 
    # assert that material is returned.
    
    learner_id = "test-learner"
    course_id = "test-course"
    
    mock_get_profile.return_value = {
        "learner_id": learner_id,
        "weak_concepts": ["pubsub"]
    }
    
    mock_list_modules.return_value = [
        {"module_id": "mod1", "order": 1}
    ]
    
    mock_list_materials.return_value = [
        {
            "material_id": "mat1",
            "module_id": "mod1",
            "title": "PubSub Basics",
            "concepts": ["pubsub"],
            "order": 1
        },
        {
            "material_id": "mat2",
            "module_id": "mod1",
            "title": "Other Topic",
            "concepts": ["other"],
            "order": 2
        }
    ]
    
    response = await get_recommendations(learner_id, course_id)
    
    assert len(response.recommendations) == 1
    assert response.recommendations[0].material_id == "mat1"
    assert "pubsub" in response.recommendations[0].concepts
    assert "weak concept: pubsub" in response.recommendations[0].reason

@pytest.mark.asyncio
@patch("agents.recommender_agent.app.mcp_client.get_learning_profile")
@patch("agents.recommender_agent.app.mcp_client.list_materials")
@patch("agents.recommender_agent.app.mcp_client.list_modules")
async def test_recommender_no_weak_concepts(mock_list_modules, mock_list_materials, mock_get_profile):
    # Case 2: Given a profile with no weak concepts, 
    # assert the first material by order is returned.
    
    learner_id = "test-learner"
    course_id = "test-course"
    
    mock_get_profile.return_value = {
        "learner_id": learner_id,
        "weak_concepts": []
    }
    
    mock_list_modules.return_value = [
        {"module_id": "mod1", "order": 1},
        {"module_id": "mod2", "order": 2}
    ]
    
    mock_list_materials.return_value = [
        {
            "material_id": "mat-late",
            "module_id": "mod2",
            "title": "Late Material",
            "concepts": ["topic2"],
            "order": 1
        },
        {
            "material_id": "mat-early",
            "module_id": "mod1",
            "title": "Early Material",
            "concepts": ["topic1"],
            "order": 1
        }
    ]
    
    response = await get_recommendations(learner_id, course_id)
    
    assert len(response.recommendations) == 1
    # mat-early is in mod1 (order 1), mat-late is in mod2 (order 2)
    assert response.recommendations[0].material_id == "mat-early"
    assert "sequence" in response.recommendations[0].reason
