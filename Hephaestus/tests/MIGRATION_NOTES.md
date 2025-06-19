# Test Migration Notes

## Migration Summary
All test files have been moved from various locations to `/Hephaestus/tests/` directory.

## Files Moved (20 total - test_ui_devtools.py removed as redundant):
1. From `/Hephaestus/`:
   - test_parser_isolated.py
   - test_rhetor_capture.py
   - test_rhetor_footer_change.py (formerly acid_test.py)
   - test_rhetor_nav_and_capture.py
   - test_rhetor_semantic_tags.py
   - test_ui_devtools_enhanced.py

2. From `/Hephaestus/hephaestus/mcp/`:
   - test_phase3.py

3. From `/Hephaestus/hephaestus/mcp/tests/`:
   - run_tests.py
   - test_batch_debug.py
   - test_phase1_enhancements.py
   - test_phase3_architecture_mapping.py
   - test_ui_capture_fix.py
   - test_ui_capture_improvements.py
   - test_ui_tools.py
   - test_all.sh
   - README.md
   - __init__.py

## Import Path Updates
Updated sys.path.insert statements in 4 files:
- test_phase3.py
- test_phase3_architecture_mapping.py
- test_phase1_enhancements.py
- test_ui_capture_fix.py

### Old pattern:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
```

### New pattern:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../hephaestus/mcp'))
```

## Test Types
1. **Integration Tests** (use HTTP, no path changes needed):
   - test_rhetor_*.py
   - test_ui_devtools*.py
   - test_batch_debug.py
   - run_tests.py

2. **Unit Tests** (import modules directly, needed path updates):
   - test_phase1_enhancements.py
   - test_phase3.py
   - test_phase3_architecture_mapping.py
   - test_ui_capture_fix.py
   - test_ui_tools.py

## Running Tests
- Integration tests: Can be run directly with Python
- Unit tests: Use pytest or run_tests.py
- All tests: Use test_all.sh script

## Notes
- ui_devtools_client.py remains in /Hephaestus/ as it's a client SDK, not a test
- The empty /hephaestus/mcp/tests/ directory has been removed