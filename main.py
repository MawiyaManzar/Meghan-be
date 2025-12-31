"""
Root main.py - Wrapper to expose the FastAPI app from app/main.py
This allows running 'fastapi dev main.py' from the project root.
"""
from app.main import app

# Re-export the FastAPI app so it can be imported as 'app'
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
