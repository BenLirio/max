import os
import openai
import atexit
import pickle

openai.api_key = os.getenv('OPENAI_API_KEY')

_cache = {}

def save_cache():
    pickle.dump(_cache, open('cache.pkl', 'wb'))
atexit.register(save_cache)
_cache = pickle.load(open('cache.pkl', 'rb'))

def complete(prompt, quality=False, lots=False, cache=True):
    if cache and (prompt, quality, lots) in _cache:
        return _cache[(prompt, quality, lots)]
    max_tokens = 16
    if lots:
        max_tokens = 64
    engine = 'text-curie-001'
    if quality:
        engine = 'text-davinci-001'
    res = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=max_tokens
            )
    out = res.choices[0].text.strip()
    _cache[(prompt, quality, lots)] = out
    return out
