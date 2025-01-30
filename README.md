# Unoffical DeepSeek API for Python

A reverse-engineered DeepSeek API. Fully extensible for chatbots and other applications.

---

## Installation
Install the package using pip:

```bash
pip install py-deepseek-api
```

## Usage

### Basic example (streamed):

```python
from deepseek import DeepSeekApi, Conversation

deepseek_api = DeepSeekApi(your_token_here)

conv = Conversation(deepseek_api)

conv.continuous_chat()
```

### How to Get a Token?
You can easily obtain a token using your email and password:
```python
token = deepseek_api.login(email, password)
print(token)
```

### All API methods
For detailed usage and advanced developer guides, refer to the [Wiki](https://github.com/robbinhust/deepseek-api/wiki/).

## Reporting Issues
If you encounter bugs or have feature requests, please open an issue on the [GitHub Issues page](https://github.com/robbinhust/deepseek-api/issues/). Make sure to provide detailed information and steps to reproduce the problem.

## Disclaimer
This API is intended for educational purposes only. Any use for commercial purposes is strictly prohibited without prior permission. If any violation occurs, please contact me for immediate removal.
