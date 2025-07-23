# Dev Sprint: `aish purpose "message"` Search Enhancement

## Goal
Enhance `aish purpose` to search for and display purpose content when given a string argument.

## Current Behavior
- `aish purpose` - shows current terminal's purpose
- `aish purpose bari` - shows terminal bari's purpose
- `aish purpose bari "coding"` - sets bari's purpose to "coding"

## New Behavior to Add
- `aish purpose "forward"` - searches for and displays purpose content named "forward"
- If the argument is NOT a known terminal name, treat it as a purpose search
- Search in these locations (in order):
  1. `.tekton/playbook/` (local project-specific purposes)
  2. `MetaData/Documentation/AIPurposes/text/` (shared text purposes)
  3. `MetaData/Documentation/AIPurposes/json/` (shared JSON purposes)
- Display all matching files found

## Implementation Note
Since shell strips quotes, detect by checking if the argument is a terminal name first. If not, assume it's a purpose search.

## Test Cases
1. `aish purpose forward` - should find and display forward.json and forward.md
2. `aish purpose code-review` - should find and display code-review.txt
3. `aish purpose bari` - should still show bari terminal's purpose (if bari exists)
4. `aish purpose unknown` - should search for 'unknown' purpose content

## Success Criteria
- Seamless fallback from terminal lookup to purpose search
- Display content from all matching files across search locations
- Maintain backward compatibility with existing terminal purpose functionality