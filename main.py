from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app)

if __name__ == '__main__':
    # In a production environment, you would use a WSGI server like Gunicorn
    # For development, the Flask development server is fine.
    app.run(debug=True)