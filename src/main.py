#!/usr/bin/env python3
"""CLI entry point for the ggssgs251 multi-agent system.

Run with: python -m src.main
Or after installing: ggssgs251

Requires Ollama running locally with a model pulled (e.g., llama3.1).
"""

import sys

from strands.models.ollama import OllamaModel

from src.orchestrator import create_swarm, run_swarm


def main() -> None:
    """Main entry point for the CLI application."""
    # Configuration
    ollama_host = "http://localhost:11434"
    ollama_model_id = "llama3.1"  # Change to your preferred Ollama model

    print("=" * 60)
    print("  🤖 ggssgs251 — Multi-Agent AI System")
    print("  Orchestrator • Data Tutor • Code Advisor")
    print("=" * 60)
    print()
    print(f"🔗 Ollama: {ollama_host}")
    print(f"🧠 Model:  {ollama_model_id}")
    print()
    print("Supported commands:")
    print("  /quit          — Exit the application")
    print("  /model <name>  — Switch to a different Ollama model")
    print()
    print("Just type your question and the orchestrator will route it")
    print("to the right specialist agent (Data Tutor or Code Advisor).")
    print()

    # Initialize the Ollama model
    model = OllamaModel(
        host=ollama_host,
        model_id=ollama_model_id,
        temperature=0.7,
    )

    # Create the swarm
    swarm = create_swarm(model)

    # Interactive REPL
    while True:
        try:
            user_input = input("🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "/q"):
            print("👋 Goodbye!")
            break

        if user_input.startswith("/model "):
            new_model = user_input[7:].strip()
            if new_model:
                model.update_config(model_id=new_model)
                print(f"✅ Switched model to: {new_model}")
            continue

        print()
        print("🤖 Processing...")
        print()

        try:
            # Run the swarm
            result = run_swarm(swarm, user_input)
            print(f"✅ Done! Swarm result status: {result.status.value}")
            print()

            # Print the node history to show the routing path
            if hasattr(result, "node_history") and result.node_history:
                path = " → ".join(node.node_id for node in result.node_history)
                print(f"🔄 Routing path: {path}")
                print()

        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            print("💡 Make sure Ollama is running and the model is pulled.")
            print(f"   > ollama pull {ollama_model_id}")
            print(f"   > ollama serve")
            print()


if __name__ == "__main__":
    main()
