from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import tools

app = FastAPI(title="Assessment MCP Server")

class ToolExecuteRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

@app.get("/health")
def health():
    return {"status": "ok", "service": "assessment-mcp-server"}

@app.post("/tools/execute")
async def execute_tool(request: ToolExecuteRequest):
    tool_name = request.tool
    args = request.arguments

    try:
        if tool_name == "get_assignment":
            if "assignment_id" not in args:
                raise HTTPException(status_code=400, detail="Missing argument: assignment_id")
            return await tools.get_assignment(args["assignment_id"])
        
        elif tool_name == "get_submission":
            if "submission_id" not in args:
                raise HTTPException(status_code=400, detail="Missing argument: submission_id")
            return await tools.get_submission(args["submission_id"])
        
        elif tool_name == "record_grade":
            if "submission_id" not in args:
                raise HTTPException(status_code=400, detail="Missing argument: submission_id")
            if "grade_payload" not in args:
                raise HTTPException(status_code=400, detail="Missing argument: grade_payload")
            return await tools.record_grade(args["submission_id"], args["grade_payload"])
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
