/**
 * Systematic Component Tagging Script
 * Adds semantic data-tekton-* tags to all component HTML files
 * Part of the Tekton UI semantic navigation infrastructure
 */

const fs = require('fs');
const path = require('path');

// Component configurations with their CI specialist mappings
const COMPONENT_CONFIGS = {
    'athena': { specialist: 'athena-assistant', description: 'Knowledge Graph' },
    'apollo': { specialist: 'apollo-assistant', description: 'Insight' },
    'budget': { specialist: 'budget-assistant', description: 'Cost Management' },
    'engram': { specialist: 'engram-assistant', description: 'Memory System' },
    'rhetor': { specialist: 'rhetor-orchestrator', description: 'Models' },
    'prometheus': { specialist: 'prometheus-assistant', description: 'Strategic Planning' },
    'metis': { specialist: 'metis-assistant', description: 'Task Decomposition' },
    'harmonia': { specialist: 'harmonia-assistant', description: 'Workflow Orchestration' },
    'synthesis': { specialist: 'synthesis-assistant', description: 'Integration Hub' },
    'sophia': { specialist: 'sophia-assistant', description: 'Machine Learning' },
    'ergon': { specialist: 'ergon-assistant', description: 'Agent Management' },
    'telos': { specialist: 'telos-assistant', description: 'Requirements' },
    'hermes': { specialist: null, description: 'Message Bus' },
    'codex': { specialist: null, description: 'Code Management' },
    'terma': { specialist: null, description: 'Terminal Interface' }
};

// Standard semantic tags to add to component containers
function getComponentTags(componentName) {
    const config = COMPONENT_CONFIGS[componentName] || {};
    const tags = {
        'data-tekton-area': componentName,
        'data-tekton-component': componentName,
        'data-tekton-type': 'component-workspace'
    };
    
    if (config.specialist) {
        tags['data-tekton-ai'] = config.specialist;
        tags['data-tekton-ai-ready'] = 'false';
    }
    
    return tags;
}

// Add tags to an HTML element string
function addTagsToElement(elementStr, tags) {
    // Find the position after the class attribute or after the opening tag
    const classMatch = elementStr.match(/class="[^"]*"/);
    let insertPos;
    
    if (classMatch) {
        insertPos = elementStr.indexOf(classMatch[0]) + classMatch[0].length;
    } else {
        // Insert after the tag name and before any existing attributes
        const match = elementStr.match(/<\w+/);
        if (match) {
            insertPos = match[0].length;
        } else {
            return elementStr;
        }
    }
    
    // Build the tag string
    const tagStr = Object.entries(tags)
        .map(([key, value]) => ` ${key}="${value}"`)
        .join('');
    
    // Insert the tags
    return elementStr.slice(0, insertPos) + tagStr + elementStr.slice(insertPos);
}

// Process a component HTML file
function processComponentFile(componentName, filePath) {
    console.log(`\nProcessing ${componentName}...`);
    
    try {
        let content = fs.readFileSync(filePath, 'utf8');
        const tags = getComponentTags(componentName);
        
        // Find the main component container (usually the first div with the component class)
        const componentClassPattern = new RegExp(`<div\\s+class="[^"]*${componentName}[^"]*"[^>]*>`, 'i');
        const match = content.match(componentClassPattern);
        
        if (match) {
            const originalElement = match[0];
            const taggedElement = addTagsToElement(originalElement, tags);
            content = content.replace(originalElement, taggedElement);
            
            // Write back the file
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✓ Tagged ${componentName} container`);
            
            // Log the tags added
            console.log('  Added tags:', JSON.stringify(tags, null, 2));
        } else {
            console.log(`⚠ Could not find main container for ${componentName}`);
        }
        
        // Additional tagging for common elements
        // Tag chat areas if present
        if (content.includes('chat') || content.includes('message')) {
            console.log(`  - Found chat interface in ${componentName}`);
        }
        
        // Tag navigation tabs if present
        if (content.includes('tab') && content.includes('data-tab')) {
            console.log(`  - Found tab navigation in ${componentName}`);
        }
        
    } catch (error) {
        console.error(`✗ Error processing ${componentName}:`, error.message);
    }
}

// Main execution
function main() {
    console.log('Starting systematic component tagging...');
    console.log('=====================================\n');
    
    const componentsDir = path.join(__dirname, '..', 'ui', 'components');
    const components = fs.readdirSync(componentsDir)
        .filter(dir => fs.statSync(path.join(componentsDir, dir)).isDirectory())
        .filter(dir => !['shared', 'test', 'tekton-dashboard'].includes(dir));
    
    console.log(`Found ${components.length} components to process:`, components.join(', '));
    
    components.forEach(componentName => {
        const htmlFile = path.join(componentsDir, componentName, `${componentName}-component.html`);
        if (fs.existsSync(htmlFile)) {
            processComponentFile(componentName, htmlFile);
        } else {
            console.log(`\n⚠ No HTML file found for ${componentName}`);
        }
    });
    
    console.log('\n=====================================');
    console.log('Component tagging complete!');
    console.log('\nNext steps:');
    console.log('1. Review the tagged components');
    console.log('2. Add interactive element tags (buttons, forms)');
    console.log('3. Add chat interface tags where applicable');
    console.log('4. Test with UI DevTools');
}

// Run the script
main();
