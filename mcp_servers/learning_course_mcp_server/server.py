from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import tools

app = FastAPI(title="Learning Course MCP Server")

class ToolExecuteRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

@app.get("/health")
def health():
    return {"status": "ok", "service": "learning-course-mcp-server"}

@app.post("/tools/execute")
async def execute_tool(request: ToolExecuteRequest):
    tool_name = request.tool
    args = request.arguments

    try:
        if tool_name == "get_course":
            if "course_id" not in args:
                raise HTTPException(status_code=400, detail="Missing argument: course_id")
            return await tools.get_course(args["course_id"])
        
        elif tool_name == "list_modules":
            if "course_id" not in args:
                raise HTTPException(status_code=400, detail="Missing argument: course_id")
            return await tools.list_modules(args["course_id"])
        
        elif tool_name == "list_materials":
            if "course_id" not in args:
                raise HTTPException(status_code=400, detail="Missing argument: course_id")
            return await tools.list_materials(args["course_id"])
        
        elif tool_name == "get_learning_profile":
            if "learner_id" not in args:
                raise HTTPException(status_code=400, detail="Missing argument: learner_id")
            return await tools.get_learning_profile(args["learner_id"])
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
