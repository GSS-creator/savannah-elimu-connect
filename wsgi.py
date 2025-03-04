import os
import sys
from dotenv import load_dotenv

# Add the application directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

try:
    from messaging_app.app import app
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

 