/**
 * Add Interactive Element Tags Script
 * Adds semantic tags to buttons, forms, and other interactive elements
 * Part of the Tekton UI semantic navigation infrastructure
 */

const fs = require('fs');
const path = require('path');

// Interactive element patterns and their semantic tags
const INTERACTIVE_PATTERNS = [
    {
        // Buttons without data-tekton-action
        pattern: /<button[^>]+(?!data-tekton-action)[^>]*>/g,
        getTag: (element) => {
            // Extract button text or id for context
            const idMatch = element.match(/id="([^"]+)"/);
            const classMatch = element.match(/class="[^"]*button[^"]*"/);
            
            if (idMatch) {
                const id = idMatch[1];
                let actionType = 'action';
                
                // Determine action type based on ID or class
                if (id.includes('save') || id.includes('submit')) actionType = 'save';
                else if (id.includes('cancel') || id.includes('close')) actionType = 'cancel';
                else if (id.includes('delete') || id.includes('remove')) actionType = 'delete';
                else if (id.includes('refresh') || id.includes('reload')) actionType = 'refresh';
                else if (id.includes('add') || id.includes('create')) actionType = 'create';
                
                return `data-tekton-action="${actionType}"`;
            }
            return null;
        },
        description: 'Button actions'
    },
    {
        // Input fields without data-tekton-input
        pattern: /<input[^>]+type="(?:text|email|password|number|search)"[^>]*(?!data-tekton-input)[^>]*>/g,
        getTag: (element) => {
            const idMatch = element.match(/id="([^"]+)"/);
            const typeMatch = element.match(/type="([^"]+)"/);
            
            if (idMatch) {
                const id = idMatch[1];
                const type = typeMatch ? typeMatch[1] : 'text';
                
                // Don't tag chat inputs (already tagged)
                if (id.includes('chat')) return null;
                
                let inputType = type;
                if (id.includes('search')) inputType = 'search';
                else if (id.includes('filter')) inputType = 'filter';
                else if (id.includes('config') || id.includes('setting')) inputType = 'config';
                
                return `data-tekton-input="${inputType}"`;
            }
            return null;
        },
        description: 'Input fields'
    },
    {
        // Select dropdowns
        pattern: /<select[^>]+(?!data-tekton-select)[^>]*>/g,
        getTag: (element) => {
            const idMatch = element.match(/id="([^"]+)"/);
            if (idMatch) {
                const id = idMatch[1];
                let selectType = 'option';
                
                if (id.includes('filter')) selectType = 'filter';
                else if (id.includes('sort')) selectType = 'sort';
                else if (id.includes('config') || id.includes('setting')) selectType = 'config';
                
                return `data-tekton-select="${selectType}"`;
            }
            return null;
        },
        description: 'Select dropdowns'
    },
    {
        // Forms without data-tekton-form
        pattern: /<form[^>]+(?!data-tekton-form)[^>]*>/g,
        getTag: (element) => {
            const idMatch = element.match(/id="([^"]+)"/);
            const classMatch = element.match(/class="([^"]+)"/);
            
            if (idMatch || classMatch) {
                const identifier = idMatch ? idMatch[1] : classMatch[1];
                let formType = 'input';
                
                if (identifier.includes('config') || identifier.includes('settings')) formType = 'config';
                else if (identifier.includes('search')) formType = 'search';
                else if (identifier.includes('create') || identifier.includes('add')) formType = 'create';
                
                return `data-tekton-form="${formType}"`;
            }
            return null;
        },
        description: 'Forms'
    }
];

// Add a tag to an element if it doesn't already have it
function addTagToElement(element, tag) {
    if (!tag) return element;
    
    // Check if a similar tag already exists
    const tagName = tag.split('=')[0];
    if (element.includes(tagName)) {
        return element; // Already has this type of tag
    }
    
    // Insert before the closing >
    const insertPos = element.lastIndexOf('>');
    return element.slice(0, insertPos) + ' ' + tag + element.slice(insertPos);
}

// Process a component HTML file
function processComponent(componentName, filePath) {
    console.log(`\nProcessing ${componentName}...`);
    
    try {
        let content = fs.readFileSync(filePath, 'utf8');
        let modified = false;
        let tagCount = 0;
        
        INTERACTIVE_PATTERNS.forEach(({ pattern, getTag, description }) => {
            const matches = [...content.matchAll(pattern)];
            
            matches.forEach(match => {
                const element = match[0];
                const tag = getTag(element);
                
                if (tag) {
                    const newElement = addTagToElement(element, tag);
                    if (newElement !== element) {
                        content = content.replace(element, newElement);
                        modified = true;
                        tagCount++;
                        console.log(`  ✓ Added ${tag} to ${description}`);
                    }
                }
            });
        });
        
        // Special handling for navigation links
        const navLinkPattern = /<a[^>]+href="#"[^>]*onclick="[^"]*switchTab[^"]*"[^>]*>/g;
        const navMatches = [...content.matchAll(navLinkPattern)];
        
        navMatches.forEach(match => {
            const element = match[0];
            if (!element.includes('data-tekton-nav-link')) {
                const newElement = addTagToElement(element, 'data-tekton-nav-link="tab"');
                content = content.replace(element, newElement);
                modified = true;
                tagCount++;
                console.log(`  ✓ Added data-tekton-nav-link="tab" to navigation link`);
            }
        });
        
        if (modified) {
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`  📊 Total tags added: ${tagCount}`);
        } else {
            console.log(`  ℹ️  No interactive elements need tagging`);
        }
        
    } catch (error) {
        console.error(`  ✗ Error processing ${componentName}:`, error.message);
    }
}

// Main execution
function main() {
    console.log('Adding Interactive Element Tags...');
    console.log('=====================================\n');
    
    const componentsDir = path.join(__dirname, '..', 'ui', 'components');
    const components = fs.readdirSync(componentsDir)
        .filter(dir => fs.statSync(path.join(componentsDir, dir)).isDirectory())
        .filter(dir => !['shared', 'test'].includes(dir));
    
    console.log(`Components to process: ${components.length}`);
    
    components.forEach(componentName => {
        const htmlFile = path.join(componentsDir, componentName, `${componentName}-component.html`);
        if (fs.existsSync(htmlFile)) {
            processComponent(componentName, htmlFile);
        }
    });
    
    // Also process main navigation in index.html
    console.log('\nProcessing main navigation...');
    const indexPath = path.join(__dirname, '..', 'ui', 'index.html');
    if (fs.existsSync(indexPath)) {
        processComponent('index', indexPath);
    }
    
    console.log('\n=====================================');
    console.log('✨ Interactive element tagging complete!');
    console.log('\nNext steps:');
    console.log('1. Review the tagged elements');
    console.log('2. Test interactive navigation with UI DevTools');
    console.log('3. Fine-tune any specific interaction patterns');
}

// Run the script
main();