import openai
import os
import json
import sys
from dotenv import load_dotenv

# Load API key from .env file or environment
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Custom Exception Classes
class ChatGPTBotError(Exception):
    """Base class for all exceptions raised by ChatGPTBot."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class RoleError(ChatGPTBotError):
    def __init__(self, role_name):
        super().__init__(f"Invalid role: {role_name}")

class UserRoleError(ChatGPTBotError):
    def __init__(self, user_role):
        super().__init__(f"Invalid user role: {user_role}")

class OpenAIRequestError(ChatGPTBotError):
    def __init__(self, message):
        super().__init__(f"OpenAI request error: {message}")

class ChatGPTBot:
    def __init__(self, model="gpt-3.5-turbo", temperature=0.7, max_tokens=150):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history = []
        self.current_role = "Friendly Assistant"
        self.roles = {
            "Friendly Assistant": "You are a friendly assistant who provides helpful and polite responses.",
            "Technical Support": "You are a technical support agent who provides detailed and technical assistance.",
            "Expert Advisor": "You are an expert advisor offering professional and high-level advice."
        }
        self.users = {
            "general": "Regular users seeking help or information.",
            "admin": "Users with elevated permissions, capable of managing the system or accessing advanced features."
        }
        self.current_role_description = self.roles[self.current_role]

    def set_role(self, role_name):
        if role_name in self.roles:
            self.current_role = role_name
            self.current_role_description = self.roles[role_name]
            self.history.append({"role": "system", "content": f"Role changed to: {self.current_role}"})
            return f"Role changed to {self.current_role}."
        else:
            raise RoleError(role_name)

    def set_user_role(self, user_role):
        if user_role in self.users:
            self.history.append({"role": "system", "content": f"User role changed to: {user_role}"})
            return f"User role changed to {user_role}."
        else:
            raise UserRoleError(user_role)

    def get_response(self, user_input):
        try:
            messages = [{"role": "system", "content": self.current_role_description}] + self.history
            messages.append({"role": "user", "content": user_input})

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            reply = response.choices[0].message["content"].strip()
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            raise OpenAIRequestError(str(e))

    def save_history(self, filename='chat_history.json'):
        try:
            with open(filename, 'w') as file:
                json.dump(self.history, file, indent=4)
        except IOError as e:
            raise ChatGPTBotError(f"Error saving history: {str(e)}")

    def load_history(self, filename='chat_history.json'):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as file:
                    self.history = json.load(file)
            except IOError as e:
                raise ChatGPTBotError(f"Error loading history: {str(e)}")
            except json.JSONDecodeError as e:
                raise ChatGPTBotError(f"Error decoding history file: {str(e)}")
        else:
            self.history = []

def chat():
    bot = ChatGPTBot()
    try:
        bot.load_history()
    except ChatGPTBotError as e:
        print(f"Warning: {e}")

    print("ChatGPT Console Application (v2)")
    print("Type 'exit' to end the chat.")
    print("Type 'role <role_name>' to change the chatbot's role.")
    print("Type 'userrole <role_name>' to change the user role.")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Goodbye!")
                bot.save_history()
                break

            if user_input.lower().startswith('role '):
                role_name = user_input[5:].strip()
                response = bot.set_role(role_name)
                print(response)
            elif user_input.lower().startswith('userrole '):
                user_role = user_input[9:].strip()
                response = bot.set_user_role(user_role)
                print(response)
            else:
                response = bot.get_response(user_input)
                print(f"{bot.current_role}: {response}")
        except (RoleError, UserRoleError, OpenAIRequestError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    chat()
    sys.exit(0)
