
import os
import sys

# Add app directory to the Python path to allow for imports from the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

print("--- Firebase Connection Test (using google_services) ---")

# The google_services module will handle initialization on import
print("\n1. Initializing services via app.services.google_services...")
try:
    from app.services import google_services
    from firebase_admin import db, _apps
    print("   - Successfully imported services.")
except ImportError as e:
    print(f"   ERROR: Failed to import a required module: {e}")
    print("   Please ensure you have activated the virtual environment: `source .venv/bin/activate`")
    sys.exit(1)
except Exception as e:
    print(f"   ERROR: An exception occurred during service initialization: {e}")
    sys.exit(1)

# Check which environment is being used
if "GOOGLE_CLOUD_PROJECT_NUMBER" in os.environ:
    print("   - Running in PRODUCTION-LIKE environment (found GOOGLE_CLOUD_PROJECT_NUMBER).")
else:
    print("   - Running in LOCAL environment (using .env file).")


# --- Step 2: Verify Firebase Initialization and Query Data ---
print("\n2. Verifying Firebase initialization and attempting to query data...")

if not _apps:
    print("   ERROR: Firebase Admin SDK was not initialized by google_services.")
    sys.exit(1)
else:
    print(f"   - Firebase App '{list(_apps.keys())[0]}' initialized successfully.")

try:
    test_deal_id = 1  # The ID from the original error
    
    print(f"   - Querying 'deals' collection for a record with id: {test_deal_id}")
    deals_ref = db.reference('deals')
    
    results = deals_ref.order_by_child('id').equal_to(test_deal_id).get()

    if not results:
         results = deals_ref.order_by_child('id').equal_to(str(test_deal_id)).get()


    if results:
        deal_key = list(results.keys())[0]
        deal_data = results[deal_key]
        company_name = deal_data.get('company', '[Name Not Found]')
        print(f"   SUCCESS: Found data for deal '{company_name}' (ID: {test_deal_id}).")
        print("\n--- Connection Test Passed! ---")
    else:
        print(f"   WARNING: Connection successful, but no data found for a deal with id={test_deal_id}.")
        print("   This confirms the original 'No data found' error.")
        print("   Please check your Firebase Realtime Database and ensure the deal exists.")
        print("\n--- Connection Test Partially Passed ---")

except Exception as e:
    print(f"\n   ERROR: An exception occurred while querying the database: {e}")
    print("\n--- Connection Test Failed! ---")
    sys.exit(1)
