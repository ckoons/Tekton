/**
 * Semantic Tag Verification Script
 * Verifies that all components have proper semantic tagging
 * Reports on coverage and identifies missing tags
 */

const fs = require('fs');
const path = require('path');
// const cheerio = require('cheerio'); // If not available, we'll parse manually

// Expected components and their configurations
const EXPECTED_COMPONENTS = {
    'athena': { specialist: 'athena-assistant' },
    'apollo': { specialist: 'apollo-assistant' },
    'budget': { specialist: 'budget-assistant' },
    'engram': { specialist: 'engram-assistant' },
    'rhetor': { specialist: 'rhetor-orchestrator' },
    'prometheus': { specialist: 'prometheus-assistant' },
    'metis': { specialist: 'metis-assistant' },
    'harmonia': { specialist: 'harmonia-assistant' },
    'synthesis': { specialist: 'synthesis-assistant' },
    'sophia': { specialist: 'sophia-assistant' },
    'ergon': { specialist: 'ergon-assistant' },
    'telos': { specialist: 'telos-assistant' },
    'hermes': { specialist: null },
    'codex': { specialist: null },
    'terma': { specialist: null },
    'tekton': { specialist: null },
    'settings': { specialist: null },
    'profile': { specialist: null }
};

// Required semantic tags for components
const REQUIRED_TAGS = [
    'data-tekton-area',
    'data-tekton-component',
    'data-tekton-type'
];

const AI_TAGS = [
    'data-tekton-ai',
    'data-tekton-ai-ready'
];

// Simple HTML attribute parser
function extractAttributes(htmlString) {
    const attrs = {};
    const attrRegex = /(\w+(?:-\w+)*)\s*=\s*"([^"]*)"/g;
    let match;
    
    while ((match = attrRegex.exec(htmlString)) !== null) {
        attrs[match[1]] = match[2];
    }
    
    return attrs;
}

// Verify a single component
function verifyComponent(componentName, filePath) {
    const results = {
        component: componentName,
        exists: false,
        tagged: false,
        missingTags: [],
        attributes: {},
        warnings: []
    };
    
    try {
        if (!fs.existsSync(filePath)) {
            return results;
        }
        
        results.exists = true;
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Find the main component div
        const componentPattern = new RegExp(`<div\\s+class="[^"]*${componentName}[^"]*"[^>]*>`, 'i');
        const match = content.match(componentPattern);
        
        if (!match) {
            results.warnings.push('Could not find main component container');
            return results;
        }
        
        // Extract attributes
        results.attributes = extractAttributes(match[0]);
        
        // Check required tags
        REQUIRED_TAGS.forEach(tag => {
            if (!results.attributes[tag]) {
                results.missingTags.push(tag);
            }
        });
        
        // Check AI tags if specialist expected
        const config = EXPECTED_COMPONENTS[componentName];
        if (config && config.specialist) {
            AI_TAGS.forEach(tag => {
                if (!results.attributes[tag]) {
                    results.missingTags.push(tag);
                }
            });
            
            // Verify specialist ID matches
            if (results.attributes['data-tekton-ai'] && 
                results.attributes['data-tekton-ai'] !== config.specialist) {
                results.warnings.push(`AI specialist mismatch: expected '${config.specialist}', found '${results.attributes['data-tekton-ai']}'`);
            }
        }
        
        results.tagged = results.missingTags.length === 0;
        
        // Check for additional useful tags
        if (content.includes('chat') || content.includes('message')) {
            if (!content.includes('data-tekton-chat')) {
                results.warnings.push('Component has chat interface but no data-tekton-chat tags');
            }
        }
        
    } catch (error) {
        results.warnings.push(`Error processing: ${error.message}`);
    }
    
    return results;
}

// Generate report
function generateReport(results) {
    console.log('\n📊 SEMANTIC TAG VERIFICATION REPORT');
    console.log('=====================================\n');
    
    const summary = {
        total: results.length,
        tagged: results.filter(r => r.tagged).length,
        partial: results.filter(r => r.exists && !r.tagged && r.missingTags.length > 0).length,
        missing: results.filter(r => !r.exists).length
    };
    
    console.log('SUMMARY:');
    console.log(`✅ Fully Tagged: ${summary.tagged}/${summary.total}`);
    console.log(`⚠️  Partially Tagged: ${summary.partial}`);
    console.log(`❌ Missing Files: ${summary.missing}`);
    console.log(`📈 Coverage: ${Math.round((summary.tagged / summary.total) * 100)}%\n`);
    
    // Detailed results
    console.log('COMPONENT DETAILS:');
    console.log('-----------------');
    
    results.forEach(result => {
        const status = result.tagged ? '✅' : result.exists ? '⚠️' : '❌';
        console.log(`\n${status} ${result.component}`);
        
        if (!result.exists) {
            console.log('   File not found');
        } else {
            if (result.missingTags.length > 0) {
                console.log(`   Missing tags: ${result.missingTags.join(', ')}`);
            }
            
            if (result.warnings.length > 0) {
                result.warnings.forEach(warning => {
                    console.log(`   ⚠️  ${warning}`);
                });
            }
            
            // Show current tags
            const tektonTags = Object.entries(result.attributes)
                .filter(([key]) => key.startsWith('data-tekton'))
                .map(([key, value]) => `${key}="${value}"`)
                .join(', ');
            
            if (tektonTags) {
                console.log(`   Current tags: ${tektonTags}`);
            }
        }
    });
    
    // Navigation verification
    console.log('\n\nNAVIGATION VERIFICATION:');
    console.log('----------------------');
    const indexPath = path.join(__dirname, '..', 'ui', 'index.html');
    if (fs.existsSync(indexPath)) {
        const indexContent = fs.readFileSync(indexPath, 'utf8');
        const navTagged = indexContent.includes('data-tekton-nav="main"');
        console.log(`Main Navigation: ${navTagged ? '✅ Tagged' : '❌ Not Tagged'}`);
        
        const navItemCount = (indexContent.match(/data-tekton-nav-item/g) || []).length;
        console.log(`Navigation Items Tagged: ${navItemCount}`);
    }
    
    console.log('\n=====================================');
    console.log('✨ Next Steps:');
    console.log('1. Fix any missing or incorrect tags');
    console.log('2. Add interactive element tags (buttons, forms)');
    console.log('3. Add chat interface tags where applicable');
    console.log('4. Test with UI DevTools\n');
}

// Main execution
function main() {
    console.log('🔍 Verifying Semantic Tags...');
    
    const componentsDir = path.join(__dirname, '..', 'ui', 'components');
    const results = [];
    
    Object.keys(EXPECTED_COMPONENTS).forEach(componentName => {
        const htmlFile = path.join(componentsDir, componentName, `${componentName}-component.html`);
        const result = verifyComponent(componentName, htmlFile);
        results.push(result);
    });
    
    generateReport(results);
}

// Run verification
main();