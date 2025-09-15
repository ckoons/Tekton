/**
 * Cognition Brain 3D Visualization
 * Three.js-based 3D brain with rotation and anatomical regions
 */

class CognitionBrain3D {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.brain = null;
        this.regions = {};
        this.mouse = { x: 0, y: 0 };
        this.targetRotation = { x: 0, y: 0 };
        this.currentRotation = { x: 0, y: 0 };
        this.isDragging = false;
        this.previousMousePosition = { x: 0, y: 0 };
        
        this.init();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000000); // Pure black background
        
        // Setup camera
        const width = this.container.clientWidth || 800;
        const height = this.container.clientHeight || 500;
        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        this.camera.position.set(0, 0, 300);
        this.camera.lookAt(0, 0, 0);
        
        // Setup renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.domElement.style.display = 'block';
        this.container.appendChild(this.renderer.domElement);
        console.log('3D Brain renderer created, size:', width, 'x', height);
        
        // Add lights
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);
        
        const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight1.position.set(100, 100, 100);
        this.scene.add(directionalLight1);
        
        const directionalLight2 = new THREE.DirectionalLight(0x9C27B0, 0.3);
        directionalLight2.position.set(-100, -100, -100);
        this.scene.add(directionalLight2);
        
        // Create brain structure
        this.createBrain();
        
        // Add event listeners
        this.setupEventListeners();
        
        // Start animation
        this.animate();
    }
    
    createBrain() {
        // Create main brain group
        this.brain = new THREE.Group();
        
        // Create cranium (semi-transparent gray shell)
        const craniumGeometry = new THREE.SphereGeometry(100, 32, 32);
        craniumGeometry.scale(1.0, 0.85, 0.75); // Make it more brain-shaped
        const craniumMaterial = new THREE.MeshPhongMaterial({
            color: 0x808080,
            transparent: true,
            opacity: 0.15,
            side: THREE.DoubleSide,
            wireframe: false
        });
        const cranium = new THREE.Mesh(craniumGeometry, craniumMaterial);
        this.brain.add(cranium);
        
        // Create brain matter (main brain volume)
        const brainGeometry = new THREE.SphereGeometry(95, 32, 32);
        brainGeometry.scale(1.0, 0.85, 0.75);
        const brainMaterial = new THREE.MeshPhongMaterial({
            color: 0xffb3ba,
            transparent: true,
            opacity: 0.3,
            shininess: 30
        });
        const brainMatter = new THREE.Mesh(brainGeometry, brainMaterial);
        this.brain.add(brainMatter);
        
        // Create anatomical regions
        this.createBrainRegions();
        
        // Add brain to scene
        this.scene.add(this.brain);
    }
    
    createBrainRegions() {
        const regionData = {
            prefrontalCortex: {
                position: { x: 0, y: 30, z: 60 },
                size: 25,
                color: 0x4CAF50,
                functions: ['working_memory', 'planning', 'decision_making']
            },
            hippocampus: {
                position: { x: -20, y: -10, z: 0 },
                size: 15,
                color: 0x2196F3,
                functions: ['encoding', 'consolidation', 'retrieval']
            },
            amygdala: {
                position: { x: 20, y: -10, z: 0 },
                size: 12,
                color: 0xFF9800,
                functions: ['emotional_tagging', 'fear_response', 'memory_modulation']
            },
            temporalLobe: {
                position: { x: -50, y: 0, z: 10 },
                size: 20,
                color: 0x9C27B0,
                functions: ['semantic_memory', 'language', 'recognition']
            },
            parietalLobe: {
                position: { x: 0, y: 40, z: -20 },
                size: 22,
                color: 0x00BCD4,
                functions: ['spatial_processing', 'attention', 'integration']
            },
            occipitalLobe: {
                position: { x: 0, y: 0, z: -60 },
                size: 18,
                color: 0xFFEB3B,
                functions: ['visual_processing', 'pattern_recognition']
            },
            cerebellum: {
                position: { x: 0, y: -40, z: -40 },
                size: 25,
                color: 0x795548,
                functions: ['procedural_memory', 'motor_learning', 'coordination']
            },
            basalGanglia: {
                position: { x: 0, y: 0, z: 0 },
                size: 15,
                color: 0x607D8B,
                functions: ['habit_formation', 'reward_processing', 'motivation']
            },
            cingulateCortex: {
                position: { x: 0, y: 20, z: 20 },
                size: 18,
                color: 0xE91E63,
                functions: ['error_detection', 'conflict_monitoring', 'attention']
            },
            thalamus: {
                position: { x: 0, y: -5, z: 5 },
                size: 14,
                color: 0x3F51B5,
                functions: ['relay_station', 'consciousness', 'alertness']
            }
        };
        
        Object.entries(regionData).forEach(([name, data]) => {
            // Create sphere for region
            const geometry = new THREE.SphereGeometry(data.size, 16, 16);
            const material = new THREE.MeshPhongMaterial({
                color: data.color,
                transparent: true,
                opacity: 0.6,
                emissive: data.color,
                emissiveIntensity: 0.2
            });
            
            const region = new THREE.Mesh(geometry, material);
            region.position.set(data.position.x, data.position.y, data.position.z);
            region.userData = { name, functions: data.functions, baseOpacity: 0.6 };
            
            this.regions[name] = region;
            this.brain.add(region);
            
            // Add pulsing animation
            region.userData.pulsePhase = Math.random() * Math.PI * 2;
        });
    }
    
    setupEventListeners() {
        // Mouse move for auto-rotation
        this.renderer.domElement.addEventListener('mousemove', (e) => {
            const rect = this.renderer.domElement.getBoundingClientRect();
            this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            
            if (this.isDragging) {
                const deltaX = e.clientX - this.previousMousePosition.x;
                const deltaY = e.clientY - this.previousMousePosition.y;
                
                this.targetRotation.y += deltaX * 0.01;
                this.targetRotation.x += deltaY * 0.01;
                
                this.previousMousePosition = { x: e.clientX, y: e.clientY };
            }
        });
        
        // Mouse down to start dragging
        this.renderer.domElement.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            this.previousMousePosition = { x: e.clientX, y: e.clientY };
            this.renderer.domElement.style.cursor = 'grabbing';
        });
        
        // Mouse up to stop dragging
        this.renderer.domElement.addEventListener('mouseup', () => {
            this.isDragging = false;
            this.renderer.domElement.style.cursor = 'grab';
        });
        
        // Mouse leave to stop dragging
        this.renderer.domElement.addEventListener('mouseleave', () => {
            this.isDragging = false;
            this.renderer.domElement.style.cursor = 'grab';
        });
        
        // Set initial cursor
        this.renderer.domElement.style.cursor = 'grab';
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }
    
    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight || 500;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Smooth rotation
        if (!this.isDragging) {
            // Auto-rotate slowly when not dragging
            this.targetRotation.y += 0.002;
        }
        
        // Lerp current rotation to target
        this.currentRotation.x += (this.targetRotation.x - this.currentRotation.x) * 0.05;
        this.currentRotation.y += (this.targetRotation.y - this.currentRotation.y) * 0.05;
        
        // Apply rotation
        this.brain.rotation.x = this.currentRotation.x;
        this.brain.rotation.y = this.currentRotation.y;
        
        // Animate brain regions
        const time = Date.now() * 0.001;
        Object.values(this.regions).forEach(region => {
            const pulseScale = 1 + Math.sin(time * 2 + region.userData.pulsePhase) * 0.05;
            region.scale.set(pulseScale, pulseScale, pulseScale);
            
            // Vary opacity slightly
            const opacityVariation = Math.sin(time * 3 + region.userData.pulsePhase) * 0.1;
            region.material.opacity = region.userData.baseOpacity + opacityVariation;
        });
        
        this.renderer.render(this.scene, this.camera);
    }
    
    updateRegionActivity(regionName, intensity) {
        const region = this.regions[regionName];
        if (region) {
            // Update color intensity based on activity
            region.material.emissiveIntensity = 0.2 + (intensity * 0.5);
            region.userData.baseOpacity = 0.4 + (intensity * 0.4);
            
            // Add temporary glow effect
            const originalScale = region.scale.x;
            region.scale.set(originalScale * 1.2, originalScale * 1.2, originalScale * 1.2);
            
            setTimeout(() => {
                region.scale.set(originalScale, originalScale, originalScale);
            }, 300);
        }
    }
    
    highlightRegion(regionName) {
        Object.entries(this.regions).forEach(([name, region]) => {
            if (name === regionName) {
                region.material.opacity = 0.9;
                region.material.emissiveIntensity = 0.5;
            } else {
                region.material.opacity = 0.3;
                region.material.emissiveIntensity = 0.1;
            }
        });
    }
    
    resetHighlight() {
        Object.values(this.regions).forEach(region => {
            region.material.opacity = region.userData.baseOpacity;
            region.material.emissiveIntensity = 0.2;
        });
    }
    
    showAspect(aspectName) {
        // Map aspects to relevant brain regions
        const aspectRegions = {
            memory: ['hippocampus', 'temporalLobe', 'prefrontalCortex'],
            emotion: ['amygdala', 'cingulateCortex', 'prefrontalCortex'],
            planning: ['prefrontalCortex', 'parietalLobe', 'basalGanglia'],
            language: ['temporalLobe', 'prefrontalCortex'],
            spatial: ['parietalLobe', 'occipitalLobe', 'hippocampus'],
            attention: ['cingulateCortex', 'parietalLobe', 'thalamus'],
            learning: ['hippocampus', 'cerebellum', 'basalGanglia'],
            reasoning: ['prefrontalCortex', 'parietalLobe', 'temporalLobe']
        };
        
        const regions = aspectRegions[aspectName] || [];
        
        Object.entries(this.regions).forEach(([name, region]) => {
            if (regions.includes(name)) {
                region.material.opacity = 0.8;
                region.material.emissiveIntensity = 0.4;
                // Add pulsing effect for active aspects
                region.userData.aspectActive = true;
            }
        });
    }
    
    hideAspect(aspectName) {
        // Reset regions associated with this aspect
        Object.values(this.regions).forEach(region => {
            if (region.userData.aspectActive) {
                region.userData.aspectActive = false;
                region.material.opacity = region.userData.baseOpacity;
                region.material.emissiveIntensity = 0.2;
            }
        });
    }
}

// Initialize when ready
function initializeCognitionBrain3D() {
    const container = document.getElementById('cognition-brain-3d');
    if (container) {
        // Clear any existing instance
        if (window.cognitionBrain3D) {
            console.log('Clearing existing 3D brain instance');
            if (window.cognitionBrain3D.renderer) {
                container.innerHTML = '';
            }
        }
        
        console.log('Initializing Cognition Brain 3D visualization');
        window.cognitionBrain3D = new CognitionBrain3D('cognition-brain-3d');
        
        // Connect to WebSocket for real-time updates
        connectCognitionWebSocket();
    } else {
        console.log('Container cognition-brain-3d not found yet');
    }
}

// Try to initialize on DOM ready and also when panel becomes visible
document.addEventListener('DOMContentLoaded', () => {
    // Check if Three.js is loaded
    if (typeof THREE === 'undefined') {
        console.warn('Three.js not loaded. Loading from CDN...');
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
        script.onload = () => {
            setTimeout(initializeCognitionBrain3D, 100);
        };
        document.head.appendChild(script);
    } else {
        setTimeout(initializeCognitionBrain3D, 100);
    }
});

// Also try to initialize when cognition tab is clicked
document.addEventListener('click', (e) => {
    if (e.target.closest('[data-tab="cognition"]') || e.target.closest('#engram-tab-cognition')) {
        setTimeout(initializeCognitionBrain3D, 100);
    }
    
    // Handle region button clicks
    if (e.target.closest('.cognition__btn-region')) {
        const btn = e.target.closest('.cognition__btn-region');
        const region = btn.getAttribute('data-region');
        
        // Remove active from all region buttons
        document.querySelectorAll('.cognition__btn-region').forEach(b => b.classList.remove('active'));
        
        // Toggle active state on clicked button
        btn.classList.add('active');
        
        // Highlight region in 3D brain if exists
        if (window.cognitionBrain3D) {
            window.cognitionBrain3D.highlightRegion(region);
        }
    }
    
    // Handle aspect button clicks
    if (e.target.closest('.cognition__btn-aspect')) {
        const btn = e.target.closest('.cognition__btn-aspect');
        const aspect = btn.getAttribute('data-aspect');
        
        // Toggle active state
        btn.classList.toggle('active');
        
        // Trigger aspect visualization if brain exists
        if (window.cognitionBrain3D) {
            if (btn.classList.contains('active')) {
                window.cognitionBrain3D.showAspect(aspect);
            } else {
                window.cognitionBrain3D.hideAspect(aspect);
            }
        }
    }
});

function connectCognitionWebSocket() {
    const ws = new WebSocket('ws://localhost:8100/cognition/stream');
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'region_activation' && window.cognitionBrain3D) {
            window.cognitionBrain3D.updateRegionActivity(data.region, data.intensity);
        }
    };
    
    ws.onerror = (error) => {
        console.log('WebSocket error, will retry in 5 seconds');
        setTimeout(connectCognitionWebSocket, 5000);
    };
}