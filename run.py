import sys
import os
import importlib.util
from dotenv import load_dotenv

# ───── PROXY PACKAGE FOR FLATTENED DEPLOYMENT ─────
# If the folder 'AstraeaV3_env' is missing, we create a proxy in sys.modules
if not os.path.exists("AstraeaV3_env"):
    print("--- [DETECTED] Flattened Structure. Reconstructing Astraea Engine... ---")
    
    # Create empty modules to satisfy imports
    from types import ModuleType
    
    # AstraeaV3_env
    ast_pkg = ModuleType("AstraeaV3_env")
    sys.modules["AstraeaV3_env"] = ast_pkg
    
    # AstraeaV3_env.server
    srv_pkg = ModuleType("AstraeaV3_env.server")
    sys.modules["AstraeaV3_env.server"] = srv_pkg
    
    # AstraeaV3_env.models
    if os.path.exists("models.py"):
        spec = importlib.util.spec_from_file_location("AstraeaV3_env.models", "models.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["AstraeaV3_env.models"] = mod
        spec.loader.exec_module(mod)

    # AstraeaV3_env.server.app
    if os.path.exists("app.py"):
        spec = importlib.util.spec_from_file_location("AstraeaV3_env.server.app", "app.py")
        app_mod = importlib.util.module_from_spec(spec)
        sys.modules["AstraeaV3_env.server.app"] = app_mod
        spec.loader.exec_module(app_mod)

    # AstraeaV3_env.server.environment
    if os.path.exists("environment.py"):
        spec = importlib.util.spec_from_file_location("AstraeaV3_env.server.environment", "environment.py")
        env_mod = importlib.util.module_from_spec(spec)
        sys.modules["AstraeaV3_env.server.environment"] = env_mod
        spec.loader.exec_module(env_mod)

# ───── Standard Startup ─────
from AstraeaV3_env.server.app import app
import uvicorn

# Load environment variables (.env)
if os.path.exists(".env"):
    load_dotenv(".env", override=True)

if __name__ == "__main__":
    # Standard entry point for Hugging Face Spaces
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Astraea OS Booting on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
