#!/usr/bin/env python3
"""
Test Tekton UI Component Instrumentation

This tool validates that components follow the semantic tagging patterns
defined in INSTRUMENTATION_PATTERNS.md
"""
import os
import sys
import glob
import re
from typing import Dict, List, Tuple

class InstrumentationTester:
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        
    def test_component(self, filepath: str) -> Dict:
        """Test a single component file"""
        component_name = os.path.basename(filepath).replace('-component.html', '')
        
        with open(filepath, 'r') as f:
            content = f.read()
            
        results = {
            'component': component_name,
            'filepath': filepath,
            'tests': {},
            'score': 0,
            'max_score': 0
        }
        
        # Test 1: Has root area tag
        results['tests']['has_area'] = self._test_has_area(content, component_name)
        
        # Test 2: Has component tag
        results['tests']['has_component'] = self._test_has_component(content, component_name)
        
        # Test 3: Has zones
        results['tests']['has_zones'] = self._test_has_zones(content)
        
        # Test 4: Has proper navigation (if menu exists)
        results['tests']['has_navigation'] = self._test_has_navigation(content)
        
        # Test 5: Has proper panels (if panels exist)
        results['tests']['has_panels'] = self._test_has_panels(content)
        
        # Test 6: Has actions (if buttons exist)
        results['tests']['has_actions'] = self._test_has_actions(content)
        
        # Calculate score
        for test, result in results['tests'].items():
            results['max_score'] += result['weight']
            if result['passed']:
                results['score'] += result['weight']
                
        results['percentage'] = (results['score'] / results['max_score'] * 100) if results['max_score'] > 0 else 0
        
        return results
    
    def _test_has_area(self, content: str, component_name: str) -> Dict:
        """Test if component has data-tekton-area"""
        pattern = f'data-tekton-area="{component_name}"'
        has_area = pattern in content
        
        return {
            'passed': has_area,
            'weight': 10,
            'message': f"Has data-tekton-area=\"{component_name}\"" if has_area else f"Missing data-tekton-area=\"{component_name}\""
        }
    
    def _test_has_component(self, content: str, component_name: str) -> Dict:
        """Test if component has data-tekton-component"""
        pattern = f'data-tekton-component="{component_name}"'
        has_component = pattern in content
        
        return {
            'passed': has_component,
            'weight': 10,
            'message': f"Has data-tekton-component=\"{component_name}\"" if has_component else f"Missing data-tekton-component=\"{component_name}\""
        }
    
    def _test_has_zones(self, content: str) -> Dict:
        """Test if component has proper zones"""
        zones = re.findall(r'data-tekton-zone="([^"]+)"', content)
        unique_zones = set(zones)
        
        required_zones = {'header', 'content'}  # Minimum required
        optional_zones = {'menu', 'footer'}
        
        has_required = required_zones.issubset(unique_zones)
        zone_count = len(unique_zones)
        
        if has_required:
            message = f"Has {zone_count} zones: {', '.join(sorted(unique_zones))}"
        else:
            missing = required_zones - unique_zones
            message = f"Missing required zones: {', '.join(missing)}"
            
        return {
            'passed': has_required,
            'weight': 20,
            'message': message
        }
    
    def _test_has_navigation(self, content: str) -> Dict:
        """Test navigation tags if menu exists"""
        has_menu = 'data-tekton-zone="menu"' in content
        
        if not has_menu:
            return {
                'passed': True,
                'weight': 5,
                'message': "No menu zone - navigation not required"
            }
            
        # Check for menu items
        menu_items = re.findall(r'data-tekton-menu-item="([^"]+)"', content)
        
        if menu_items:
            # Check if each menu item has required attributes
            issues = []
            for item in menu_items:
                if f'data-tekton-menu-item="{item}"' in content:
                    # Check for companion attributes
                    item_section = content[content.find(f'data-tekton-menu-item="{item}"')-200:content.find(f'data-tekton-menu-item="{item}"')+200]
                    
                    if 'data-tekton-menu-active=' not in item_section:
                        issues.append(f"{item} missing active state")
                    if 'data-tekton-menu-panel=' not in item_section:
                        issues.append(f"{item} missing panel reference")
                        
            if issues:
                return {
                    'passed': False,
                    'weight': 10,
                    'message': f"Navigation issues: {'; '.join(issues[:3])}"
                }
            else:
                return {
                    'passed': True,
                    'weight': 10,
                    'message': f"Has proper navigation for {len(menu_items)} menu items"
                }
        else:
            return {
                'passed': False,
                'weight': 10,
                'message': "Has menu zone but no menu items tagged"
            }
    
    def _test_has_panels(self, content: str) -> Dict:
        """Test panel tags if panels exist"""
        panels = re.findall(r'data-tekton-panel="([^"]+)"', content)
        
        if not panels:
            # Check if component uses panels
            if '__panel' in content or '-panel' in content:
                return {
                    'passed': False,
                    'weight': 10,
                    'message': "Has panel elements but no panel tags"
                }
            else:
                return {
                    'passed': True,
                    'weight': 5,
                    'message': "No panels in component"
                }
                
        # Check panel attributes
        issues = []
        for panel in panels:
            panel_section = content[content.find(f'data-tekton-panel="{panel}"'):content.find(f'data-tekton-panel="{panel}"')+300]
            
            if 'data-tekton-panel-active=' not in panel_section:
                issues.append(f"{panel} missing active state")
                
        if issues:
            return {
                'passed': False,
                'weight': 10,
                'message': f"Panel issues: {'; '.join(issues[:3])}"
            }
        else:
            return {
                'passed': True,
                'weight': 10,
                'message': f"Has proper panel tags for {len(panels)} panels"
            }
    
    def _test_has_actions(self, content: str) -> Dict:
        """Test action tags if buttons exist"""
        button_count = content.count('<button')
        action_count = content.count('data-tekton-action=')
        
        if button_count == 0:
            return {
                'passed': True,
                'weight': 5,
                'message': "No buttons in component"
            }
            
        if action_count == 0:
            return {
                'passed': False,
                'weight': 5,
                'message': f"Has {button_count} buttons but no action tags"
            }
            
        coverage = (action_count / button_count) * 100
        
        if coverage >= 50:  # At least half the buttons should be tagged
            return {
                'passed': True,
                'weight': 5,
                'message': f"{action_count}/{button_count} buttons tagged ({coverage:.0f}%)"
            }
        else:
            return {
                'passed': False,
                'weight': 5,
                'message': f"Only {action_count}/{button_count} buttons tagged ({coverage:.0f}%)"
            }
    
    def run_all_tests(self) -> None:
        """Run tests on all components"""
        component_files = glob.glob('ui/components/**/*-component.html', recursive=True)
        
        print("🧪 Testing Tekton UI Component Instrumentation\n")
        print(f"Found {len(component_files)} components to test\n")
        
        all_results = []
        
        for filepath in sorted(component_files):
            results = self.test_component(filepath)
            all_results.append(results)
            
            # Print immediate feedback
            status = "✅" if results['percentage'] >= 80 else "⚠️" if results['percentage'] >= 50 else "❌"
            print(f"{status} {results['component']}: {results['percentage']:.0f}% ({results['score']}/{results['max_score']} points)")
            
            # Show failures
            for test_name, test_result in results['tests'].items():
                if not test_result['passed'] and test_result['weight'] >= 10:  # Only show important failures
                    print(f"   ❌ {test_result['message']}")
                    
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        passed = [r for r in all_results if r['percentage'] >= 80]
        partial = [r for r in all_results if 50 <= r['percentage'] < 80]
        failed = [r for r in all_results if r['percentage'] < 50]
        
        print(f"\n✅ Fully Instrumented ({len(passed)}):")
        for r in sorted(passed, key=lambda x: x['percentage'], reverse=True):
            print(f"   {r['component']}: {r['percentage']:.0f}%")
            
        print(f"\n⚠️  Partially Instrumented ({len(partial)}):")
        for r in sorted(partial, key=lambda x: x['percentage'], reverse=True):
            print(f"   {r['component']}: {r['percentage']:.0f}%")
            
        print(f"\n❌ Not/Poorly Instrumented ({len(failed)}):")
        for r in sorted(failed, key=lambda x: x['percentage'], reverse=True):
            print(f"   {r['component']}: {r['percentage']:.0f}%")
            
        # Overall score
        total_score = sum(r['score'] for r in all_results)
        total_max = sum(r['max_score'] for r in all_results)
        overall_percentage = (total_score / total_max * 100) if total_max > 0 else 0
        
        print(f"\n📊 Overall Instrumentation Score: {overall_percentage:.1f}%")
        print(f"   Total Points: {total_score}/{total_max}")

if __name__ == "__main__":
    tester = InstrumentationTester()
    tester.run_all_tests()