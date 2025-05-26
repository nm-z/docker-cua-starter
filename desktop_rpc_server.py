from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn
import sys
import traceback
import json
import os
sys.path.append(os.path.dirname(__file__))
from computer import DockerComputer

app = FastAPI()
computer = DockerComputer()

@app.post("/jsonrpc")
async def jsonrpc_handler(request: Request):
    try:
        data = await request.json()
        method = data.get("method")
        params = data.get("params", {})
        req_id = data.get("id")
        if not hasattr(computer, method):
            return {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Method {method} not found"}, "id": req_id}
        func = getattr(computer, method)
        # Handle positional and keyword arguments
        if isinstance(params, dict):
            result = func(**params)
        elif isinstance(params, list):
            result = func(*params)
        else:
            result = func(params)
        return {"jsonrpc": "2.0", "result": result, "id": req_id}
    except Exception as e:
        tb = traceback.format_exc()
        return {"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e), "data": tb}, "id": data.get("id")}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=14500) 