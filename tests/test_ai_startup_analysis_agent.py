import unittest
from unittest.mock import patch
import os

# Set a dummy API key for testing
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "test_key"

from app.agents.ai_startup_analysis_agent import AIStartupAnalysisAgent

class TestAIStartupAnalysisAgent(unittest.TestCase):

    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'})
    def setUp(self):
        """Set up the test environment before each test."""
        self.llm_patcher = patch('app.agents.base_agent.BaseAgent.generate_text_with_llm')
        self.mock_llm_generate = self.llm_patcher.start()
        self.addCleanup(self.llm_patcher.stop)

        self.orchestrator_agent = AIStartupAnalysisAgent()
        self.mock_startup_data = {
            "id": "1",
            "name": "Terra Food Co.",
            "industry": "Food & Beverages",
            "description": "A test startup",
        }

    def test_initialization(self):
        """Test that the agent and its team are initialized correctly."""
        self.assertEqual(self.orchestrator_agent.agent_name, "AI Startup Analysis Agent")
        self.assertIn("deal_memo", self.orchestrator_agent.agent_team)
        self.assertIn("risk_and_compliance", self.orchestrator_agent.agent_team)
        self.assertIn("benchmarking", self.orchestrator_agent.agent_team)
        self.assertIn("market_research", self.orchestrator_agent.agent_team)
        self.assertIn("portfolio_fit", self.orchestrator_agent.agent_team)
        self.assertIn("digital_footprint", self.orchestrator_agent.agent_team)

    @patch('app.agents.ai_startup_analysis_agent.realtime_db')
    def test_get_startup_data_queries_database(self, mock_realtime_db):
        """Test that _get_startup_data correctly queries the database."""
        # Arrange
        deal_id = "test-deal-123"
        mock_deal_info = {
            "id": deal_id,
            "company": "TestCo",
            "sector": "Tech",
            "description": "A test company."
        }
        mock_key_metrics = {
            "dealId": deal_id,
            "mrr": 10000,
            "churn": 5
        }

        # Configure the mock to return different values for each query call
        mock_realtime_db.query.side_effect = [
            mock_deal_info,
            mock_key_metrics
        ]

        # Act
        startup_data = self.orchestrator_agent._get_startup_data(deal_id)

        # Assert
        self.assertEqual(mock_realtime_db.query.call_count, 2)
        
        # Check the call for deal info
        mock_realtime_db.query.assert_any_call('deals', 'id', deal_id)
        
        # Check the call for key metrics
        mock_realtime_db.query.assert_any_call('key_metrics', 'dealId', deal_id)

        # Check that the data is correctly assembled
        self.assertEqual(startup_data['name'], "TestCo")
        self.assertEqual(startup_data['industry'], "Tech")
        self.assertIn('key_metrics', startup_data)
        self.assertEqual(startup_data['key_metrics']['mrr'], 10000)

    @patch('app.agents.ai_startup_analysis_agent.AIStartupAnalysisAgent._get_startup_data')
    @patch('app.agents.deal_memo_agent.DealMemoAgent.run')
    @patch('app.agents.risk_and_compliance_agent.RiskAndComplianceAgent.run')
    @patch('app.agents.benchmarking_agent.BenchmarkingAgent.run')
    @patch('app.agents.market_research_agent.MarketResearchAgent.run')
    @patch('app.agents.portfolio_fit_agent.PortfolioFitAgent.run')
    @patch('app.agents.digital_footprint_analysis_agent.DigitalFootprintAnalysisAgent.run')
    def test_run_comprehensive_analysis(self, mock_digital, mock_portfolio, mock_market, mock_bench, mock_risk, mock_memo, mock_get_data):
        """Test the full orchestration when 'all' agents are selected for a comprehensive analysis."""
        # Arrange
        deal_id = "1"
        query = "Give me a full analysis of this startup."
        mock_get_data.return_value = self.mock_startup_data
        
        # First LLM call is for routing, second is for synthesizing the final report.
        self.mock_llm_generate.side_effect = ["all", "Final synthesized report."]

        # Act
        result = self.orchestrator_agent.run(deal_id, query)

        # Assert
        mock_get_data.assert_called_once_with(deal_id)
        self.assertEqual(self.mock_llm_generate.call_count, 2)
        
        # Check that all agent run methods were called
        mock_memo.assert_called_once_with(self.mock_startup_data)
        mock_risk.assert_called_once_with(self.mock_startup_data)
        mock_bench.assert_called_once_with(self.mock_startup_data)
        mock_market.assert_called_once_with(self.mock_startup_data)
        mock_portfolio.assert_called_once_with(self.mock_startup_data)
        mock_digital.assert_called_once_with(self.mock_startup_data)

        self.assertIn("final_summary", result["analysis"])
        self.assertEqual(result["analysis"]["final_summary"], "Final synthesized report.")

    @patch('app.agents.ai_startup_analysis_agent.AIStartupAnalysisAgent._get_startup_data')
    @patch('app.agents.digital_footprint_analysis_agent.DigitalFootprintAnalysisAgent.run')
    @patch('app.agents.deal_memo_agent.DealMemoAgent.run')
    @patch('app.agents.risk_and_compliance_agent.RiskAndComplianceAgent.run')
    def test_run_specific_query_linkedin(self, mock_risk_run, mock_memo_run, mock_digital_run, mock_get_data):
        """Test that a specific query for 'linkedin updates' routes to the correct agent."""
        # Arrange
        deal_id = "1"
        query = "check for linkedin updates"
        mock_get_data.return_value = self.mock_startup_data
        
        # Mock the router to deterministically return the 'digital_footprint' agent
        self.mock_llm_generate.return_value = "digital_footprint"
        mock_digital_run.return_value = {"digital_footprint_analysis": "LinkedIn analysis complete"}

        # Act
        with patch('app.agents.ai_startup_analysis_agent.AIStartupAnalysisAgent._format_single_agent_response') as mock_format:
            mock_format.return_value = "LinkedIn analysis complete"
            result = self.orchestrator_agent.run(deal_id, query)

            # Assert
            mock_get_data.assert_called_once_with(deal_id)
            self.mock_llm_generate.assert_called_once()
            mock_digital_run.assert_called_once_with(self.mock_startup_data)
            
            # Ensure other agents were NOT called
            mock_memo_run.assert_not_called()
            mock_risk_run.assert_not_called()

            self.assertIn("response", result["analysis"])
            self.assertEqual(result["analysis"]["response"], "LinkedIn analysis complete")
            self.assertNotIn("final_summary", result["analysis"])

    @patch('app.agents.ai_startup_analysis_agent.AIStartupAnalysisAgent._get_startup_data')
    @patch('app.agents.benchmarking_agent.BenchmarkingAgent.run')
    @patch('app.agents.deal_memo_agent.DealMemoAgent.run')
    def test_run_specific_query_competitors(self, mock_memo_run, mock_bench_run, mock_get_data):
        """Test that a query about competitors routes to the Benchmarking Agent."""
        # Arrange
        deal_id = "1"
        query = "Who are the main competitors of this startup?"
        mock_get_data.return_value = self.mock_startup_data

        # Mock the router to return 'benchmarking'
        self.mock_llm_generate.return_value = "benchmarking"
        mock_bench_run.return_value = {"benchmarking_analysis": "Competitor analysis is complete."}

        # Act
        with patch('app.agents.ai_startup_analysis_agent.AIStartupAnalysisAgent._format_single_agent_response') as mock_format:
            mock_format.return_value = "Competitor analysis is complete."
            result = self.orchestrator_agent.run(deal_id, query)

            # Assert
            mock_get_data.assert_called_once_with(deal_id)
            self.mock_llm_generate.assert_called_once()
            mock_bench_run.assert_called_once_with(self.mock_startup_data)

            # Ensure other agents were not called
            mock_memo_run.assert_not_called()

            self.assertIn("response", result["analysis"])
            self.assertEqual(result["analysis"]["response"], "Competitor analysis is complete.")
            self.assertNotIn("final_summary", result["analysis"])

    @patch('app.agents.ai_startup_analysis_agent.AIStartupAnalysisAgent._get_startup_data')
    def test_run_with_unknown_deal_id(self, mock_get_data):
        """Test the agent's behavior with an unknown deal_id."""
        # Arrange
        deal_id = "deal_unknown"
        query = "any query for an unknown deal"
        mock_get_data.return_value = {"name": "Unknown Startup"}
        
        # Act
        result = self.orchestrator_agent.run(deal_id, query)

        # Assert
        mock_get_data.assert_called_once_with(deal_id)
        self.assertIn('error', result)
        self.assertEqual(result['error'], f"No data found for deal ID: {deal_id}")
        # Ensure no LLM calls were made if the deal is not found
        self.mock_llm_generate.assert_not_called()

if __name__ == '__main__':
    unittest.main()
