#!/usr/bin/env python3
"""
Test script to simulate Claude-like output to test flicker prevention.
"""
import sys
import time

# Simulate Claude generating tokens
print("Starting simulated Claude output...")
sys.stdout.flush()
time.sleep(0.5)

# Rapid token generation (like Claude streaming)
tokens = ["Hello", " there", "!", " I'm", " generating", " tokens", " like", " Claude", " would", ".",
          "\n", "This", " should", " be", " frozen", " during", " generation", ".", "\n"]

for token in tokens:
    print(token, end='', flush=True)
    time.sleep(0.05)  # 50ms between tokens

print("\n\nDone with output generation!")
print("You should have seen minimal flicker during the token streaming.")