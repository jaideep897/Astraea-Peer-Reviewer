from AstraeaV3_env.server.app import app
import uvicorn
import os
from dotenv import load_dotenv

# Load local environment variables (.env)
if os.path.exists(".env"):
    load_dotenv(".env", override=True)
elif os.path.exists("AstraeaV3_env/.env"):
    load_dotenv("AstraeaV3_env/.env", override=True)
else:
    load_dotenv(override=True)

if __name__ == "__main__":
    # Standard entry point for local runs and deployment verification
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
