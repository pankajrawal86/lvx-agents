
import unittest
from unittest.mock import patch, MagicMock

# Make sure the app module is in the path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.ai_startup_analysis_agent import AIStartupAnalysisAgent

class TestDatabaseIntegration(unittest.TestCase):
    """
    Tests the data retrieval method of the AIStartupAnalysisAgent
    to ensure it correctly interacts with the database service.
    """

    def setUp(self):
        """Set up the agent for testing."""
        self.agent = AIStartupAnalysisAgent()

    @patch('app.agents.ai_startup_analysis_agent.realtime_db')
    def test_get_startup_data_success(self, mock_realtime_db):
        """
        Test that _get_startup_data successfully fetches and combines deal and metrics data.
        """
        # Arrange
        deal_id = "test_deal_1"
        mock_deal_data = {
            "company": "TestCo",
            "sector": "Tech",
            "description": "A test company."
        }
        mock_metrics_data = {
            "arr": "$1M",
            "valuation": "$10M"
        }

        # Configure the mock to return different values on subsequent calls
        mock_realtime_db.get.side_effect = [
            mock_deal_data,
            mock_metrics_data
        ]

        # Act
        result = self.agent._get_startup_data(deal_id)

        # Assert
        self.assertEqual(mock_realtime_db.get.call_count, 2)
        mock_realtime_db.get.assert_any_call(f'deals/{deal_id}')
        mock_realtime_db.get.assert_any_call(f'key_metrics/{deal_id}')

        self.assertEqual(result['name'], "TestCo")
        self.assertEqual(result['industry'], "Tech")
        self.assertIn('key_metrics', result)
        self.assertEqual(result['key_metrics']['arr'], "$1M")

    @patch('app.agents.ai_startup_analysis_agent.realtime_db')
    def test_get_startup_data_deal_not_found(self, mock_realtime_db):
        """
        Test that _get_startup_data returns 'Unknown Startup' if the deal is not found.
        """
        # Arrange
        deal_id = "deal_does_not_exist"
        
        # Configure the mock to simulate the deal not being found
        mock_realtime_db.get.return_value = None

        # Act
        result = self.agent._get_startup_data(deal_id)

        # Assert
        # Verify it only tried to fetch the 'deals' data once
        mock_realtime_db.get.assert_called_once_with(f'deals/{deal_id}')
        
        # Verify it returns the correct 'not found' structure
        self.assertEqual(result['name'], "Unknown Startup")
        self.assertNotIn('key_metrics', result)

if __name__ == '__main__':
    unittest.main()
