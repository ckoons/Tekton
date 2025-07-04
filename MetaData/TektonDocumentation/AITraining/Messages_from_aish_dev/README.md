# Messages from aish Development

This directory enables communication between aish developers and AI terminals during debugging and testing.

## How It Works

1. **Check for Requests**: Look in the `requests/` directory for test requests or questions
2. **Provide Feedback**: Create response files in `responses/` directory
3. **File Naming**: Use format `YYYY-MM-DD_yourname_topic.md`

## Current Status

We're debugging the inbox system. New terminals (Jane, Ann) should have working inbox operations while older terminals (Alice, Bob, Betty, Wilma, Kari) need restart.

## Example Response Format

```markdown
# Inbox Test Results - Jane
Date: 2025-07-04
Terminal: Jane

## Tests Performed
1. inbox new pop - [PASS/FAIL]
2. inbox keep push - [PASS/FAIL]
3. inbox keep write - [PASS/FAIL]

## Observations
- What worked well
- What didn't work
- Error messages seen

## Suggestions
- Ideas for improvement
```

Please check the `requests/` directory for specific test requests!