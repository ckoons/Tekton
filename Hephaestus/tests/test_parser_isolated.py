"""
Isolated test to demonstrate the parser issue without dependencies
"""
from bs4 import BeautifulSoup, Tag, NavigableString


def simple_html_to_structured_data(html: str, selector: str = None, max_depth: int = 3):
    """Simplified version of _html_to_structured_data to test"""
    soup = BeautifulSoup(html, 'html.parser')
    
    if selector:
        elements = soup.select(selector)
    else:
        # This is the problem - only returns root!
        root = soup.body if soup.body else soup
        elements = [root]
    
    def extract_element_tree(element: Tag, depth: int = 0):
        if not isinstance(element, Tag) or depth > max_depth:
            return None
            
        info = {
            "tag": element.name,
            "id": element.get("id"),
            "classes": element.get("class", []),
        }
        
        # Get direct text
        direct_text = "".join([str(s) for s in element.children if isinstance(s, NavigableString)]).strip()
        if direct_text:
            info["text"] = direct_text[:100]
        
        # Process children
        child_elements = [child for child in element.children if isinstance(child, Tag)]
        if child_elements and depth < max_depth:
            info["children"] = []
            for child in child_elements[:10]:
                child_info = extract_element_tree(child, depth + 1)
                if child_info:
                    info["children"].append(child_info)
        else:
            info["child_count"] = len(child_elements)
        
        return info
    
    result = {
        "element_count": len(elements),  # THIS IS THE BUG! Always 1 for no selector
        "elements": []
    }
    
    for element in elements:
        if isinstance(element, Tag):
            el_tree = extract_element_tree(element)
            if el_tree:
                result["elements"].append(el_tree)
    
    return result


def count_total_elements(element_data):
    """Helper to count all elements in tree"""
    count = 1
    if "children" in element_data:
        for child in element_data["children"]:
            count += count_total_elements(child)
    return count


# Test HTML
TEST_HTML = '''
<html>
<body>
    <div class="navigation">
        <ul>
            <li data-component="prometheus">
                <span class="nav-label">Prometheus</span>
            </li>
            <li data-component="rhetor">
                <span class="nav-label">Rhetor</span>
            </li>
        </ul>
    </div>
    <div class="content">
        <h1>Welcome</h1>
        <p>Content here</p>
    </div>
</body>
</html>
'''

print("=== Testing Current Parser Behavior ===\n")

# Test 1: No selector (broken)
print("1. Without selector (BROKEN):")
result = simple_html_to_structured_data(TEST_HTML)
print(f"   element_count: {result['element_count']} (WRONG - only counts root)")
total = sum(count_total_elements(el) for el in result["elements"])
print(f"   actual total elements in tree: {total}")
print(f"   root element: {result['elements'][0]['tag']}")
print()

# Test 2: With selector (works)
print("2. With selector '.nav-label' (WORKS):")
result = simple_html_to_structured_data(TEST_HTML, ".nav-label")
print(f"   element_count: {result['element_count']} (CORRECT)")
print(f"   found elements: {[el['tag'] for el in result['elements']]}")
print()

# Test 3: The fix
print("3. PROPOSED FIX:")
soup = BeautifulSoup(TEST_HTML, 'html.parser')
all_elements = soup.find_all(True)  # Find ALL tags
print(f"   Total elements in HTML: {len(all_elements)}")
print(f"   Element types found: {set(el.name for el in all_elements)}")
print()

# Test 4: What the result should look like
print("4. DESIRED RESULT STRUCTURE:")
desired = {
    "html": TEST_HTML,  # Raw HTML for searching
    "total_elements": len(all_elements),
    "element_count": len(all_elements),  # Fixed count
    "selectors_found": {
        ".nav-label": len(soup.select(".nav-label")),
        "[data-component]": len(soup.select("[data-component]")),
        "li": len(soup.select("li")),
        "div": len(soup.select("div"))
    },
    "structure": result  # Keep for compatibility
}
print(f"   html: <included>")
print(f"   total_elements: {desired['total_elements']}")
print(f"   selectors_found: {desired['selectors_found']}")