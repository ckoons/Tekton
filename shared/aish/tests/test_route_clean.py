#!/usr/bin/env python3
"""
Clean test suite for aish route command
Tests core functionality with clear pass/fail reporting
"""
import subprocess
import json
import os
import sys

# Setup
TEKTON_ROOT = "/Users/cskoons/projects/github/Coder-C"
AISH = f"{TEKTON_ROOT}/shared/aish/aish"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

class RouteTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.clean_session()
    
    def clean_session(self):
        """Start fresh session"""
        os.system(f"rm -f {TEKTON_ROOT}/.tekton/aish/.session_active")
        os.system(f"rm -f {TEKTON_ROOT}/.tekton/aish/routes.json")
    
    def run_cmd(self, cmd):
        """Run command and return (success, output)"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def test(self, name, cmd, check_fn):
        """Run a test case"""
        success, output = self.run_cmd(cmd)
        
        if check_fn(success, output):
            print(f"{GREEN}✓{ENDC} {name}")
            self.passed += 1
        else:
            print(f"{RED}✗{ENDC} {name}")
            print(f"  Command: {cmd}")
            print(f"  Output: {output}")
            self.failed += 1
    
    def run_tests(self):
        """Run all tests"""
        print("=== AISH ROUTE TEST SUITE ===\n")
        
        # Test 1: Empty list
        self.test("Empty route list",
                  f"{AISH} route list",
                  lambda s, o: s and "No routes defined" in o)
        
        # Test 2: Create simple route
        self.test("Create simple route",
                  f"{AISH} route name test numa tekton",
                  lambda s, o: s and "Route 'test' created: numa → tekton" in o)
        
        # Test 3: List shows route
        self.test("List shows created route",
                  f"{AISH} route list",
                  lambda s, o: s and "test: numa → tekton" in o)
        
        # Test 4: Create route with purposes
        self.test("Create route with multi-word purposes",
                  f'{AISH} route name review numa purpose "code analysis" apollo purpose "risk check" tekton',
                  lambda s, o: s and "Route 'review' created: numa → apollo → tekton" in o)
        
        # Test 5: Show route details
        success, output = self.run_cmd(f"{AISH} route show review")
        self.test("Show displays purposes correctly",
                  f"{AISH} route show review",
                  lambda s, o: s and 'Purpose: "code analysis"' in o and 'Purpose: "risk check"' in o)
        
        # Test 6: Send message (JSON output)
        success, output = self.run_cmd(f'{AISH} route tekton "Hello"')
        try:
            data = json.loads(output)
            json_valid = data.get("message") == "Hello" and data.get("dest") == "tekton"
        except:
            json_valid = False
        
        self.test("Message produces valid JSON",
                  f'{AISH} route tekton "Hello"',
                  lambda s, o: s and json_valid)
        
        # Test 7: Named route adds metadata
        success, output = self.run_cmd(f'{AISH} route name review tekton "Check this"')
        try:
            data = json.loads(output)
            has_route = data.get("route_name") == "review"
            has_next = data.get("next_hop") == "numa"
            has_purpose = data.get("purpose") == "code analysis"
        except:
            has_route = has_next = has_purpose = False
        
        self.test("Named route adds correct metadata",
                  f'{AISH} route name review tekton "Check this"',
                  lambda s, o: s and has_route and has_next and has_purpose)
        
        # Test 8: Route progression
        json_msg = '{"message": "test", "annotations": [{"author": "numa", "content": "done"}]}'
        success, output = self.run_cmd(f"{AISH} route name review tekton '{json_msg}'")
        try:
            data = json.loads(output)
            next_is_apollo = data.get("next_hop") == "apollo"
        except:
            next_is_apollo = False
        
        self.test("Route progresses to next hop",
                  f"{AISH} route name review tekton '{json_msg}'",
                  lambda s, o: s and next_is_apollo)
        
        # Test 9: Remove route
        self.test("Remove route",
                  f"{AISH} route remove test",
                  lambda s, o: s and "Route 'test' removed" in o)
        
        # Test 10: Invalid route name
        self.test("Invalid route name error",
                  f'{AISH} route name invalid tekton "msg"',
                  lambda s, o: s and "No route named 'invalid' to tekton" in o)
        
        # Summary
        print(f"\n=== SUMMARY ===")
        print(f"Passed: {GREEN}{self.passed}{ENDC}")
        print(f"Failed: {RED}{self.failed}{ENDC}")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = RouteTest()
    success = tester.run_tests()
    sys.exit(0 if success else 1)