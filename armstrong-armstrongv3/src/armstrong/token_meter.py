import openai, tiktoken, threading, time, json

_lock = threading.Lock()
usage_totals = {"prompt": 0, "completion": 0, "total": 0}

def _add_usage(u: dict):
    with _lock:
        for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
            if k in u:
                canon = k.replace("_tokens", "")
                usage_totals[canon] += u[k]

def _wrap(orig_func):
    def wrapper(*args, **kwargs):
        resp = orig_func(*args, **kwargs)
        # non-stream: usage is on the response object
        if "usage" in resp:
            _add_usage(resp["usage"])
        return resp
    return wrapper

# monkey-patch once ⬇
openai.ChatCompletion.create = _wrap(openai.ChatCompletion.create)
# If you also use text completions:
# openai.Completion.create = _wrap(openai.Completion.create)

def report_usage() -> str:
    """Call at the end of the run (or print periodically)."""
    with _lock:
        return json.dumps(usage_totals, indent=2)
