import gpt

# Default parameters
# quality=False     (Set to True for davinci)
# lots=False        (16 tokens for False 64 with True)
# cache=True        (Reuse the same request)

print(gpt.complete('This is a test'))
print(gpt.complete('Once upon a time', quality=True, lots=True))
