# -*- coding: utf-8 -*-
import sys
import google.genai as genai

api_key = sys.argv[1] if len(sys.argv) > 1 else input("API Key: ").strip()
client = genai.Client(api_key=api_key)

print("\n=== Modelos con soporte generateContent ===\n")
for m in client.models.list():
    actions = m.supported_actions or []
    if "generateContent" in actions:
        print(f"  ✅ {m.name}")

print("\n=== Todos los modelos disponibles ===\n")
for m in client.models.list():
    print(f"  {m.name}  —  {m.supported_actions}")
