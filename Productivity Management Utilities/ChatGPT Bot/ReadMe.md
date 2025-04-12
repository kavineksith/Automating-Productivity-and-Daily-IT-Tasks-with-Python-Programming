Here's the updated and improved documentation for the **latest version of your `ChatGPTBot`**, reflecting the changes in code (notably the switch to `openai.ChatCompletion.create`, use of `.env`, better structure, etc.):

---

# ChatGPTBot Documentation

## Overview

The `ChatGPTBot` Python script provides a conversational interface powered by OpenAI's latest `gpt-3.5-turbo` (or `gpt-4`) model. It enables users to interact with a role-aware chatbot in a console environment, with features for role-switching, conversation persistence, user role management, and graceful error handling. This script is ideal for prototyping conversational assistants or educational exploration of LLM capabilities.

---

## Features

- **💬 Role-Based Interaction**: Switch between predefined chatbot roles such as:
  - `Friendly Assistant`: Polite, helpful, everyday conversations.
  - `Technical Support`: Focused on troubleshooting and technical answers.
  - `Expert Advisor`: Offers professional and high-level advice.

- **👥 User Role Management**: Choose between `general` and `admin` user roles to tailor the chatbot experience.

- **🧠 Persistent Chat History**: Saves your full conversation to `chat_history.json` and reloads it in the next session.

- **⚠️ Robust Error Handling**: Custom exceptions for invalid role selection, OpenAI API issues, and file I/O errors.

- **⌨️ Interactive Console Commands**: Modify the role and user role during an ongoing session using simple typed commands.

---

## Dependencies

| Package       | Purpose                          |
|---------------|----------------------------------|
| `openai`      | Interface with OpenAI's API      |
| `python-dotenv` | Load the API key from `.env`    |

### Install Dependencies

```bash
pip install openai python-dotenv
```

---

## Setup Instructions

1. **Create a `.env` File**  
   Add your OpenAI API key to a file named `.env` in the same directory as the script:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

2. **Run the Script**
   ```bash
   python gpt_bot.py
   ```

3. **Available Commands**
   - `role <role_name>`: Change the chatbot’s behavior.
   - `userrole <role_name>`: Change your user role.
   - `exit`: Quit the chatbot and save the session.

---

## Interactive Commands

### Role Management
| Command Example             | Description                                      |
|----------------------------|--------------------------------------------------|
| `role Technical Support`   | Sets the bot to a tech support role              |
| `role Expert Advisor`      | Switches the bot to professional advisory mode   |

### User Role Management
| Command Example             | Description                                      |
|----------------------------|--------------------------------------------------|
| `userrole admin`           | Assigns user role with elevated privileges       |
| `userrole general`         | Standard user interaction                        |

### Exit
| Command      | Description                                |
|--------------|--------------------------------------------|
| `exit`       | Ends the session and saves the chat log    |

---

## Method Reference

### `set_role(role_name)`
Changes the chatbot's system behavior to one of the predefined roles.  
**Raises:** `RoleError` if the input is invalid.

### `set_user_role(user_role)`
Sets the current user role.  
**Raises:** `UserRoleError` for invalid entries.

### `get_response(user_input)`
Generates a response using OpenAI's `ChatCompletion` API with the conversation history.  
**Raises:** `OpenAIRequestError` if the API call fails.

### `save_history(filename='chat_history.json')`
Saves the entire chat history to disk.  
**Raises:** `ChatGPTBotError` on file write error.

### `load_history(filename='chat_history.json')`
Loads previous session history from disk if available.  
**Raises:** `ChatGPTBotError` on read/parse errors.

---

## File Structure

```
project/
│
├── gpt_bot.py             # Main script
├── .env                   # Contains your API key
├── chat_history.json      # Automatically generated conversation log
├── requirements.txt       # (Optional) Package dependencies
```

---

## Example Usage

```bash
$ python gpt_bot.py
ChatGPT Console Application (v2)
Type 'exit' to end the chat.
Type 'role <role_name>' to change the chatbot's role.
Type 'userrole <role_name>' to change the user role.

You: role Expert Advisor
> Role changed to Expert Advisor.

You: How should I structure a business plan?
Expert Advisor: Here's how you can structure a business plan...
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

## Disclaimer

This project is developed **for educational purposes only**. It is not intended for production or commercial use. The authors do **not assume responsibility for misuse or commercial deployment**. Please use responsibly and ethically.

Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.