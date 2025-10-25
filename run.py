import uvicorn


if __name__ == "__main__":    
    uvicorn.run(
        "app.main:app",
        host="188.93.140.207",
        port=8000,
        reload=True
    )
