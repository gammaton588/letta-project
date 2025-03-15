"""
AI-powered diagnostics for Letta server using Google Gemini.
"""
import os
import json
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class AITroubleshooter:
    def __init__(self):
        # Load API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')) as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.strip().split('=')[1].strip("'").strip('"')
                        break
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def _create_system_prompt(self) -> str:
        """Create a system prompt for the AI model."""
        return """You are an expert system administrator and Docker specialist.
Your task is to analyze Letta server issues and provide specific, actionable solutions.
Focus on practical steps and command-line solutions.
Format your response in markdown with clear sections:
1. Issue Analysis
2. Root Cause
3. Solution Steps
4. Prevention Measures"""

    def _format_check_results(self, results: List[Dict]) -> str:
        """Format check results for AI analysis."""
        formatted = "### System Status\n"
        for result in results:
            status = "✅" if result['passed'] else "❌"
            formatted += f"{status} {result['message']}\n"
            if not result['passed'] and result.get('error_details'):
                formatted += f"Error: {result['error_details']}\n"
        return formatted

    def _format_logs(self, logs: str) -> str:
        """Format log entries for AI analysis."""
        return f"### Recent Logs\n```\n{logs}\n```"

    def _format_repair_history(self, repairs: List[Dict]) -> str:
        """Format repair history for AI analysis."""
        if not repairs:
            return ""
        formatted = "### Recent Repair Attempts\n"
        for repair in repairs:
            status = "✅" if repair['success'] else "❌"
            formatted += f"{repair['timestamp']} - {status} {repair['component']}: {repair['action']}\n"
        return formatted

    async def analyze_issues(self, 
                           check_results: List[Dict],
                           recent_logs: str,
                           repair_history: Optional[List[Dict]] = None) -> str:
        """
        Analyze system issues using Gemini AI.
        
        Args:
            check_results: List of check results with status and messages
            recent_logs: Recent system logs
            repair_history: Optional list of recent repair attempts
        
        Returns:
            AI analysis and recommendations
        """
        # Prepare context for AI
        context = [
            "# Letta Server Diagnostic Report\n",
            self._format_check_results(check_results),
            self._format_logs(recent_logs)
        ]
        
        if repair_history:
            context.append(self._format_repair_history(repair_history))
            
        # Add system configuration context
        context.append("""
### System Configuration
- Docker-based Letta server
- External Port: 8284
- Internal Port: 8283
- Using Google Gemini API
- Auto-start enabled via launchd
""")

        # Generate analysis
        prompt = self._create_system_prompt() + "\n\nAnalyze this system status and provide recommendations:\n\n" + "\n".join(context)
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"""### AI Analysis Error
Unable to generate AI analysis: {str(e)}

Please check:
1. Gemini API key configuration
2. Network connectivity
3. API rate limits"""

    def get_quick_fix(self, specific_error: str) -> str:
        """
        Get a quick fix suggestion for a specific error.
        
        Args:
            specific_error: The specific error message or issue
            
        Returns:
            Quick fix suggestion
        """
        prompt = f"""As a Docker and system administration expert, provide a quick fix for this Letta server issue:

{specific_error}

Focus on:
1. Immediate solution
2. Command to run
3. Expected outcome"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate quick fix: {str(e)}"
