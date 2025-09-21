from flask import Blueprint, request, jsonify
from app.agents.ai_startup_analysis_agent import AIStartupAnalysisAgent

bp = Blueprint('analysis', __name__, url_prefix='/analysis')

@bp.route('/startup/<string:startup_name>', methods=['GET'])
def analyze_startup(startup_name):
    """Analyzes a startup and returns a report."""
    analysis_agent = AIStartupAnalysisAgent()
    report = analysis_agent.run(startup_name)
    return jsonify(report)
