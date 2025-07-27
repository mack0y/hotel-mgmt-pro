# wsgi.py
<<<<<<< HEAD
import os
from run import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use PORT if available, otherwise 5000
    app.run(host="0.0.0.0", port=port)
=======
from run import app

if __name__ == "__main__":
    app.run()
>>>>>>> 123d7ca1cb1a9fc0f20da4936dcc520fa5865572
