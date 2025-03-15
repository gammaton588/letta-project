#!/usr/bin/env python3
import os
import sys
import json
import logging
from typing import Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv

class LettaAgentCommunicationTest:
    """
    Test script to simulate communication between Gemini-powered Letta agents
    """
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        load_dotenv(os.path.expanduser('~/.letta/env'))
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.logger.error("Gemini API key not found in environment")
            raise ValueError("GEMINI_API_KEY must be set")
        
        genai.configure(api_key=api_key)
        
        # Create two agents with different personas
        self.researcher_agent = self._create_agent(
            name="ResearchAssistant",
            system_prompt="""You are a meticulous research assistant. 
            Your goal is to provide detailed, well-researched information. 
            Respond scientifically and objectively."""
        )
        
        self.creative_agent = self._create_agent(
            name="CreativeInterpreter",
            system_prompt="""You are a creative interpreter who takes 
            complex research and translates it into engaging, 
            understandable narratives. Make technical information 
            accessible and interesting."""
        )
    
    def _create_agent(self, name: str, system_prompt: str):
        """
        Create a Gemini agent with a specific persona
        
        :param name: Name of the agent
        :param system_prompt: Initial system prompt defining agent's role
        :return: Configured Gemini model
        """
        model = genai.GenerativeModel(
            'gemini-2.0-flash',
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024
            ),
            system_instruction=system_prompt
        )
        
        # Start a chat session
        chat = model.start_chat(history=[])
        return chat
    
    def simulate_conversation(self, topic: str) -> Dict[str, Any]:
        """
        Simulate a conversation between two agents
        
        :param topic: Conversation topic
        :return: Conversation results
        """
        try:
            # Research agent provides initial detailed information
            research_response = self.researcher_agent.send_message(
                f"Provide a comprehensive, scientific overview of {topic}. "
                "Include key facts, research findings, and current understanding."
            )
            
            # Creative agent interprets the research
            creative_response = self.creative_agent.send_message(
                f"Interpret this research about {topic} in an engaging way. "
                f"Make it accessible and interesting:\n\n{research_response.text}"
            )
            
            return {
                'success': True,
                'research_response': research_response.text,
                'creative_response': creative_response.text
            }
        
        except Exception as e:
            self.logger.error(f"Conversation simulation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_test(self):
        """
        Run the agent communication test
        """
        print("🤖 Letta Agent Communication Test 🤖")
        print("===================================")
        
        # Test conversation topics
        test_topics = [
            "Artificial Intelligence and Machine Learning",
            "Climate Change and Sustainable Technologies",
            "Quantum Computing Advancements"
        ]
        
        for topic in test_topics:
            print(f"\n📍 Topic: {topic}")
            print("-" * 50)
            
            result = self.simulate_conversation(topic)
            
            if result['success']:
                print("🔬 Research Perspective:")
                print(result['research_response'][:500] + "...\n")
                
                print("🎨 Creative Interpretation:")
                print(result['creative_response'][:500] + "...\n")
            else:
                print(f"❌ Test failed: {result.get('error', 'Unknown error')}")

def main():
    communication_test = LettaAgentCommunicationTest()
    communication_test.run_test()

if __name__ == '__main__':
    main()
