
import os
import json
from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials as firebase_credentials, db
import google.generativeai as genai
from dotenv import load_dotenv
from google.oauth2 import service_account

# Load environment variables from .env file
load_dotenv()

# --- Real Generative AI Service ---
# Configure the Generative AI client
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Warning: GOOGLE_API_KEY environment variable not set. LLM calls will fail.")
    generative_model = None
else:
    genai.configure(api_key=api_key)
    generative_model = genai.GenerativeModel('gemini-1.5-flash-latest')


# --- Firebase Realtime Database Service ---
# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        # Create the Secret Manager client.
        client = secretmanager.SecretManagerServiceClient()

        # Get the secret version.
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_NUMBER")
        secret_id = "firebase-credentials"
        version_id = "1"
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        secret_payload = response.payload.data.decode("UTF-8")
        cred_dict = json.loads(secret_payload)
        
        cred = firebase_credentials.Certificate(cred_dict)
        db_url = os.environ.get("FIREBASE_DATABASE_URL")
        if db_url:
            firebase_admin.initialize_app(cred, {
                'databaseURL': db_url
            })
            print("Firebase Admin SDK initialized successfully.")
        else:
            print("Warning: FIREBASE_DATABASE_URL environment variable not set. Firebase will not be initialized.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")

class GoogleRealtimeDatabase:
    """A wrapper class for the Firebase Realtime Database to be used as a tool for the LLM.
    This is not a general purpose Firebase client, but rather a specific implementation for the LLM.
    """
    def get(self, path):
        """Fetches data from the specified path in the database."""
        try:
            ref = db.reference(path)
            data = ref.get()
            return data
        except Exception as e:
            print(f"An error occurred while fetching data from Firebase: {e}")
            return None

    def query(self, path, field, value):
        """Queries the database for a specific value in a specific field."""
        try:
            ref = db.reference(path)
            # Query the database for a specific value in a specific field
            results = ref.order_by_child(field).equal_to(value).get()
            return results
        except Exception as e:
            print(f"An error occurred while querying data from Firebase: {e}")
            return None


# --- Vertex AI Vector Search Service ---
class GoogleVectorDB:
    def __init__(self):
        self.initialized = False
        print("--- GoogleVectorDB initialization is commented out. Vector search will be disabled. ---")
        # try:
        #     # Get environment variables
        #     project = os.environ.get("GOOGLE_CLOUD_PROJECT_NUMBER")
        #     region = os.environ.get("VECTOR_SEARCH_REGION")
        #     endpoint_id = os.environ.get("VECTOR_SEARCH_ENDPOINT_ID")
        #     deployed_index_id = os.environ.get("VECTOR_SEARCH_DEPLOYED_INDEX_ID")
        #     credentials_path = "vector_search_credentials.json"

        #     # Check if all environment variables are set
        #     if not all([project, region, endpoint_id, deployed_index_id]):
        #         print("Warning: Vector search environment variables not fully set. Vector search will not work.")
        #         return
            
        #     if not os.path.exists(credentials_path):
        #         print(f"Warning: {credentials_path} not found. Vector search will not be initialized.")
        #         return

        #     credentials = service_account.Credentials.from_service_account_file(credentials_path)

        #     # Initialize the AI Platform client with the service account credentials
        #     aiplatform.init(project=project, location=region, credentials=credentials)

        #     # Get the endpoint
        #     self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=endpoint_id)

        #     self.deployed_index_id = deployed_index_id
        #     self.initialized = True
        #     print("Vertex AI Vector Search initialized successfully.")

        # except Exception as e:
        #     print(f"An error occurred during Vertex AI initialization: {e}")
        #     self.initialized = False

    def search(self, query, num_neighbors=5):
        """Connects to the deployed index and finds the nearest neighbors.
        This is a specific implementation for the LLM and not a general purpose vector search client.
        """
        if not self.initialized:
            print("--- FAKE VECTOR DB SEARCH (not initialized): {} ---".format(query))
            return []
        
        try:
            # Encode the query to a vector using Google's model
            embedding_result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = embedding_result['embedding']

            # Find the nearest neighbors
            results = self.index_endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_embedding],
                num_neighbors=num_neighbors
            )
            return results
        except Exception as e:
            print(f"An error occurred during the vector search: {e}")
            return []


# Initialize the services for reuse
vector_db = GoogleVectorDB()
realtime_db = GoogleRealtimeDatabase()
