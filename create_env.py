"""
Helper script to create .env file with required properties.
"""
import os
from pathlib import Path

def create_env_file():
    """Create .env file from env.example template."""
    script_dir = Path(__file__).parent
    env_example = script_dir / "env.example"
    env_file = script_dir / ".env"
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Cancelled. .env file not created.")
            return
    
    # Read template
    with open(env_example, 'r') as f:
        template = f.read()
    
    # Create .env file
    with open(env_file, 'w') as f:
        f.write(template)
    
    print("✅ Created .env file from env.example")
    print(f"📝 Location: {env_file}")
    print("\n⚠️  IMPORTANT: Edit .env file and add your actual API keys:")
    print("   1. OPENAI_API_KEY=sk-your-actual-key")
    print("   2. LANGCHAIN_API_KEY=lsv2_pt_your-actual-key")
    print("\nGet keys from:")
    print("   - OpenAI: https://platform.openai.com/api-keys")
    print("   - LangSmith: https://smith.langchain.com/")

if __name__ == "__main__":
    create_env_file()

