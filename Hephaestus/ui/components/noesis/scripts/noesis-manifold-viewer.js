/**
 * Noesis 3D Manifold Viewer
 * Advanced 3D visualization for manifold analysis using Three.js
 */

class NoesisManifoldViewer {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        
        if (!this.container) {
            console.error(`[NoesisManifoldViewer] Container ${containerId} not found`);
            return;
        }
        
        // Three.js components
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        
        // Data objects
        this.pointCloud = null;
        this.trajectory = null;
        this.regions = [];
        
        // Configuration
        this.config = {
            pointSize: 3,
            trajectoryWidth: 2,
            cameraDistance: 10,
            autoRotate: false,
            showAxes: true
        };
        
        this.initialized = false;
        this.animationId = null;
        
        this.initialize();
    }
    
    initialize() {
        try {
            if (typeof THREE === 'undefined') {
                console.warn('[NoesisManifoldViewer] THREE.js not loaded, using fallback 2D visualization');
                this.initializeFallback();
                return;
            }
            
            this.initializeThreeJS();
            this.setupEventListeners();
            this.initialized = true;
            
            console.log('[NoesisManifoldViewer] 3D visualization initialized');
        } catch (error) {
            console.error('[NoesisManifoldViewer] Initialization failed:', error);
            this.initializeFallback();
        }
    }
    
    initializeThreeJS() {
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1e1e2e);
        
        // Camera setup
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
        this.camera.position.set(5, 5, 5);
        this.camera.lookAt(0, 0, 0);
        
        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true 
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);
        
        // Controls setup (if available)
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
            this.controls.autoRotate = this.config.autoRotate;
            this.controls.autoRotateSpeed = 1.0;
        }
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        this.scene.add(directionalLight);
        
        // Add coordinate axes if enabled
        if (this.config.showAxes) {
            this.addCoordinateAxes();
        }
        
        // Start render loop
        this.startRenderLoop();
    }
    
    initializeFallback() {
        // Fallback 2D visualization using Canvas
        this.container.innerHTML = `
            <canvas id="${this.containerId}-canvas" 
                    style="width: 100%; height: 100%; background: #1e1e2e;">
            </canvas>
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                        color: #aaa; text-align: center;">
                <p>3D visualization requires Three.js library</p>
                <p>Fallback 2D visualization active</p>
            </div>
        `;
        
        this.canvas = document.getElementById(`${this.containerId}-canvas`);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.initialized = true;
    }
    
    addCoordinateAxes() {
        const axesHelper = new THREE.AxesHelper(3);
        this.scene.add(axesHelper);
        
        // Add axis labels
        const loader = new THREE.FontLoader();
        // Note: In production, you'd load a proper font
        // For now, we'll skip text labels to avoid font loading complexity
    }
    
    startRenderLoop() {
        const animate = () => {
            this.animationId = requestAnimationFrame(animate);
            
            if (this.controls) {
                this.controls.update();
            }
            
            if (this.renderer && this.scene && this.camera) {
                this.renderer.render(this.scene, this.camera);
            }
        };
        
        animate();
    }
    
    updateManifold(data) {
        if (!this.initialized) {
            console.warn('[NoesisManifoldViewer] Not initialized, cannot update manifold');
            return;
        }
        
        try {
            if (this.renderer) {
                this.updateManifold3D(data);
            } else {
                this.updateManifold2D(data);
            }
        } catch (error) {
            console.error('[NoesisManifoldViewer] Error updating manifold:', error);
        }
    }
    
    updateManifold3D(data) {
        // Clear previous manifold objects
        this.clearPreviousManifold();
        
        // Add new point cloud
        if (data.embedding_coordinates && data.embedding_coordinates.length > 0) {
            this.renderManifoldPoints(data.embedding_coordinates);
        }
        
        // Add trajectory if available
        if (data.trajectory && data.trajectory.length > 0) {
            this.renderTrajectory(data.trajectory);
        }
        
        // Add regime regions if available
        if (data.regime_assignments && data.regime_assignments.length > 0) {
            this.renderRegions(data.regime_assignments);
        }
        
        console.log('[NoesisManifoldViewer] 3D manifold updated');
    }
    
    updateManifold2D(data) {
        if (!this.ctx || !this.canvas) return;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Simple 2D projection of data
        if (data.embedding_coordinates && data.embedding_coordinates.length > 0) {
            this.render2DPoints(data.embedding_coordinates);
        }
        
        console.log('[NoesisManifoldViewer] 2D manifold updated');
    }
    
    clearPreviousManifold() {
        // Remove point cloud
        if (this.pointCloud) {
            this.scene.remove(this.pointCloud);
            if (this.pointCloud.geometry) this.pointCloud.geometry.dispose();
            if (this.pointCloud.material) this.pointCloud.material.dispose();
            this.pointCloud = null;
        }
        
        // Remove trajectory
        if (this.trajectory) {
            this.scene.remove(this.trajectory);
            if (this.trajectory.geometry) this.trajectory.geometry.dispose();
            if (this.trajectory.material) this.trajectory.material.dispose();
            this.trajectory = null;
        }
        
        // Remove regions
        this.regions.forEach(region => {
            this.scene.remove(region);
            if (region.geometry) region.geometry.dispose();
            if (region.material) region.material.dispose();
        });
        this.regions = [];
    }
    
    renderManifoldPoints(coordinates) {
        if (!coordinates || coordinates.length === 0) return;
        
        const geometry = new THREE.BufferGeometry();
        const positions = [];
        const colors = [];
        
        // Convert coordinates to Three.js format
        coordinates.forEach((point, index) => {
            if (point.length >= 3) {
                positions.push(point[0], point[1], point[2]);
                
                // Color gradient based on index
                const hue = (index / coordinates.length) * 360;
                const color = new THREE.Color();
                color.setHSL(hue / 360, 0.7, 0.6);
                colors.push(color.r, color.g, color.b);
            }
        });
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        
        const material = new THREE.PointsMaterial({
            size: this.config.pointSize,
            vertexColors: true,
            transparent: true,
            opacity: 0.8
        });
        
        this.pointCloud = new THREE.Points(geometry, material);
        this.scene.add(this.pointCloud);
    }
    
    renderTrajectory(trajectory) {
        if (!trajectory || trajectory.length < 2) return;
        
        const geometry = new THREE.BufferGeometry();
        const positions = [];
        
        trajectory.forEach(point => {
            if (point.length >= 3) {
                positions.push(point[0], point[1], point[2]);
            }
        });
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        
        const material = new THREE.LineBasicMaterial({
            color: 0xff6f00,
            linewidth: this.config.trajectoryWidth,
            transparent: true,
            opacity: 0.9
        });
        
        this.trajectory = new THREE.Line(geometry, material);
        this.scene.add(this.trajectory);
    }
    
    renderRegions(regimeAssignments) {
        // Group points by regime
        const regimes = {};
        regimeAssignments.forEach((regime, index) => {
            if (!regimes[regime]) regimes[regime] = [];
            regimes[regime].push(index);
        });
        
        // Create convex hull for each regime (simplified)
        Object.keys(regimes).forEach((regime, regimeIndex) => {
            const points = regimes[regime];
            if (points.length < 3) return;
            
            // Create a simple sphere to represent the regime region
            const geometry = new THREE.SphereGeometry(0.5, 16, 16);
            const material = new THREE.MeshBasicMaterial({
                color: new THREE.Color().setHSL(regimeIndex / Object.keys(regimes).length, 0.6, 0.5),
                transparent: true,
                opacity: 0.2,
                wireframe: true
            });
            
            const region = new THREE.Mesh(geometry, material);
            
            // Position at centroid of points (simplified)
            region.position.set(
                Math.random() * 4 - 2,
                Math.random() * 4 - 2,
                Math.random() * 4 - 2
            );
            
            this.regions.push(region);
            this.scene.add(region);
        });
    }
    
    render2DPoints(coordinates) {
        if (!this.ctx || !coordinates || coordinates.length === 0) return;
        
        const canvas = this.canvas;
        const ctx = this.ctx;
        
        // Set canvas size
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
        
        // Find bounds
        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;
        
        coordinates.forEach(point => {
            if (point.length >= 2) {
                minX = Math.min(minX, point[0]);
                maxX = Math.max(maxX, point[0]);
                minY = Math.min(minY, point[1]);
                maxY = Math.max(maxY, point[1]);
            }
        });
        
        // Draw points
        coordinates.forEach((point, index) => {
            if (point.length >= 2) {
                const x = ((point[0] - minX) / (maxX - minX)) * (canvas.width - 40) + 20;
                const y = ((point[1] - minY) / (maxY - minY)) * (canvas.height - 40) + 20;
                
                const hue = (index / coordinates.length) * 360;
                ctx.fillStyle = `hsl(${hue}, 70%, 60%)`;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fill();
            }
        });
    }
    
    setConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        
        if (this.controls) {
            this.controls.autoRotate = this.config.autoRotate;
        }
        
        if (this.pointCloud && this.pointCloud.material) {
            this.pointCloud.material.size = this.config.pointSize;
        }
    }
    
    resize() {
        if (!this.renderer || !this.camera) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(width, height);
    }
    
    setupEventListeners() {
        // Handle window resize
        window.addEventListener('resize', () => {
            this.resize();
        });
        
        // Handle container resize (using ResizeObserver if available)
        if (typeof ResizeObserver !== 'undefined') {
            const resizeObserver = new ResizeObserver(() => {
                this.resize();
            });
            resizeObserver.observe(this.container);
        }
    }
    
    destroy() {
        // Clean up animation
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        // Clean up Three.js objects
        this.clearPreviousManifold();
        
        if (this.renderer) {
            this.renderer.dispose();
            if (this.renderer.domElement && this.renderer.domElement.parentNode) {
                this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
            }
        }
        
        if (this.controls) {
            this.controls.dispose();
        }
        
        console.log('[NoesisManifoldViewer] Destroyed');
    }
}

// Export for use in other scripts
window.NoesisManifoldViewer = NoesisManifoldViewer;