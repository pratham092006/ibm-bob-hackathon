/* ============================================
   AXON Landing Page - Interactive JavaScript
   Playful, Fun, Engaging Interactions
   ============================================ */

// ============================================
// Mobile Menu Toggle
// ============================================
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const mobileMenu = document.querySelector('.mobile-menu');
const mobileLinks = document.querySelectorAll('.mobile-link');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('visible');
        mobileMenuBtn.classList.toggle('active');
        
        // Animate hamburger icon
        const spans = mobileMenuBtn.querySelectorAll('span');
        if (mobileMenu.classList.contains('visible')) {
            spans[0].style.transform = 'rotate(45deg) translateY(8px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translateY(-8px)';
        } else {
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
        }
    });
    
    // Close menu when clicking a link
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('visible');
            const spans = mobileMenuBtn.querySelectorAll('span');
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
        });
    });
}

// ============================================
// Smooth Scrolling for Navigation Links
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80; // Account for fixed navbar
            const targetPosition = target.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ============================================
// Navbar Scroll Effect
// ============================================
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    // Add shadow on scroll
    if (currentScroll > 50) {
        navbar.style.boxShadow = '0 4px 20px rgba(147, 51, 234, 0.15)';
    } else {
        navbar.style.boxShadow = '0 2px 8px rgba(147, 51, 234, 0.1)';
    }
    
    lastScroll = currentScroll;
});

// ============================================
// FAQ Accordion
// ============================================
const faqItems = document.querySelectorAll('.faq-item');

faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    
    question.addEventListener('click', () => {
        // Close other items
        faqItems.forEach(otherItem => {
            if (otherItem !== item && otherItem.classList.contains('active')) {
                otherItem.classList.remove('active');
            }
        });
        
        // Toggle current item
        item.classList.toggle('active');
        
        // Add fun bounce animation
        if (item.classList.contains('active')) {
            const icon = question.querySelector('.faq-icon');
            icon.style.animation = 'none';
            setTimeout(() => {
                icon.style.animation = 'bounce 0.5s ease';
            }, 10);
        }
    });
});

// ============================================
// Intersection Observer for Scroll Animations
// ============================================
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

// Observe feature cards
document.querySelectorAll('.feature-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(50px)';
    card.style.transition = `all 0.6s ease ${index * 0.1}s`;
    observer.observe(card);
});

// Observe steps
document.querySelectorAll('.step').forEach((step, index) => {
    step.style.opacity = '0';
    step.style.transform = 'translateX(-50px)';
    step.style.transition = `all 0.6s ease ${index * 0.2}s`;
    observer.observe(step);
});

// ============================================
// Floating Shapes Animation Enhancement
// ============================================
const shapes = document.querySelectorAll('.shape');

shapes.forEach((shape, index) => {
    // Add random movement on mouse move
    document.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth - 0.5) * 20;
        const y = (e.clientY / window.innerHeight - 0.5) * 20;
        
        shape.style.transform = `translate(${x * (index + 1)}px, ${y * (index + 1)}px)`;
    });
});

// ============================================
// Download Button Click Animation
// ============================================
const downloadBtn = document.querySelector('.btn-download');

if (downloadBtn) {
    downloadBtn.addEventListener('click', (e) => {
        // Create confetti effect
        createConfetti(e.clientX, e.clientY);
        
        // Add success message
        const originalText = downloadBtn.innerHTML;
        downloadBtn.innerHTML = '<span class="btn-icon">✅</span> Starting Download...';
        
        setTimeout(() => {
            downloadBtn.innerHTML = originalText;
        }, 3000);
    });
}

// ============================================
// Confetti Effect
// ============================================
function createConfetti(x, y) {
    const colors = ['#9333EA', '#F59E0B', '#EC4899', '#3B82F6', '#10B981'];
    const confettiCount = 30;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'fixed';
        confetti.style.left = x + 'px';
        confetti.style.top = y + 'px';
        confetti.style.width = '10px';
        confetti.style.height = '10px';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.borderRadius = '50%';
        confetti.style.pointerEvents = 'none';
        confetti.style.zIndex = '9999';
        confetti.style.transition = 'all 1s ease-out';
        
        document.body.appendChild(confetti);
        
        // Animate confetti
        setTimeout(() => {
            const angle = (Math.PI * 2 * i) / confettiCount;
            const velocity = 100 + Math.random() * 100;
            const tx = Math.cos(angle) * velocity;
            const ty = Math.sin(angle) * velocity + 200;
            
            confetti.style.transform = `translate(${tx}px, ${ty}px) rotate(${Math.random() * 360}deg)`;
            confetti.style.opacity = '0';
        }, 10);
        
        // Remove confetti
        setTimeout(() => {
            confetti.remove();
        }, 1000);
    }
}

// ============================================
// Robot Animation on Hover
// ============================================
const robotIllustration = document.querySelector('.robot-illustration');

if (robotIllustration) {
    robotIllustration.addEventListener('mouseenter', () => {
        robotIllustration.style.animation = 'none';
        setTimeout(() => {
            robotIllustration.style.animation = 'bounce 0.5s ease';
        }, 10);
    });
    
    robotIllustration.addEventListener('mouseleave', () => {
        robotIllustration.style.animation = 'float 3s infinite ease-in-out';
    });
}

// ============================================
// Feature Card Tilt Effect
// ============================================
const featureCards = document.querySelectorAll('.feature-card');

featureCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
    });
});

// ============================================
// Typing Effect for Hero Title
// ============================================
const heroTitle = document.querySelector('.hero-title');
if (heroTitle) {
    const gradientText = heroTitle.querySelector('.gradient-text');
    if (gradientText) {
        const text = gradientText.textContent;
        gradientText.textContent = '';
        gradientText.style.display = 'inline-block';
        
        let index = 0;
        const typingSpeed = 100;
        
        function typeText() {
            if (index < text.length) {
                gradientText.textContent += text.charAt(index);
                index++;
                setTimeout(typeText, typingSpeed);
            }
        }
        
        // Start typing after a short delay
        setTimeout(typeText, 500);
    }
}

// ============================================
// Stats Counter Animation
// ============================================
const stats = document.querySelectorAll('.stat-number');

const animateCounter = (element, target, duration = 2000) => {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
};

// Observe stats for animation
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const stat = entry.target;
            const text = stat.textContent;
            
            if (text.includes('%')) {
                animateCounter(stat, 100);
                setTimeout(() => {
                    stat.textContent = '100%';
                }, 2000);
            } else if (text.includes('+')) {
                animateCounter(stat, 10);
                setTimeout(() => {
                    stat.textContent = '10+';
                }, 2000);
            }
            
            statsObserver.unobserve(stat);
        }
    });
}, { threshold: 0.5 });

stats.forEach(stat => {
    statsObserver.observe(stat);
});

// ============================================
// Easter Egg: Konami Code
// ============================================
let konamiCode = [];
const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.key);
    konamiCode = konamiCode.slice(-10);
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        activateEasterEgg();
        konamiCode = [];
    }
});

function activateEasterEgg() {
    // Make all shapes rainbow colored
    const shapes = document.querySelectorAll('.shape');
    shapes.forEach((shape, index) => {
        shape.style.background = `linear-gradient(135deg, 
            hsl(${index * 60}, 70%, 60%), 
            hsl(${index * 60 + 60}, 70%, 60%))`;
        shape.style.opacity = '0.3';
        shape.style.animation = `float ${2 + index}s infinite ease-in-out, rotate 5s infinite linear`;
    });
    
    // Show celebration message
    const message = document.createElement('div');
    message.textContent = '🎉 You found the secret! AXON loves you! 🎉';
    message.style.position = 'fixed';
    message.style.top = '50%';
    message.style.left = '50%';
    message.style.transform = 'translate(-50%, -50%)';
    message.style.background = 'linear-gradient(135deg, #9333EA, #F59E0B)';
    message.style.color = 'white';
    message.style.padding = '2rem 3rem';
    message.style.borderRadius = '2rem';
    message.style.fontSize = '1.5rem';
    message.style.fontWeight = 'bold';
    message.style.zIndex = '10000';
    message.style.boxShadow = '0 20px 60px rgba(147, 51, 234, 0.4)';
    message.style.animation = 'bounce 0.5s ease';
    
    document.body.appendChild(message);
    
    // Create massive confetti
    for (let i = 0; i < 100; i++) {
        setTimeout(() => {
            createConfetti(
                Math.random() * window.innerWidth,
                Math.random() * window.innerHeight
            );
        }, i * 50);
    }
    
    setTimeout(() => {
        message.remove();
    }, 3000);
}

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
// Button Ripple Effect
// ============================================
const buttons = document.querySelectorAll('.btn');

buttons.forEach(button => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.5)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s ease-out';
        ripple.style.pointerEvents = 'none';
        
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});

// Add ripple animation to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================
// Copy to Clipboard for Code Snippets
// ============================================
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success message
        const message = document.createElement('div');
        message.textContent = '✅ Copied to clipboard!';
        message.style.position = 'fixed';
        message.style.bottom = '20px';
        message.style.right = '20px';
        message.style.background = 'linear-gradient(135deg, #10B981, #059669)';
        message.style.color = 'white';
        message.style.padding = '1rem 1.5rem';
        message.style.borderRadius = '1rem';
        message.style.fontWeight = 'bold';
        message.style.zIndex = '10000';
        message.style.boxShadow = '0 10px 30px rgba(16, 185, 129, 0.3)';
        message.style.animation = 'slideInRight 0.3s ease';
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => message.remove(), 300);
        }, 2000);
    });
}

// ============================================
// Loading Animation for Page Load
// ============================================
window.addEventListener('load', () => {
    // Fade in all sections
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
    
    // Animate hero elements
    const heroElements = document.querySelectorAll('.hero-badge, .hero-title, .hero-subtitle, .hero-buttons, .hero-stats');
    heroElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 200 + index * 100);
    });
});

// ============================================
// Cursor Trail Effect (Optional Fun Feature)
// ============================================
let cursorTrail = [];
const maxTrailLength = 10;

document.addEventListener('mousemove', (e) => {
    // Only on desktop
    if (window.innerWidth > 768) {
        const trail = document.createElement('div');
        trail.style.position = 'fixed';
        trail.style.left = e.clientX + 'px';
        trail.style.top = e.clientY + 'px';
        trail.style.width = '8px';
        trail.style.height = '8px';
        trail.style.background = 'linear-gradient(135deg, #9333EA, #F59E0B)';
        trail.style.borderRadius = '50%';
        trail.style.pointerEvents = 'none';
        trail.style.zIndex = '9998';
        trail.style.opacity = '0.5';
        trail.style.transition = 'all 0.3s ease';
        
        document.body.appendChild(trail);
        cursorTrail.push(trail);
        
        if (cursorTrail.length > maxTrailLength) {
            const oldTrail = cursorTrail.shift();
            oldTrail.style.opacity = '0';
            oldTrail.style.transform = 'scale(0)';
            setTimeout(() => oldTrail.remove(), 300);
        }
    }
});

// ============================================
// Console Easter Egg
// ============================================
console.log('%c🚀 AXON - Your AI Desktop Buddy!', 'font-size: 20px; font-weight: bold; color: #9333EA;');
console.log('%cBuilt with ❤️ for IBM Bob Hackathon', 'font-size: 14px; color: #F59E0B;');
console.log('%cWant to contribute? Check out: https://github.com/pratham092006/ibm-bob-hackathon', 'font-size: 12px; color: #3B82F6;');
console.log('%cTry the Konami Code for a surprise! ⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️BA', 'font-size: 12px; color: #EC4899;');

// ============================================
// Performance Optimization
// ============================================
// Lazy load images
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
// Accessibility Enhancements
// ============================================
// Add keyboard navigation for FAQ
faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    question.setAttribute('role', 'button');
    question.setAttribute('aria-expanded', 'false');
    
    question.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            question.click();
            question.setAttribute('aria-expanded', item.classList.contains('active'));
        }
    });
});

// ============================================
// Analytics (Placeholder)
// ============================================
function trackEvent(category, action, label) {
    console.log(`Event tracked: ${category} - ${action} - ${label}`);
    // Add your analytics code here (Google Analytics, etc.)
}

// Track button clicks
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', () => {
        trackEvent('Button', 'Click', btn.textContent.trim());
    });
});

console.log('%c✨ All systems ready! AXON is live!', 'font-size: 16px; font-weight: bold; color: #10B981;');

// Made with Bob
