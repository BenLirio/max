import os
import openai
import atexit
import pickle

openai.api_key = os.getenv('OPENAI_API_KEY')

cache = {}

def save_cache():
    pickle.dump(cache, open('cache.pkl', 'wb'))
atexit.register(save_cache)
cache = pickle.load(open('cache.pkl', 'rb'))

def complete(prompt, quality=False, lots=False, use_cache=True):
    if use_cache and (prompt, quality, lots) in cache:
        return cache[(prompt, quality, lots)]
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
    cache[(prompt, quality, lots)] = out
    return out

print(complete('Say this is a test'))
