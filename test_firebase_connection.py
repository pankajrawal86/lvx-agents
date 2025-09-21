
import os
import sys
from dotenv import load_dotenv

# Add app directory to the Python path to allow for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

print("--- Firebase Connection Test ---")

# --- Step 1: Load Environment Variables ---
print("1. Loading environment variables from .env file...")
load_dotenv()
db_url = os.environ.get("FIREBASE_DATABASE_URL")
if not db_url:
    print("   ERROR: FIREBASE_DATABASE_URL not found in .env file.")
    print("   Please make sure your .env file is correctly set up.")
    sys.exit(1)
print(f"   - Database URL found: {db_url[:25]}...") # Print a snippet for confirmation

# --- Step 2: Check for Credentials File ---
print("\n2. Checking for Firebase credentials file...")
cred_path = os.path.join(os.getcwd(), "firebase-credentials.json")
if not os.path.exists(cred_path):
    print("   ERROR: firebase-credentials.json not found in the root directory.")
    sys.exit(1)
print("   - credentials.json found.")

# --- Step 3: Initialize Firebase and Fetch Data ---
try:
    import firebase_admin
    from firebase_admin import credentials, db

    print("\n3. Initializing Firebase Admin SDK...")
    # Check if the app is already initialized to prevent errors
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': db_url
        })
        print("   - Firebase Admin SDK initialized successfully.")
    else:
        print("   - Firebase Admin SDK was already initialized.")

    print("\n4. Attempting to query data...")
    # We will try to query for a deal where the 'id' field is '1'.
    # Make sure you have this record in your database.
    test_deal_id = '1'
    ref = db.reference('deals')
    results = ref.order_by_child('id').equal_to(test_deal_id).get()
    
    data = None
    if results:
        # The result is a dictionary where keys are the unique IDs. Get the first one.
        data = list(results.values())[0]
    
    if data:
        company_name = data.get('company', '[Company Name Not Found in Data]')
        print(f"   SUCCESS: Successfully queried data for deal '{company_name}' (ID: {test_deal_id}).")
        print("\n--- Connection Test Passed! ---")
        print("Your application is correctly configured to connect to Firebase.")
    else:
        print(f"   WARNING: Connection successful, but no data found for a deal with id '{test_deal_id}'.")
        print("   Please ensure that a deal with an 'id' field of '1' exists in your 'deals' collection in the Realtime Database.")
        print("\n--- Connection Test Partially Passed ---")

except ImportError as e:
    print(f"\n   ERROR: A required library is not installed: {e}")
    print("   Please make sure you have run 'source .venv/bin/activate && pip install -r requirements.txt'")
    sys.exit(1)
except Exception as e:
    print(f"\n   ERROR: An exception occurred while connecting to Firebase: {e}")
    print("\n--- Connection Test Failed! ---")
    print("   Please check the following:")
    print("   1. Is your FIREBASE_DATABASE_URL in the .env file correct?")
    print("   2. Is the content of firebase-credentials.json valid and saved?")
    print("   3. Does your machine have a stable internet connection?")
    sys.exit(1)
