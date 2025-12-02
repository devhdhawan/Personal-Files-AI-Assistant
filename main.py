"""
MCP Agent Chat Application with Google Gemini

IMPORTANT: Run this script using 'uv run python app_gemini.py' to ensure
compatible package versions are used from the virtual environment.
Do NOT use 'python app_gemini.py' directly as it may use incompatible system packages.

Requires GOOGLE_API_KEY environment variable to be set in .env file.
"""
import os
import asyncio
from dotenv import load_dotenv


from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient


load_dotenv()


async def run_memory_chat():
    # Using Google Gemini Pro model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )
    
    config_file = "src/browser_mcp.json" # This is just an example, the actual file can have multiple servers
    client = MCPClient.from_config_file(config_file)
    print(client)

    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=10,
        memory_enabled=True,
    )

    print("Chatbot initialized. Type 'exit' to quit.")

    while True:
        user_message = input("You: ")
        if user_message.lower() == 'exit':
            print("Exiting...")
            break

        if user_message.lower() == 'clear':
            print("Clearing conversation history...")
            agent.clear_conversation_history()
            continue

        print("\nAssistant:", end=" ", flush=True)

        try:
            response = await agent.run(user_message)
            
            print(response)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_memory_chat())