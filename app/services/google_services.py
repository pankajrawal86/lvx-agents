
import os
import json
from dotenv import load_dotenv

# --- Service Clients ---
# These are initialized by initialize_services()
generative_model = None


def initialize_services():
    """
    Initializes all external services by loading configuration and then setting up clients.
    - In a GCP environment, it loads config from Secret Manager.
    - For local development, it loads config from a .env file.
    """
    global generative_model

    # --- 1. Load Configuration ---
    project_id_number = os.environ.get("GOOGLE_CLOUD_PROJECT_NUMBER")
    
    if project_id_number:
        # PRODUCTION: Load from Google Cloud Secret Manager
        print("Initializing from Secret Manager (Production Environment).")
        try:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()

            # The secret should contain a JSON payload with all required environment variables
            secret_id = "firebase-credentials"
            name = f"projects/{project_id_number}/secrets/{secret_id}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            secret_payload = response.payload.data.decode("UTF-8")
            config_from_secret = json.loads(secret_payload)

            # Populate environment variables from the secret
            for key, value in config_from_secret.items():
                if key not in os.environ and value is not None:
                    os.environ[key] = str(value)
            print(f"Loaded {len(config_from_secret)} settings from Secret Manager.")

        except Exception as e:
            print(f"CRITICAL: Failed to initialize from Secret Manager: {e}")
            # This is a fatal error in production, so we exit.
            raise SystemExit(f"Could not load production configuration: {e}")
    else:
        # LOCAL: Load from .env file
        print("Initializing from .env file (Local Environment).")
        load_dotenv()
        # For local Firebase auth, ensure GOOGLE_APPLICATION_CREDENTIALS is in your .env file
        # and points to your service account JSON file.
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set in .env for local development.")

    # --- 2. Initialize Services using Loaded Configuration ---
    
    # Initialize Firebase Admin SDK
    try:
        import firebase_admin
        from firebase_admin import credentials as firebase_credentials, db

        if not firebase_admin._apps:
            db_url = os.environ.get("FIREBASE_DATABASE_URL")
            if not db_url:
                raise ValueError("FIREBASE_DATABASE_URL is not set in the environment.")

            # In production, creds are inferred from the environment. Locally, from the JSON file.
            if project_id_number:
                 # In a managed GCP environment, credentials can often be inferred.
                cred = firebase_credentials.ApplicationDefault()
            else:
                 # Locally, we rely on GOOGLE_APPLICATION_CREDENTIALS pointing to a file.
                cred = firebase_credentials.ApplicationDefault()

            firebase_admin.initialize_app(cred, {'databaseURL': db_url})
            print("Firebase Admin SDK initialized successfully.")
        else:
            print("Firebase Admin SDK was already initialized.")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Firebase Admin SDK: {e}")
        raise SystemExit(f"Could not initialize Firebase: {e}")

    # Configure Google Generative AI client
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        generative_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("Google Generative AI client configured successfully.")
    else:
        print("Warning: GOOGLE_API_KEY not found. LLM calls will fail.")

    # Initialize Vertex AI for Vector Search
    vector_project_id = os.environ.get("VECTOR_GOOGLE_CLOUD_PROJECT_ID")
    vector_location = os.environ.get("VECTOR_SEARCH_REGION")
    if vector_project_id and vector_location:
        try:
            from google.cloud import aiplatform
            aiplatform.init(project=vector_project_id, location=vector_location)
            print("Vertex AI Platform client configured for Vector Search.")
        except Exception as e:
            print(f"Error initializing Vertex AI Platform client: {e}")
    else:
        print("Warning: Vertex AI Search environment variables not fully set.")

# --- Run Initialization --- 
# This code runs once when the module is first imported.
initialize_services()
