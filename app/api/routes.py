from flask import Blueprint, request, jsonify
from app.agents.ai_startup_analysis_agent import AIStartupAnalysisAgent

# Create a Blueprint for the API
api_bp = Blueprint('api_bp', __name__, url_prefix='/api/v1')

@api_bp.route('/analyze/<string:deal_id>', methods=['POST'])
def analyze_startup(deal_id):
    """
    Analyzes a startup based on the deal ID and a query.
    Can also continue a conversation if a conversation_id is provided.
    ---
    parameters:
      - name: deal_id
        in: path
        type: string
        required: true
        description: The ID of the deal to analyze.
      - name: body
        in: body
        required: true
        schema:
          id: AnalysisQuery
          required:
            - query
          properties:
            query:
              type: string
              description: The analysis query or question.
              example: "Give me a full analysis of this startup."
            conversation_id:
              type: string
              description: The ID of an ongoing conversation for follow-up questions.
              example: "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
    responses:
      200:
        description: Analysis successful
      400:
        description: Bad request (e.g., missing query)
      404:
        description: Deal ID not found
    """
    # Get the data from the request body
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query in request body'}), 400

    query = data['query']
    # Get the optional conversation_id
    conversation_id = data.get('conversation_id')

    # Initialize and run the agent
    agent = AIStartupAnalysisAgent()
    result = agent.run(
        deal_id=deal_id,
        query=query,
        conversation_id=conversation_id
    )

    if 'error' in result:
        # Assuming errors from the agent might be for things like 'deal not found'
        return jsonify(result), 404

    return jsonify(result)
