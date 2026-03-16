import os
import sys

# Add parent directory to path so 'backend' can be imported
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
