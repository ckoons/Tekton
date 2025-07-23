/**
 * Add Chat Interface Tags Script
 * Adds data-tekton-chat tags to chat interface elements
 * Part of the Tekton UI semantic navigation infrastructure
 */

const fs = require('fs');
const path = require('path');

// Components that need chat tags
const COMPONENTS_WITH_CHAT = [
    'budget', 'engram', 'prometheus', 'metis', 'harmonia', 
    'synthesis', 'sophia', 'ergon', 'telos', 'hermes', 
    'codex', 'settings', 'profile'
];

// Chat element patterns and their tags
const CHAT_PATTERNS = [
    {
        pattern: /class="[^"]*chat-messages[^"]*"/g,
        addTag: 'data-tekton-chat="messages"',
        description: 'Chat messages container'
    },
    {
        pattern: /class="[^"]*chat-input[^"]*"/g,
        addTag: 'data-tekton-chat="input"',
        description: 'Chat input field'
    },
    {
        pattern: /id="[^"]*chat-panel[^"]*"/g,
        addTag: 'data-tekton-chat="panel"',
        description: 'Chat panel container'
    },
    {
        pattern: /data-tab="[^"]*chat[^"]*"/g,
        addTag: 'data-tekton-chat="tab"',
        description: 'Chat tab button'
    }
];

// Add a tag to an element if it doesn't already have it
function addTagToElement(element, tag) {
    // Check if the tag already exists
    const tagName = tag.split('=')[0];
    if (element.includes(tagName)) {
        return element; // Already has this tag
    }
    
    // Find where to insert the tag (after class or at the end of opening tag)
    let insertPos;
    const classMatch = element.match(/class="[^"]*"/);
    if (classMatch) {
        insertPos = element.indexOf(classMatch[0]) + classMatch[0].length;
    } else {
        // Insert before the closing >
        insertPos = element.lastIndexOf('>');
    }
    
    return element.slice(0, insertPos) + ' ' + tag + element.slice(insertPos);
}

// Process a component HTML file
function processComponent(componentName, filePath) {
    console.log(`\nProcessing ${componentName}...`);
    
    try {
        let content = fs.readFileSync(filePath, 'utf8');
        let modified = false;
        let tagCount = 0;
        
        CHAT_PATTERNS.forEach(({ pattern, addTag, description }) => {
            const matches = content.match(pattern);
            if (matches) {
                matches.forEach(match => {
                    // Find the full element containing this match
                    const startIndex = content.lastIndexOf('<', content.indexOf(match));
                    const endIndex = content.indexOf('>', content.indexOf(match)) + 1;
                    const element = content.substring(startIndex, endIndex);
                    
                    const newElement = addTagToElement(element, addTag);
                    if (newElement !== element) {
                        content = content.replace(element, newElement);
                        modified = true;
                        tagCount++;
                        console.log(`  ✓ Added ${addTag} to ${description}`);
                    }
                });
            }
        });
        
        // Special handling for chat interface containers
        // Look for divs containing chat-related IDs or classes
        const chatContainerPattern = /<div[^>]+(?:id|class)="[^"]*chat[^"]*"[^>]*>/g;
        let chatMatch;
        while ((chatMatch = chatContainerPattern.exec(content)) !== null) {
            const element = chatMatch[0];
            if (!element.includes('data-tekton-chat')) {
                // Determine the type based on the element
                let chatType = 'container';
                if (element.includes('messages')) chatType = 'messages';
                else if (element.includes('input')) chatType = 'input';
                else if (element.includes('panel')) chatType = 'panel';
                
                const newElement = addTagToElement(element, `data-tekton-chat="${chatType}"`);
                if (newElement !== element) {
                    content = content.replace(element, newElement);
                    modified = true;
                    tagCount++;
                    console.log(`  ✓ Added data-tekton-chat="${chatType}" to chat container`);
                }
            }
        }
        
        if (modified) {
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`  📊 Total tags added: ${tagCount}`);
        } else {
            console.log(`  ℹ️  No changes needed (chat tags may already exist)`);
        }
        
    } catch (error) {
        console.error(`  ✗ Error processing ${componentName}:`, error.message);
    }
}

// Main execution
function main() {
    console.log('Adding Chat Interface Tags...');
    console.log('=====================================\n');
    
    const componentsDir = path.join(__dirname, '..', 'ui', 'components');
    
    console.log(`Components to process: ${COMPONENTS_WITH_CHAT.join(', ')}`);
    
    COMPONENTS_WITH_CHAT.forEach(componentName => {
        const htmlFile = path.join(componentsDir, componentName, `${componentName}-component.html`);
        if (fs.existsSync(htmlFile)) {
            processComponent(componentName, htmlFile);
        } else {
            console.log(`\n⚠ No HTML file found for ${componentName}`);
        }
    });
    
    console.log('\n=====================================');
    console.log('✨ Chat tagging complete!');
    console.log('\nNext steps:');
    console.log('1. Run verify-semantic-tags.js to check all tags');
    console.log('2. Test chat navigation with UI DevTools');
    console.log('3. Add any additional interactive element tags');
}

// Run the script
main();