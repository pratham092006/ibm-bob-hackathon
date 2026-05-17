// ============================================
// AXON Landing Page - Production JavaScript
// Advanced Animations & Interactions
// ============================================

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ============================================
// Navbar Scroll Effects
// ============================================
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    // Add scrolled class for glassmorphism effect
    if (currentScroll > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
    
    lastScroll = currentScroll;
});

// ============================================
// Scroll Progress Bar
// ============================================
const createScrollProgress = () => {
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', () => {
        const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (window.pageYOffset / windowHeight) * 100;
        progressBar.style.width = scrolled + '%';
    });
};

createScrollProgress();

// ============================================
// Intersection Observer for Scroll Animations
// ============================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const animateOnScroll = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            
            // Add stagger effect for children
            const children = entry.target.querySelectorAll('.feature-card, .step, .doc-card, .use-case, .download-card, .instruction');
            children.forEach((child, index) => {
                setTimeout(() => {
                    child.classList.add('visible');
                }, index * 100);
            });
        }
    });
}, observerOptions);

// Observe all animated elements
document.querySelectorAll('.section-title, .section-subtitle, section').forEach(el => {
    animateOnScroll.observe(el);
});

// ============================================
// Terminal Typing Animation
// ============================================
const terminalLines = document.querySelectorAll('.terminal-line');
let delay = 0;

terminalLines.forEach((line, index) => {
    line.style.opacity = '0';
    setTimeout(() => {
        line.style.transition = 'opacity 0.5s ease-in, transform 0.5s ease-in';
        line.style.opacity = '1';
        line.style.transform = 'translateX(0)';
    }, delay);
    delay += 600;
});

// ============================================
// Copy Code to Clipboard
// ============================================
document.querySelectorAll('.code-block').forEach(block => {
    block.style.position = 'relative';
    
    const copyButton = document.createElement('button');
    copyButton.innerHTML = '📋 Copy';
    copyButton.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 0.5rem 1rem;
        background: rgba(99, 102, 241, 0.9);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 600;
        transition: all 0.3s;
        z-index: 10;
    `;
    
    copyButton.addEventListener('mouseenter', () => {
        copyButton.style.background = 'rgba(99, 102, 241, 1)';
        copyButton.style.transform = 'scale(1.05)';
    });
    
    copyButton.addEventListener('mouseleave', () => {
        copyButton.style.background = 'rgba(99, 102, 241, 0.9)';
        copyButton.style.transform = 'scale(1)';
    });
    
    copyButton.addEventListener('click', (e) => {
        e.stopPropagation();
        const code = block.querySelector('code').textContent;
        navigator.clipboard.writeText(code).then(() => {
            copyButton.innerHTML = '✅ Copied!';
            copyButton.style.background = 'rgba(16, 185, 129, 0.9)';
            setTimeout(() => {
                copyButton.innerHTML = '📋 Copy';
                copyButton.style.background = 'rgba(99, 102, 241, 0.9)';
            }, 2000);
        });
    });
    
    block.appendChild(copyButton);
});

// ============================================
// Stats Counter Animation
// ============================================
const animateCounter = (element, target, suffix = '') => {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target + suffix;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current) + suffix;
        }
    }, 30);
};

// Observe stats
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.dataset.animated) {
            const text = entry.target.textContent;
            let target, suffix = '';
            
            if (text.includes('+')) {
                target = parseInt(text.replace('+', ''));
                suffix = '+';
            } else if (text.includes('%')) {
                target = parseInt(text.replace('%', ''));
                suffix = '%';
            } else {
                target = parseInt(text);
            }
            
            entry.target.dataset.animated = 'true';
            animateCounter(entry.target, target, suffix);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-number').forEach(stat => {
    statsObserver.observe(stat);
});

// ============================================
// Comparison Table Row Hover Effects
// ============================================
document.querySelectorAll('.comparison-table tbody tr').forEach(row => {
    row.addEventListener('mouseenter', () => {
        row.style.transform = 'scale(1.02)';
        row.style.transition = 'transform 0.3s ease';
        row.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
    });
    
    row.addEventListener('mouseleave', () => {
        row.style.transform = 'scale(1)';
        row.style.boxShadow = 'none';
    });
});

// ============================================
// Mobile Menu Toggle
// ============================================
const createMobileMenu = () => {
    const navLinks = document.querySelector('.nav-links');
    const menuButton = document.createElement('button');
    menuButton.innerHTML = '☰';
    menuButton.style.cssText = `
        display: none;
        font-size: 1.5rem;
        background: none;
        border: none;
        cursor: pointer;
        color: var(--dark);
    `;
    
    const checkMobile = () => {
        if (window.innerWidth <= 768) {
            menuButton.style.display = 'block';
        } else {
            menuButton.style.display = 'none';
            navLinks.style.display = 'flex';
        }
    };
    
    menuButton.addEventListener('click', () => {
        if (navLinks.style.display === 'none' || navLinks.style.display === '') {
            navLinks.style.display = 'flex';
            navLinks.style.flexDirection = 'column';
            navLinks.style.position = 'absolute';
            navLinks.style.top = '100%';
            navLinks.style.left = '0';
            navLinks.style.right = '0';
            navLinks.style.background = 'rgba(255, 255, 255, 0.98)';
            navLinks.style.padding = '1rem';
            navLinks.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
            navLinks.style.backdropFilter = 'blur(20px)';
            menuButton.innerHTML = '✕';
        } else {
            navLinks.style.display = 'none';
            menuButton.innerHTML = '☰';
        }
    });
    
    document.querySelector('.navbar .container').appendChild(menuButton);
    window.addEventListener('resize', checkMobile);
    checkMobile();
};

createMobileMenu();

// ============================================
// Parallax Effect for Hero Section
// ============================================
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroVisual = document.querySelector('.hero-visual');
    if (heroVisual && scrolled < window.innerHeight) {
        heroVisual.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// ============================================
// Page Load Animation
// ============================================
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease-in';
        document.body.style.opacity = '1';
    }, 100);
});

// ============================================
// Cursor Trail Effect (Optional)
// ============================================
const createCursorTrail = () => {
    const trail = [];
    const trailLength = 20;
    
    for (let i = 0; i < trailLength; i++) {
        const dot = document.createElement('div');
        dot.style.cssText = `
            position: fixed;
            width: 4px;
            height: 4px;
            background: rgba(99, 102, 241, ${1 - i / trailLength});
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            transition: all 0.1s;
        `;
        document.body.appendChild(dot);
        trail.push(dot);
    }
    
    let mouseX = 0, mouseY = 0;
    
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    
    const animateTrail = () => {
        let x = mouseX;
        let y = mouseY;
        
        trail.forEach((dot, index) => {
            dot.style.left = x + 'px';
            dot.style.top = y + 'px';
            
            const nextDot = trail[index + 1] || trail[0];
            x += (parseInt(nextDot.style.left) - x) * 0.3;
            y += (parseInt(nextDot.style.top) - y) * 0.3;
        });
        
        requestAnimationFrame(animateTrail);
    };
    
    animateTrail();
};

// Uncomment to enable cursor trail
// createCursorTrail();

// ============================================
// Feature Card Tilt Effect
// ============================================
document.querySelectorAll('.feature-card, .download-card, .doc-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
    });
});

// ============================================
// Scroll-triggered Animations for Demo Window
// ============================================
const demoWindow = document.querySelector('.demo-window');
if (demoWindow) {
    const demoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInRight 1s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        });
    }, { threshold: 0.3 });
    
    demoObserver.observe(demoWindow);
}

// ============================================
// Easter Egg: Konami Code
// ============================================
let konamiCode = [];
const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.key);
    konamiCode = konamiCode.slice(-10);
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        document.body.style.animation = 'rainbow 2s infinite';
        
        // Create confetti effect
        for (let i = 0; i < 100; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.style.cssText = `
                    position: fixed;
                    width: 10px;
                    height: 10px;
                    background: hsl(${Math.random() * 360}, 100%, 50%);
                    top: -10px;
                    left: ${Math.random() * 100}%;
                    animation: fall ${2 + Math.random() * 3}s linear;
                    z-index: 9999;
                `;
                document.body.appendChild(confetti);
                setTimeout(() => confetti.remove(), 5000);
            }, i * 30);
        }
        
        setTimeout(() => {
            document.body.style.animation = '';
        }, 5000);
    }
});

// Add confetti animation
const style = document.createElement('style');
style.textContent = `
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
    @keyframes fall {
        to {
            transform: translateY(100vh) rotate(360deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================
// Performance Monitoring
// ============================================
if ('PerformanceObserver' in window) {
    const perfObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.duration > 100) {
                console.warn(`Slow operation detected: ${entry.name} took ${entry.duration}ms`);
            }
        }
    });
    
    perfObserver.observe({ entryTypes: ['measure'] });
}

// ============================================
// Console Easter Egg
// ============================================
console.log('%c🤖 AXON - Built with IBM Bob', 'font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding: 10px;');
console.log('%cGitHub Copilot for Your Operating System', 'font-size: 16px; color: #64748b; padding: 5px;');
console.log('%cTry the Konami code! ⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️BA', 'font-size: 14px; color: #6366f1; padding: 5px;');
console.log('%cInterested in the code? Check out: https://github.com/pratham092006/ibm-bob-hackathon', 'font-size: 12px; color: #10b981; padding: 5px;');

// ============================================
// Accessibility Enhancements
// ============================================
document.querySelectorAll('button, a').forEach(element => {
    if (!element.getAttribute('aria-label') && !element.textContent.trim()) {
        element.setAttribute('aria-label', 'Interactive element');
    }
});

// ============================================
// Lazy Loading for Images (if any added later)
// ============================================
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            }
        });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// ============================================
// Initialize All Features
// ============================================
console.log('✅ AXON Landing Page Loaded Successfully');
console.log('🎨 All animations initialized');
console.log('🚀 Ready for production!');

// Made with Bob
