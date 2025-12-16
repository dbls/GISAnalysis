"""Claude API integration for natural language query processing."""
import os
from anthropic import Anthropic
from typing import Dict, Optional
import json


class ClaudeQueryParser:
    """Parse natural language queries using Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude API client.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
        """
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

    def parse_query(self, query_text: str, available_metadata: Dict = None) -> Dict:
        """
        Parse a natural language query and determine what analysis to perform.

        Args:
            query_text: User's natural language query
            available_metadata: Optional metadata about available images/analyses

        Returns:
            Dictionary with parsed query intent and parameters
        """
        system_prompt = """You are a query parser for a GIS satellite imagery analysis system.
Your job is to interpret natural language queries and return structured JSON responses.

The system can:
1. Count objects (cars, trucks, buildings, etc.) using YOLOv8
2. Retrieve previously computed metadata
3. Provide image information (bounds, resolution, CRS, etc.)

Supported object classes for detection:
- Vehicles: car, truck, bus, motorcycle, bicycle
- Other: person, airplane, boat, etc. (full COCO dataset)

Return a JSON object with:
{
  "query_type": "count" | "metadata" | "info" | "unknown",
  "target_object": "class_name" (for count queries),
  "analysis_needed": true/false (whether new analysis is required),
  "response_template": "human-readable response template"
}

Examples:
- "number of cars" -> {"query_type": "count", "target_object": "car", "analysis_needed": true}
- "how many trucks" -> {"query_type": "count", "target_object": "truck", "analysis_needed": true}
- "image resolution" -> {"query_type": "metadata", "field": "resolution", "analysis_needed": false}
- "what's the coordinate system" -> {"query_type": "metadata", "field": "crs", "analysis_needed": false}
"""

        user_message = f"Parse this query: '{query_text}'"

        if available_metadata:
            user_message += f"\n\nAvailable metadata: {json.dumps(available_metadata, indent=2)}"

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to parse JSON from response
            try:
                # Look for JSON in the response
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                elif "{" in response_text:
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    json_str = response_text[json_start:json_end]
                else:
                    json_str = response_text

                parsed = json.loads(json_str)
                return parsed

            except json.JSONDecodeError:
                # Fallback: return raw response
                return {
                    "query_type": "unknown",
                    "raw_response": response_text,
                    "analysis_needed": False
                }

        except Exception as e:
            return {
                "query_type": "error",
                "error": str(e),
                "analysis_needed": False
            }

    def generate_response(
        self,
        query_text: str,
        analysis_result: Dict
    ) -> str:
        """
        Generate a natural language response based on query and analysis results.

        Args:
            query_text: Original user query
            analysis_result: Dictionary containing analysis results

        Returns:
            Natural language response string
        """
        system_prompt = """You are an assistant for a GIS satellite imagery analysis system.
Generate clear, concise responses to user queries based on analysis results.
Be factual and specific with numbers and data."""

        user_message = f"""Query: "{query_text}"

Analysis Result:
{json.dumps(analysis_result, indent=2)}

Generate a clear, natural language response to the user's query."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Error generating response: {str(e)}"
