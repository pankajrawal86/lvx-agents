import google.generativeai as genai
import os
from app.tools.vector_search import vector_search
import json

# The ToolbeltAgent is a more advanced agent that can use tools.
# It is designed to be a drop-in replacement for the BaseAgent.
class ToolbeltAgent:
    """Base class for agents that can use tools."""
    def __init__(self, agent_name, tools=None):
        self.agent_name = agent_name
        self.tools = tools if tools else []
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initializes the Google Generative AI model."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("--- LLM NOT INITIALIZED: GOOGLE_API_KEY not set. --- ")
            return None
        genai.configure(api_key=api_key)
        
        # Prepare the tools for the generative model
        model_tools = { "tools": self.tools } if self.tools else {}

        return genai.GenerativeModel(
            model_name='gemini-flash-latest',
            **model_tools
        )

    def generate_text_with_llm(self, prompt):
        """
        Generates text using the configured LLM, automatically handling tool calls.
        """
        if not self.llm:
            print("--- LLM NOT INITIALIZED: Returning placeholder text. Set GOOGLE_API_KEY. ---")
            return f"[Placeholder LLM response for: {prompt[:50]}...]"

        try:
            print(f"--- CALLING LLM for {self.agent_name} with prompt: {prompt[:100]}... ---")
            result = self.llm.generate_content(prompt)
            
            # This is the new tool-calling logic. If the LLM returns a tool call, we execute it.
            # This is a recursive function that will continue to execute tools until the LLM
            # returns a text response.
            while result.candidates[0].content.parts[0].function_call:
                function_call = result.candidates[0].content.parts[0].function_call
                tool_name = function_call.name
                tool_args = dict(function_call.args)
                
                # This is the new, more informative logging you requested.
                print(f"--- AGENT: {self.agent_name} is calling TOOL: {tool_name} with args: {tool_args} ---")
                
                # Find and execute the corresponding tool function
                tool_function = globals().get(tool_name)
                if tool_function:
                    # Note: We are using `globals()` to find the tool function. This is a simple
                    # approach for this example. In a larger application, you would want to use a more
                    # robust tool registry.
                    tool_response = tool_function(**tool_args)
                    
                    # Send the tool's response back to the LLM
                    result = self.llm.generate_content(
                        [   # We are creating a conversation history to send back to the LLM
                            result.candidates[0].content, # The original prompt
                            # This is the corrected part. The SDK expects a "function_response"
                            # key and a specific structure for the response payload.
                            {
                                "function_response": {
                                    "name": tool_name,
                                    "response": {"content": tool_response},
                                }
                            },
                        ]
                    )
                else:
                    print(f"--- TOOL NOT FOUND: {tool_name} ---")
                    # If the tool is not found, we return an error message to the LLM
                    result = self.llm.generate_content(
                        [
                            result.candidates[0].content,
                            {
                                "function_response": {
                                    "name": tool_name,
                                    "response": {"content": f"Error: Tool '{tool_name}' not found."},
                                }
                            },
                        ]
                    )

            return result.text

        except Exception as e:
            print(f"--- LLM GENERATION FAILED for {self.agent_name}: {e} ---")
            return f"[LLM Generation Failed: {e}]"

    def run(self, *args, **kwargs):
        """
        The main method for an agent. This should be implemented by subclasses.
        """
        raise NotImplementedError("The run method must be implemented by a subclass.")
