#!/usr/bin/env python3
"""
Taskade Integration Test Suite

Comprehensive testing for Taskade conversation retrieval and storage.
"""

import os
import sys
import unittest
import logging
from typing import Dict, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.taskade_integration import TaskadeIntegration
from letta_server_manager import LettaServerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/Library/Logs/taskade_integration_test.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TaskadeIntegrationTest(unittest.TestCase):
    def setUp(self):
        """Initialize test environment"""
        self.taskade_integration = TaskadeIntegration()
        self.letta_manager = LettaServerManager()
    
    def test_taskade_api_connectivity(self):
        """Test connectivity to Taskade API"""
        try:
            agents = self.taskade_integration.get_workspace_agents()
            self.assertIsNotNone(agents, "Failed to retrieve agents from Taskade")
            logger.info(f"Successfully retrieved {len(agents)} agents")
        except Exception as e:
            self.fail(f"Taskade API connection failed: {e}")
    
    def test_agent_conversation_retrieval(self):
        """Test retrieving conversations for an agent"""
        agents = self.taskade_integration.get_workspace_agents()
        
        if not agents:
            self.skipTest("No agents available for testing")
        
        test_agent = agents[0]
        agent_id = test_agent.get('id')
        
        conversations = self.taskade_integration.get_agent_conversations(agent_id)
        self.assertTrue(len(conversations) > 0, "No conversations retrieved")
        logger.info(f"Retrieved {len(conversations)} conversations for agent {agent_id}")
    
    def test_conversation_storage(self):
        """Test storing conversations in Letta server"""
        agents = self.taskade_integration.get_workspace_agents()
        
        if not agents:
            self.skipTest("No agents available for testing")
        
        test_agent = agents[0]
        agent_id = test_agent.get('id')
        
        conversations = self.taskade_integration.get_agent_conversations(agent_id)
        
        for conversation in conversations[:3]:  # Test first 3 conversations
            try:
                conversation_id = self.taskade_integration.save_conversation(
                    agent_id=agent_id,
                    platform='taskade',
                    conversation_data=conversation
                )
                self.assertIsNotNone(conversation_id, "Failed to save conversation")
                logger.info(f"Successfully saved conversation {conversation_id}")
            except Exception as e:
                self.fail(f"Conversation storage failed: {e}")
    
    def test_error_handling(self):
        """Test error handling for invalid scenarios"""
        with self.assertRaises(ValueError):
            TaskadeIntegration(token='invalid_token')
        
        with self.assertRaises(Exception):
            self.taskade_integration.get_agent_conversations('non_existent_agent')

def run_tests():
    """Run the test suite and generate a report"""
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TaskadeIntegrationTest)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Generate a detailed report
    report = {
        'total_tests': test_result.testsRun,
        'failures': len(test_result.failures),
        'errors': len(test_result.errors),
        'skipped': len(test_result.skipped),
        'successful': test_result.wasSuccessful()
    }
    
    logger.info(f"Test Report: {report}")
    return report

if __name__ == '__main__':
    run_tests()
