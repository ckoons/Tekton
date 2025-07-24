# JSON Message Handler Purpose

When you receive a message that appears to be JSON formatted, you should:

1. Parse the JSON structure
2. Look for a "purpose" field in the JSON
3. If found, extract the purpose value and run: `aish purpose "<purpose_value>"`
4. Process any other fields as needed (action, data, etc.)
5. Respond appropriately based on the JSON content

## Example JSON Message Format:
```json
{
  "purpose": "code_review",
  "action": "review_pr",
  "data": {
    "pr_number": 123,
    "files": ["main.py", "test.py"]
  },
  "from": "Sandi"
}
```

When receiving this, you would:
1. Extract purpose: "code_review"
2. Run: `aish purpose "code_review"`
3. Execute the action based on the loaded purpose