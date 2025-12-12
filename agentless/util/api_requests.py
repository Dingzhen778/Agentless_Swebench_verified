import os
import signal
import time
from typing import Dict, Union

import openai
import tiktoken

# Support custom API endpoint via environment variables
api_key = os.environ.get("OPENAI_API_KEY", "dummy-key")
base_url = os.environ.get("OPENAI_BASE_URL", None)

if base_url:
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
else:
    client = openai.OpenAI()


def num_tokens_from_messages(message, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if isinstance(message, list):
        # use last message.
        num_tokens = len(encoding.encode(message[0]["content"]))
    else:
        num_tokens = len(encoding.encode(message))
    return num_tokens


def create_chatgpt_config(
    message: Union[str, list],
    max_tokens: int,
    temperature: float = 1,
    batch_size: int = 1,
    system_message: str = "You are a helpful assistant.",
    model: str = "gpt-3.5-turbo",
) -> Dict:
    if isinstance(message, list):
        config = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "n": batch_size,
            "messages": [{"role": "system", "content": system_message}] + message,
        }
    else:
        config = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "n": batch_size,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": message},
            ],
        }
    return config


def handler(signum, frame):
    # swallow signum and frame
    raise Exception("end of time")


def request_chatgpt_engine(config):
    ret = None
    max_retries = 3
    retry_count = 0

    while ret is None and retry_count < max_retries:
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(100)
            ret = client.chat.completions.create(**config)
            signal.alarm(0)
        except openai._exceptions.BadRequestError as e:
            print(f"BadRequestError: {e}")
            signal.alarm(0)
            # Don't retry on BadRequest (usually means context too long or invalid request)
            # Return a dummy response with empty content
            class DummyChoice:
                def __init__(self):
                    self.message = type('obj', (object,), {'content': ''})()
            class DummyUsage:
                def __init__(self):
                    self.completion_tokens = 0
                    self.prompt_tokens = 0
            class DummyResponse:
                def __init__(self):
                    self.choices = [DummyChoice()]
                    self.usage = DummyUsage()
            return DummyResponse()
        except openai._exceptions.RateLimitError as e:
            print("Rate limit exceeded. Waiting...")
            print(e)
            signal.alarm(0)
            time.sleep(5)
            retry_count += 1
        except openai._exceptions.APIConnectionError as e:
            print("API connection error. Waiting...")
            signal.alarm(0)
            time.sleep(5)
            retry_count += 1
        except Exception as e:
            print("Unknown error. Waiting...")
            print(e)
            signal.alarm(0)
            time.sleep(1)
            retry_count += 1

    # If we exhausted all retries, return dummy response
    if ret is None:
        print("Max retries exceeded, returning empty response")
        class DummyChoice:
            def __init__(self):
                self.message = type('obj', (object,), {'content': ''})()
        class DummyUsage:
            def __init__(self):
                self.completion_tokens = 0
                self.prompt_tokens = 0
        class DummyResponse:
            def __init__(self):
                self.choices = [DummyChoice()]
                self.usage = DummyUsage()
        return DummyResponse()

    return ret


def create_anthropic_config(
    message: str,
    prefill_message: str,
    max_tokens: int,
    temperature: float = 1,
    batch_size: int = 1,
    system_message: str = "You are a helpful assistant.",
    model: str = "claude-2.1",
) -> Dict:
    if isinstance(message, list):
        config = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "system": system_message,
            "messages": message,
        }
    else:
        config = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "system": system_message,
            "messages": [
                {"role": "user", "content": message},
                {"role": "assistant", "content": prefill_message},
            ],
        }
    return config


def request_anthropic_engine(client, config):
    ret = None
    while ret is None:
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(100)
            ret = client.messages.create(**config)
            signal.alarm(0)
        except Exception as e:
            print("Unknown error. Waiting...")
            print(e)
            signal.alarm(0)
            time.sleep(10)
    return ret
