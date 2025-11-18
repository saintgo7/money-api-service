"""Simple chatbot example using Money API."""
import sys
from money_api import MoneyAPI


def main():
    """Run simple chatbot."""
    # Get API key
    api_key = input("Enter your Money API key: ").strip()

    if not api_key:
        print("Error: API key is required")
        sys.exit(1)

    # Initialize client
    client = MoneyAPI(api_key=api_key)

    print("\n🤖 Money API Chatbot")
    print("Type 'quit' to exit, 'balance' to check credits\n")

    conversation_history = []

    while True:
        # Get user input
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if user_input.lower() == "balance":
            try:
                user = client.management.get_current_user()
                print(f"💰 Credit Balance: ${user['credit_balance']:.2f}")
                print(f"📊 Plan: {user['plan'].upper()}\n")
            except Exception as e:
                print(f"Error: {e}\n")
            continue

        # Add to history
        conversation_history.append(f"User: {user_input}")

        # Build context
        context = "\n".join(conversation_history[-5:])  # Last 5 messages

        try:
            # Get response
            response = client.text.complete(
                prompt=user_input,
                system="You are a helpful AI assistant. Be concise and friendly.",
                max_tokens=500,
                temperature=0.7
            )

            assistant_message = response["content"]
            cost = response["cost"]

            # Add to history
            conversation_history.append(f"Assistant: {assistant_message}")

            # Display response
            print(f"\n🤖 Assistant: {assistant_message}")
            print(f"💵 Cost: ${cost:.4f}\n")

        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
