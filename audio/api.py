from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from generate import generate_song
from loguru import logger
import os

app = FastAPI()
LOG_FILE = os.path.join("$LOG_DIR", "api.log")
logger.add(LOG_FILE, rotation="500 MB")

SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(401, detail="Invalid token")
    return token

@app.get("/generate_song")
async def api_generate_song(token: str = Depends(verify_token)):
    try:
        generate_song()
        return {"message": "Song generated", "file": "$OUTPUT_DIR/generated_song.wav", "midi": "$OUTPUT_DIR/generated_song.mid"}
    except Exception as e:
        logger.error(f"Error generating song: {e}")
        raise HTTPException(500, detail=f"Song generation failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
