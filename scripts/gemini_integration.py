#!/usr/bin/env python3
"""
Gemini API Integration Library for Letta
This module provides a clean, reusable interface for integrating 
Google Gemini API with Letta agents.
"""

import os
import json
import logging
from typing import Dict, List, Union, Optional, Any
from google import generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gemini_integration')

class GeminiAPI:
    """Wrapper class for Google Gemini API integration with Letta"""
    
    DEFAULT_MODEL = "gemini-2.0-flash"
    
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        """
        Initialize the Gemini API client
        
        Args:
            api_key: Google Gemini API key (will use env var if None)
            model: Gemini model to use
        """
        # Load environment from .letta/env file if exists
        if os.path.exists(os.path.expanduser("~/.letta/env")):
            load_dotenv(os.path.expanduser("~/.letta/env"))
        
        # Get API key from param or env var
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No Gemini API key provided or found in environment")
        
        # Initialize the client
        genai.configure(api_key=self.api_key)
        self.model = model
        logger.info(f"Initialized GeminiAPI with model: {model}")
    
    def generate_response(self, 
                         prompt: str, 
                         system_prompt: Optional[str] = None,
                         temperature: float = 0.7, 
                         max_tokens: int = 4096,
                         top_p: float = 0.95,
                         top_k: int = 64) -> Dict[str, Any]:
        """
        Generate a response from Gemini API
        
        Args:
            prompt: User prompt/message
            system_prompt: Optional system instructions
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Dict containing response text and metadata
        """
        try:
            # Create generation config
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                top_p=top_p, 
                top_k=top_k,
                max_output_tokens=max_tokens,
            )
            
            # Get the model
            model = genai.GenerativeModel(self.model)
            
            # Prepare content based on whether system_prompt exists
            if system_prompt:
                # Use chat format with system prompt
                chat = model.start_chat(history=[])
                chat.send_message(system_prompt, generation_config=generation_config)
                response = chat.send_message(prompt, generation_config=generation_config)
            else:
                # Use simple format without system prompt
                response = model.generate_content(prompt, generation_config=generation_config)
            
            # Process response
            return {
                "text": response.text,
                "model": self.model,
                "finish_reason": getattr(response, "finish_reason", None),
                "usage": getattr(response, "usage", {}),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "text": f"Error: {str(e)}",
                "model": self.model,
                "success": False,
                "error": str(e)
            }
    
    def analyze_image(self, 
                     prompt: str, 
                     image_path: str,
                     temperature: float = 0.7) -> Dict[str, Any]:
        """
        Analyze an image using Gemini's multimodal capabilities
        
        Args:
            prompt: Text prompt describing what to analyze
            image_path: Path to the image file
            temperature: Controls randomness (0.0-1.0)
            
        Returns:
            Dict containing analysis text and metadata
        """
        try:
            # Check for multimodal compatibility
            vision_model = "gemini-1.5-pro"  # Using a model with vision capabilities
            
            # Load the image
            img = genai.utils.encode_image(image_path)
            
            # Create generation config
            generation_config = genai.GenerationConfig(
                temperature=temperature,
            )
            
            # Get the model
            model = genai.GenerativeModel(vision_model)
            
            # Create multimodal request
            response = model.generate_content(
                [prompt, img],
                generation_config=generation_config
            )
            
            return {
                "text": response.text,
                "model": vision_model,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {
                "text": f"Error: {str(e)}",
                "model": self.model,
                "success": False,
                "error": str(e)
            }
    
    def create_chat_session(self, system_prompt: str = "") -> 'GeminiChatSession':
        """
        Create a stateful chat session for multi-turn conversations
        
        Args:
            system_prompt: Instructions for the assistant
            
        Returns:
            GeminiChatSession instance
        """
        return GeminiChatSession(self.model, system_prompt)
    
    def list_available_models(self) -> List[str]:
        """
        List available Gemini models
        
        Returns:
            List of available model names
        """
        try:
            models = genai.list_models()
            return [m.name for m in models 
                    if 'generateContent' in m.supported_generation_methods]
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []


class GeminiChatSession:
    """Maintains state for multi-turn conversations with Gemini"""
    
    def __init__(self, model: str, system_prompt: str = ""):
        """
        Initialize a chat session
        
        Args:
            model: Model to use for this chat session
            system_prompt: System instructions
        """
        self.model = model
        self.system_prompt = system_prompt
        
        # Initialize the model
        self.model_instance = genai.GenerativeModel(model)
        
        # Initialize chat with system prompt if provided
        if system_prompt:
            self.chat = self.model_instance.start_chat(history=[
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["I'll help you with that."]}
            ])
        else:
            self.chat = self.model_instance.start_chat(history=[])
    
    def send_message(self, 
                    message: str, 
                    temperature: float = 0.7, 
                    max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Send a message in this chat session
        
        Args:
            message: User message
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict containing response text and metadata
        """
        try:
            # Create generation config
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Send message to the chat session
            response = self.chat.send_message(
                message,
                generation_config=generation_config
            )
            
            return {
                "text": response.text,
                "model": self.model,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in chat session: {str(e)}")
            return {
                "text": f"Error: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.chat.history
    
    def clear_history(self) -> None:
        """Clear conversation history except system prompt"""
        if self.system_prompt:
            self.chat = self.model_instance.start_chat(history=[
                {"role": "user", "parts": [self.system_prompt]},
                {"role": "model", "parts": ["I'll help you with that."]}
            ])
        else:
            self.chat = self.model_instance.start_chat(history=[])


# Helper functions for common Letta integrations

def create_letta_agent_config(name: str, 
                            description: str, 
                            system_prompt: str,
                            gemini_model: str = "gemini-2.0-flash",
                            temperature: float = 0.7,
                            max_tokens: int = 4096,
                            top_p: float = 0.95) -> Dict[str, Any]:
    """
    Create a Letta agent configuration for Gemini
    
    Args:
        name: Agent name
        description: Agent description
        system_prompt: System prompt/instructions
        gemini_model: Gemini model to use
        temperature: Default temperature
        max_tokens: Maximum tokens for responses
        top_p: Top-p sampling parameter
        
    Returns:
        Letta agent configuration dict
    """
    return {
        "name": name,
        "description": description,
        "model_config": {
            "provider": "gemini",
            "model": gemini_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        },
        "system_prompt": system_prompt
    }


# Example usage
if __name__ == "__main__":
    # Simple usage demonstration
    try:
        # Initialize API
        api = GeminiAPI()
        
        # Generate a simple response
        response = api.generate_response(
            prompt="What are the best practices for AI safety?",
            system_prompt="You are a helpful AI assistant focused on AI ethics and safety."
        )
        
        print("\n=== Simple Response ===")
        print(response["text"])
        
        # Create a chat session
        chat = api.create_chat_session(
            system_prompt="You are a knowledgeable assistant specialized in technology."
        )
        
        # Multi-turn conversation
        print("\n=== Chat Session ===")
        msg1 = chat.send_message("What is the difference between machine learning and deep learning?")
        print("Q: What is the difference between machine learning and deep learning?")
        print(f"A: {msg1['text']}\n")
        
        msg2 = chat.send_message("Can you give me a simple example of each?")
        print("Q: Can you give me a simple example of each?")
        print(f"A: {msg2['text']}")
        
        # Create a Letta agent config
        agent_config = create_letta_agent_config(
            name="TechGemini",
            description="A technology specialist assistant powered by Gemini",
            system_prompt="You are TechGemini, an AI assistant specialized in technology, programming, and AI concepts. Provide clear, accurate, and helpful responses to technical questions."
        )
        
        print("\n=== Letta Agent Configuration ===")
        print(json.dumps(agent_config, indent=2))
        
    except Exception as e:
        print(f"Error in demonstration: {e}")
