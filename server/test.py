#!/usr/bin/env python3
"""Quick test — makes a direct API call using the public URL from .env"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))
from config import GEMMA_URL, GEMMA_API_KEY
from openai import OpenAI

client = OpenAI(base_url=GEMMA_URL, api_key=GEMMA_API_KEY)

print(f"Server : {GEMMA_URL}")
print(f"Key    : {GEMMA_API_KEY[:12]}...")
print("-" * 50)

response = client.chat.completions.create(
    model="gemma",
    messages=[{"role": "user", "content": "Can you compare CD8T and CD4T aging signatures?"}],
    max_tokens=1024,
)

print(response.choices[0].message.content)

