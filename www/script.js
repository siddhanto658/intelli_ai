/**
 * INTELLI AI - Smooth Particle Animation
 * Optimized for seamless, smooth rendering
 */
(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        particleCount: 800,
        sphereRadius: 120,
        particleSize: 1.5,
        rotationSpeed: 0.0008,
        colors: {
            primary: { r: 0, g: 100, b: 255 },
            secondary: { r: 139, g: 92, b: 246 },
            accent: { r: 6, g: 182, b: 212 }
        }
    };

    let canvas, ctx;
    let width, height;
    let centerX, centerY;
    let particles = [];
    let animationId = null;
    let rotationAngle = 0;
    let mouseX = 0, mouseY = 0;
    let isHovering = false;

    // Initialize
    function init() {
        canvas = document.getElementById('canvasOne');
        if (!canvas) return;
        
        ctx = canvas.getContext('2d');
        resize();
        createParticles();
        animate();
        
        // Mouse interaction
        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('mouseleave', handleMouseLeave);
        window.addEventListener('resize', handleResize);
    }

    function resize() {
        const container = canvas.parentElement;
        width = container.clientWidth || 700;
        height = container.clientHeight || 420;
        
        canvas.width = width;
        canvas.height = height;
        
        centerX = width / 2;
        centerY = height / 2;
    }

    function handleResize() {
        resize();
        createParticles();
    }

    function handleMouseMove(e) {
        const rect = canvas.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
        isHovering = true;
    }

    function handleMouseLeave() {
        isHovering = false;
    }

    // Particle class
    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            // Random position on sphere surface
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            
            this.baseX = CONFIG.sphereRadius * Math.sin(phi) * Math.cos(theta);
            this.baseY = CONFIG.sphereRadius * Math.sin(phi) * Math.sin(theta);
            this.baseZ = CONFIG.sphereRadius * Math.cos(phi);
            
            this.x = this.baseX;
            this.y = this.baseY;
            this.z = this.baseZ;
            
            this.vx = (Math.random() - 0.5) * 0.02;
            this.vy = (Math.random() - 0.5) * 0.02;
            this.vz = (Math.random() - 0.5) * 0.02;
            
            this.alpha = 0;
            this.targetAlpha = 0.8 + Math.random() * 0.2;
            this.colorPhase = Math.random();
            
            this.size = CONFIG.particleSize * (0.8 + Math.random() * 0.4);
        }

        update(rotation) {
            // Apply rotation
            const cosA = Math.cos(rotation);
            const sinA = Math.sin(rotation);
            
            let x = this.baseX;
            let y = this.baseY;
            let z = this.baseZ;
            
            // Rotate around Y axis
            const rx = x * cosA - z * sinA;
            const rz = x * sinA + z * cosA;
            x = rx;
            z = rz;
            
            // Mouse interaction - slight parallax
            let offsetX = 0, offsetY = 0;
            if (isHovering) {
                offsetX = (mouseX - centerX) * 0.01 * (1 - this.baseZ / CONFIG.sphereRadius);
                offsetY = (mouseY - centerY) * 0.01 * (1 - this.baseZ / CONFIG.sphereRadius);
            }
            
            this.x = x + offsetX;
            this.y = y + offsetY;
            this.z = z;
            
            // Calculate alpha based on z-depth
            const depth = (z + CONFIG.sphereRadius) / (CONFIG.sphereRadius * 2);
            this.alpha = depth * this.targetAlpha;
            
            return { x: this.x, y: this.y, z: this.z, alpha: this.alpha, depth: depth };
        }
    }

    function createParticles() {
        particles = [];
        for (let i = 0; i < CONFIG.particleCount; i++) {
            particles.push(new Particle());
        }
    }

    function getColor(depth, colorPhase) {
        const c = CONFIG.colors;
        
        if (colorPhase < 0.33) {
            return `rgba(${c.primary.r}, ${c.primary.g}, ${c.primary.b},`;
        } else if (colorPhase < 0.66) {
            return `rgba(${c.secondary.r}, ${c.secondary.g}, ${c.secondary.b},`;
        } else {
            return `rgba(${c.accent.r}, ${c.accent.g}, ${c.accent.b},`;
        }
    }

    function animate() {
        // Clear with fade effect
        ctx.fillStyle = 'rgba(10, 10, 15, 1)';
        ctx.fillRect(0, 0, width, height);
        
        // Update rotation
        rotationAngle += CONFIG.rotationSpeed;
        
        // Sort particles by depth for proper rendering
        const sortedParticles = particles.map(p => {
            const state = p.update(rotationAngle);
            return { particle: p, ...state };
        }).sort((a, b) => b.depth - a.depth);
        
        // Render particles
        for (const p of sortedParticles) {
            if (p.alpha < 0.01) continue;
            
            const color = getColor(p.depth, p.particle.colorPhase);
            const size = p.particle.size * (0.5 + p.depth * 0.5);
            
            const screenX = centerX + p.x;
            const screenY = centerY + p.y;
            
            // Create gradient for glow effect
            const gradient = ctx.createRadialGradient(
                screenX, screenY, 0,
                screenX, screenY, size * 2
            );
            gradient.addColorStop(0, `${color}${p.alpha})`);
            gradient.addColorStop(0.5, `${color}${p.alpha * 0.5})`);
            gradient.addColorStop(1, `${color}0)`);
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(screenX, screenY, size * 2, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Draw center glow
        const glowGradient = ctx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, 80
        );
        glowGradient.addColorStop(0, 'rgba(139, 92, 246, 0.15)');
        glowGradient.addColorStop(0.5, 'rgba(6, 182, 212, 0.05)');
        glowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        
        ctx.fillStyle = glowGradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, 80, 0, Math.PI * 2);
        ctx.fill();
        
        animationId = requestAnimationFrame(animate);
    }

    // Cleanup
    function stopAnimation() {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
    }

    // Start when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose for external control
    window.INTELLIAnimation = {
        stop: stopAnimation,
        restart: function() {
            stopAnimation();
            createParticles();
            animate();
        }
    };
})();