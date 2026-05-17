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

// Navbar background on scroll
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all feature cards, steps, and use cases
document.querySelectorAll('.feature-card, .step, .use-case, .doc-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
});

// Terminal typing animation
const terminalLines = document.querySelectorAll('.terminal-line');
let delay = 0;

terminalLines.forEach((line, index) => {
    line.style.opacity = '0';
    setTimeout(() => {
        line.style.transition = 'opacity 0.5s ease-in';
        line.style.opacity = '1';
    }, delay);
    delay += 800;
});

// Copy code to clipboard
document.querySelectorAll('.code-block').forEach(block => {
    block.style.position = 'relative';
    block.style.cursor = 'pointer';
    
    const copyButton = document.createElement('button');
    copyButton.textContent = '📋 Copy';
    copyButton.style.position = 'absolute';
    copyButton.style.top = '10px';
    copyButton.style.right = '10px';
    copyButton.style.padding = '0.5rem 1rem';
    copyButton.style.background = 'rgba(99, 102, 241, 0.8)';
    copyButton.style.color = 'white';
    copyButton.style.border = 'none';
    copyButton.style.borderRadius = '6px';
    copyButton.style.cursor = 'pointer';
    copyButton.style.fontSize = '0.875rem';
    copyButton.style.fontWeight = '600';
    copyButton.style.transition = 'all 0.3s';
    
    copyButton.addEventListener('mouseenter', () => {
        copyButton.style.background = 'rgba(99, 102, 241, 1)';
        copyButton.style.transform = 'scale(1.05)';
    });
    
    copyButton.addEventListener('mouseleave', () => {
        copyButton.style.background = 'rgba(99, 102, 241, 0.8)';
        copyButton.style.transform = 'scale(1)';
    });
    
    copyButton.addEventListener('click', (e) => {
        e.stopPropagation();
        const code = block.querySelector('code').textContent;
        navigator.clipboard.writeText(code).then(() => {
            copyButton.textContent = '✅ Copied!';
            setTimeout(() => {
                copyButton.textContent = '📋 Copy';
            }, 2000);
        });
    });
    
    block.appendChild(copyButton);
});

// Stats counter animation
const animateCounter = (element, target) => {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target + (element.dataset.suffix || '');
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current) + (element.dataset.suffix || '');
        }
    }, 30);
};

// Observe stats
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.dataset.animated) {
            const target = parseInt(entry.target.textContent);
            entry.target.dataset.animated = 'true';
            animateCounter(entry.target, target);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-number').forEach(stat => {
    // Store suffix if present
    const text = stat.textContent;
    if (text.includes('+')) {
        stat.dataset.suffix = '+';
        stat.textContent = text.replace('+', '');
    } else if (text.includes('%')) {
        stat.dataset.suffix = '%';
        stat.textContent = text.replace('%', '');
    }
    statsObserver.observe(stat);
});

// Add hover effect to comparison table rows
document.querySelectorAll('.comparison-table tbody tr').forEach(row => {
    row.addEventListener('mouseenter', () => {
        row.style.transform = 'scale(1.02)';
        row.style.transition = 'transform 0.3s ease';
        row.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
    });
    
    row.addEventListener('mouseleave', () => {
        row.style.transform = 'scale(1)';
        row.style.boxShadow = 'none';
    });
});

// Mobile menu toggle (if needed in future)
const createMobileMenu = () => {
    const navLinks = document.querySelector('.nav-links');
    const menuButton = document.createElement('button');
    menuButton.innerHTML = '☰';
    menuButton.style.display = 'none';
    menuButton.style.fontSize = '1.5rem';
    menuButton.style.background = 'none';
    menuButton.style.border = 'none';
    menuButton.style.cursor = 'pointer';
    
    // Show menu button on mobile
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
            navLinks.style.background = 'white';
            navLinks.style.padding = '1rem';
            navLinks.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
        } else {
            navLinks.style.display = 'none';
        }
    });
    
    document.querySelector('.navbar .container').appendChild(menuButton);
    window.addEventListener('resize', checkMobile);
    checkMobile();
};

// Initialize mobile menu
createMobileMenu();

// Add parallax effect to hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroVisual = document.querySelector('.hero-visual');
    if (heroVisual && scrolled < window.innerHeight) {
        heroVisual.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Add loading animation
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease-in';
        document.body.style.opacity = '1';
    }, 100);
});

// Easter egg: Konami code
let konamiCode = [];
const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.key);
    konamiCode = konamiCode.slice(-10);
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        document.body.style.animation = 'rainbow 2s infinite';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 5000);
    }
});

// Add rainbow animation for easter egg
const style = document.createElement('style');
style.textContent = `
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
`;
document.head.appendChild(style);

console.log('%c🤖 AXON - Built with IBM Bob', 'font-size: 20px; font-weight: bold; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;');
console.log('%cGitHub Copilot for Your Operating System', 'font-size: 14px; color: #64748b;');
console.log('%cTry the Konami code! ⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️BA', 'font-size: 12px; color: #6366f1;');

// Made with Bob
