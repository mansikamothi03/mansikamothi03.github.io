// Particle Background Animation
const canvas = document.getElementById('particles');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particlesArray = [];
const numberOfParticles = 100;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 1;
        this.speedX = Math.random() * 0.5 - 0.25;
        this.speedY = Math.random() * 0.5 - 0.25;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x > canvas.width || this.x < 0) {
            this.speedX = -this.speedX;
        }
        if (this.y > canvas.height || this.y < 0) {
            this.speedY = -this.speedY;
        }
    }

    draw() {
        ctx.fillStyle = 'rgba(99, 102, 241, 0.5)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

function initParticles() {
    particlesArray = [];
    for (let i = 0; i < numberOfParticles; i++) {
        particlesArray.push(new Particle());
    }
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
        particlesArray[i].draw();
        
        for (let j = i; j < particlesArray.length; j++) {
            const dx = particlesArray[i].x - particlesArray[j].x;
            const dy = particlesArray[i].y - particlesArray[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 100) {
                ctx.strokeStyle = `rgba(99, 102, 241, ${0.2 - distance / 500})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                ctx.lineTo(particlesArray[j].x, particlesArray[j].y);
                ctx.stroke();
            }
        }
    }
    requestAnimationFrame(animateParticles);
}

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    initParticles();
});

initParticles();
animateParticles();

// Typing Effect
const typedTextSpan = document.getElementById('typed-text');
const textArray = ['Product Analyst', 'Data Enthusiast', 'Product Manager', 'Problem Solver'];
const typingDelay = 100;
const erasingDelay = 50;
const newTextDelay = 2000;
let textArrayIndex = 0;
let charIndex = 0;

function type() {
    if (charIndex < textArray[textArrayIndex].length) {
        typedTextSpan.textContent += textArray[textArrayIndex].charAt(charIndex);
        charIndex++;
        setTimeout(type, typingDelay);
    } else {
        setTimeout(erase, newTextDelay);
    }
}

function erase() {
    if (charIndex > 0) {
        typedTextSpan.textContent = textArray[textArrayIndex].substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, erasingDelay);
    } else {
        textArrayIndex++;
        if (textArrayIndex >= textArray.length) textArrayIndex = 0;
        setTimeout(type, typingDelay + 1100);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(type, newTextDelay + 250);
});

// Navbar Scroll Effect
const navbar = document.getElementById('navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
    
    lastScroll = currentScroll;
});

// Mobile Menu Toggle
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');

hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    hamburger.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburger.classList.remove('active');
    });
});

// Smooth Scrolling for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offsetTop = target.offsetTop - 80;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Animated Counter for Stats
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;

    const updateCounter = () => {
        current += increment;
        if (current < target) {
            element.textContent = Math.floor(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    };

    updateCounter();
}

// Intersection Observer for Animations
const observerOptions = {
    threshold: 0.2,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            
            // Animate counters when stats section is visible
            if (entry.target.classList.contains('stat-number')) {
                animateCounter(entry.target);
            }
            
            // Animate skill bars when skills section is visible
            if (entry.target.classList.contains('skill-category')) {
                const progressBars = entry.target.querySelectorAll('.progress');
                progressBars.forEach(bar => {
                    const progress = bar.getAttribute('data-progress');
                    setTimeout(() => {
                        bar.style.width = progress + '%';
                    }, 200);
                });
            }
        }
    });
}, observerOptions);

// Observe elements with data-aos attribute
document.querySelectorAll('[data-aos]').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'all 0.6s ease';
    observer.observe(el);
});

// Observe stat numbers
document.querySelectorAll('.stat-number').forEach(el => {
    observer.observe(el);
});

// Observe skill categories
document.querySelectorAll('.skill-category').forEach(el => {
    observer.observe(el);
});

// Form Validation and Submission Handler
const contactForm = document.getElementById('contact-form');

// Email validation regex
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Show error message
function showError(input, message) {
    const formGroup = input.parentElement;
    let errorDiv = formGroup.querySelector('.error-message');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            color: #ef4444;
            font-size: 0.85rem;
            margin-top: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        `;
        formGroup.appendChild(errorDiv);
    }
    
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    input.style.borderColor = '#ef4444';
}

// Clear error message
function clearError(input) {
    const formGroup = input.parentElement;
    const errorDiv = formGroup.querySelector('.error-message');
    
    if (errorDiv) {
        errorDiv.remove();
    }
    
    input.style.borderColor = '';
}

// Validate individual field
function validateField(input) {
    const value = input.value.trim();
    
    clearError(input);
    
    if (!value) {
        showError(input, 'This field is required');
        return false;
    }
    
    if (input.type === 'email' && !emailRegex.test(value)) {
        showError(input, 'Please enter a valid email address');
        return false;
    }
    
    if (input.id === 'name' && value.length < 2) {
        showError(input, 'Name must be at least 2 characters');
        return false;
    }
    
    if (input.id === 'message' && value.length < 10) {
        showError(input, 'Message must be at least 10 characters');
        return false;
    }
    
    return true;
}

// Add real-time validation
['name', 'email', 'subject', 'message'].forEach(id => {
    const input = document.getElementById(id);
    if (input) {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.value.trim()) {
                clearError(input);
            }
        });
    }
});

contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Get form inputs
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const subjectInput = document.getElementById('subject');
    const messageInput = document.getElementById('message');
    
    // Validate all fields
    const isNameValid = validateField(nameInput);
    const isEmailValid = validateField(emailInput);
    const isSubjectValid = validateField(subjectInput);
    const isMessageValid = validateField(messageInput);
    
    // If any field is invalid, stop submission
    if (!isNameValid || !isEmailValid || !isSubjectValid || !isMessageValid) {
        // Show error notification
        showNotification('Please fix the errors in the form', 'error');
        return;
    }
    
    // Show success message
    showNotification('Message sent successfully! I\'ll get back to you soon.', 'success');
    
    // Reset form
    contactForm.reset();
});

// Notification function
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    const bgColor = type === 'success'
        ? 'linear-gradient(135deg, #10b981, #059669)'
        : 'linear-gradient(135deg, #ef4444, #dc2626)';
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.5s ease;
        max-width: 400px;
    `;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem;">
            <i class="fas ${icon}" style="font-size: 1.5rem;"></i>
            <div>
                <strong>${type === 'success' ? 'Success!' : 'Error'}</strong>
                <p style="margin: 0; font-size: 0.9rem;">${message}</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.5s ease';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}

// Add slide animations for success message
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Parallax Effect for Hero Section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Add hover effect to project cards
document.querySelectorAll('.project-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-10px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
    });
});

// Cursor Trail Effect
let cursorTrail = [];
const trailLength = 10;

document.addEventListener('mousemove', (e) => {
    cursorTrail.push({ x: e.clientX, y: e.clientY });
    
    if (cursorTrail.length > trailLength) {
        cursorTrail.shift();
    }
    
    // Remove old trail elements
    document.querySelectorAll('.cursor-trail').forEach(el => el.remove());
    
    // Create new trail elements
    cursorTrail.forEach((pos, index) => {
        const trail = document.createElement('div');
        trail.className = 'cursor-trail';
        trail.style.cssText = `
            position: fixed;
            width: ${10 - index}px;
            height: ${10 - index}px;
            background: rgba(99, 102, 241, ${0.5 - index * 0.05});
            border-radius: 50%;
            pointer-events: none;
            left: ${pos.x}px;
            top: ${pos.y}px;
            transform: translate(-50%, -50%);
            z-index: 9999;
            transition: all 0.1s ease;
        `;
        document.body.appendChild(trail);
        
        setTimeout(() => trail.remove(), 100);
    });
});

// Add active state to navigation links based on scroll position
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const scrollY = window.pageYOffset;

    sections.forEach(section => {
        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 100;
        const sectionId = section.getAttribute('id');
        const navLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);

        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            document.querySelectorAll('.nav-link').forEach(link => {
                link.style.color = '';
            });
            if (navLink) {
                navLink.style.color = '#6366f1';
            }
        }
    });
});

// Add tilt effect to floating cards
document.querySelectorAll('.floating-card').forEach(card => {
    card.addEventListener('mouseenter', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-20px)`;
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
    });
});

// Add ripple effect to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.5);
            left: ${x}px;
            top: ${y}px;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;
        
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
});

// Add ripple animation
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

// Loading Animation
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

console.log('Portfolio loaded successfully! 🚀');
// Project Modal Data
const projectData = {
    analytics: {
        title: "Customer Analytics Dashboard",
        subtitle: "Comprehensive analytics solution for customer behavior tracking",
        icon: "fas fa-chart-line",
        metrics: [
            { value: "25%", label: "Retention Increase" },
            { value: "10K+", label: "Daily Active Users" },
            { value: "50+", label: "KPIs Tracked" },
            { value: "99.9%", label: "Uptime" }
        ],
        overview: "Developed a comprehensive analytics dashboard that transformed how the organization tracks and understands customer behavior. The solution integrated multiple data sources and provided real-time insights that led to a 25% improvement in customer retention.",
        features: [
            { icon: "fas fa-chart-pie", text: "Real-time customer behavior tracking across all touchpoints" },
            { icon: "fas fa-users", text: "Customer segmentation with ML-powered clustering" },
            { icon: "fas fa-bell", text: "Automated alerts for anomaly detection and churn prediction" },
            { icon: "fas fa-mobile-alt", text: "Mobile-responsive design for on-the-go insights" },
            { icon: "fas fa-sync", text: "Automated daily data refresh from 15+ sources" },
            { icon: "fas fa-shield-alt", text: "Enterprise-grade security and data governance" }
        ],
        techStack: ["Tableau", "SQL", "Python", "AWS", "Apache Airflow", "PostgreSQL"],
        dashboard: {
            title: "Dashboard Components",
            widgets: [
                { name: "Customer Journey Map", description: "Visual representation of customer touchpoints and conversion funnels" },
                { name: "Cohort Analysis", description: "Track customer behavior patterns across different cohorts over time" },
                { name: "Churn Prediction", description: "ML model predicting customer churn with 85% accuracy" },
                { name: "Revenue Analytics", description: "Real-time revenue tracking with forecasting capabilities" },
                { name: "Product Usage Metrics", description: "Feature adoption and engagement analytics" },
                { name: "Customer Satisfaction", description: "NPS scores and sentiment analysis from feedback" }
            ]
        },
        impact: "The dashboard became the primary tool for strategic decision-making, used daily by 50+ stakeholders across product, marketing, and executive teams. It enabled data-driven decisions that resulted in $2M+ in retained revenue."
    },
    optimization: {
        title: "Product Feature Optimization",
        subtitle: "A/B testing framework that drove 40% engagement increase",
        icon: "fas fa-mobile-alt",
        metrics: [
            { value: "40%", label: "Engagement Increase" },
            { value: "100+", label: "Tests Conducted" },
            { value: "5M+", label: "Users Impacted" },
            { value: "95%", label: "Confidence Level" }
        ],
        overview: "Led a comprehensive A/B testing initiative to optimize product features and user experience. Implemented a robust experimentation framework that enabled rapid iteration and data-driven product decisions, resulting in a 40% increase in user engagement.",
        features: [
            { icon: "fas fa-flask", text: "Comprehensive A/B testing framework with statistical rigor" },
            { icon: "fas fa-chart-line", text: "Real-time experiment monitoring and analysis" },
            { icon: "fas fa-users-cog", text: "Advanced user segmentation for targeted experiments" },
            { icon: "fas fa-brain", text: "Machine learning for experiment optimization" },
            { icon: "fas fa-code-branch", text: "Multi-variate testing capabilities" },
            { icon: "fas fa-tachometer-alt", text: "Automated performance tracking and reporting" }
        ],
        techStack: ["Optimizely", "Google Analytics", "Python", "R", "Mixpanel", "Amplitude"],
        dashboard: {
            title: "Experiment Results",
            widgets: [
                { name: "Conversion Funnel", description: "Optimized checkout flow increased conversions by 28%" },
                { name: "Onboarding Flow", description: "Redesigned onboarding improved activation rate by 35%" },
                { name: "Feature Discovery", description: "New navigation increased feature adoption by 45%" },
                { name: "Notification Strategy", description: "Personalized notifications boosted engagement by 52%" },
                { name: "Pricing Page", description: "A/B tested pricing display increased upgrades by 22%" },
                { name: "Search Functionality", description: "Enhanced search improved user satisfaction by 30%" }
            ]
        },
        impact: "The experimentation culture established through this initiative became a core part of the product development process. Over 100 experiments were conducted, with learnings directly influencing the product roadmap and contributing to a 40% overall increase in user engagement."
    },
    automation: {
        title: "Data Pipeline Automation",
        subtitle: "Automated ETL processes reducing manual work by 60%",
        icon: "fas fa-database",
        metrics: [
            { value: "60%", label: "Time Saved" },
            { value: "15+", label: "Data Sources" },
            { value: "1M+", label: "Records/Day" },
            { value: "100%", label: "Accuracy" }
        ],
        overview: "Designed and implemented an automated data pipeline that transformed manual, error-prone data collection processes into a robust, scalable system. The solution reduced manual work by 60% while improving data accuracy and enabling real-time analytics.",
        features: [
            { icon: "fas fa-robot", text: "Fully automated ETL processes with error handling" },
            { icon: "fas fa-clock", text: "Scheduled data refreshes with configurable intervals" },
            { icon: "fas fa-check-circle", text: "Data quality validation and anomaly detection" },
            { icon: "fas fa-envelope", text: "Automated alerting for pipeline failures" },
            { icon: "fas fa-history", text: "Historical data versioning and audit trails" },
            { icon: "fas fa-expand-arrows-alt", text: "Scalable architecture handling millions of records" }
        ],
        techStack: ["Python", "Apache Airflow", "AWS S3", "Snowflake", "dbt", "Docker"],
        dashboard: {
            title: "Pipeline Architecture",
            widgets: [
                { name: "Data Ingestion", description: "Automated extraction from 15+ sources including APIs, databases, and files" },
                { name: "Data Transformation", description: "Complex transformations using dbt for data modeling" },
                { name: "Data Quality", description: "Automated validation ensuring 100% data accuracy" },
                { name: "Monitoring Dashboard", description: "Real-time pipeline health monitoring and alerting" },
                { name: "Data Catalog", description: "Automated documentation of all data assets" },
                { name: "Performance Metrics", description: "Pipeline performance tracking and optimization" }
            ]
        },
        impact: "The automated pipeline freed up 20+ hours per week of manual work, allowing the team to focus on analysis rather than data collection. It became the foundation for all analytics initiatives and enabled the organization to scale its data operations without proportional headcount increases."
    }
};

// Open Project Modal
function openProjectModal(projectId) {
    const project = projectData[projectId];
    if (!project) return;

    const modal = document.getElementById('projectModal');
    const modalBody = document.getElementById('modalBody');

    // Build modal content
    let modalHTML = `
        <div class="project-modal-header">
            <i class="${project.icon}" style="font-size: 3rem; margin-bottom: 1rem;"></i>
            <h2>${project.title}</h2>
            <p>${project.subtitle}</p>
        </div>
        <div class="project-modal-body">
            <div class="project-section">
                <h3><i class="fas fa-chart-bar"></i> Key Metrics</h3>
                <div class="project-metrics">
                    ${project.metrics.map(metric => `
                        <div class="metric-card">
                            <div class="metric-value">${metric.value}</div>
                            <div class="metric-label">${metric.label}</div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="project-section">
                <h3><i class="fas fa-info-circle"></i> Overview</h3>
                <p style="color: var(--text-secondary); line-height: 1.8; font-size: 1.1rem;">${project.overview}</p>
            </div>

            <div class="project-section">
                <h3><i class="fas fa-star"></i> Key Features</h3>
                <ul class="project-features">
                    ${project.features.map(feature => `
                        <li><i class="${feature.icon}"></i> ${feature.text}</li>
                    `).join('')}
                </ul>
            </div>

            <div class="project-section">
                <h3><i class="fas fa-code"></i> Technology Stack</h3>
                <div class="tech-stack">
                    ${project.techStack.map(tech => `
                        <div class="tech-item">${tech}</div>
                    `).join('')}
                </div>
            </div>

            <div class="project-section">
                <h3><i class="fas fa-trophy"></i> Impact</h3>
                <p style="color: var(--text-secondary); line-height: 1.8; font-size: 1.1rem; background: var(--dark-bg); padding: 1.5rem; border-radius: 10px; border-left: 4px solid var(--primary-color);">${project.impact}</p>
            </div>
        </div>
    `;

    modalBody.innerHTML = modalHTML;
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    // Add animation to metric cards
    setTimeout(() => {
        document.querySelectorAll('.metric-card').forEach((card, index) => {
            card.style.animation = `fadeInUp 0.5s ease ${index * 0.1}s both`;
        });
    }, 100);
}

// Close Project Modal
function closeProjectModal() {
    const modal = document.getElementById('projectModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('projectModal');
    if (event.target === modal) {
        closeProjectModal();
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeProjectModal();
    }
});
// Theme Toggle Function
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update icon with animation
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
    
    // Show theme change notification
    const themeName = newTheme.charAt(0).toUpperCase() + newTheme.slice(1);
    showNotification(`Switched to ${themeName} Mode`, 'success');
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = savedTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
});

// Quiz System
const quizData = {
    designer: [
        {
            question: "What design tool do you primarily use?",
            options: ["Figma", "Adobe XD", "Sketch", "Other"],
            correct: 0
        },
        {
            question: "Which design principle is most important to you?",
            options: ["Consistency", "Simplicity", "Innovation", "Accessibility"],
            correct: 3
        },
        {
            question: "How do you approach user research?",
            options: ["Surveys", "Interviews", "Analytics", "All of the above"],
            correct: 3
        },
        {
            question: "What's your preferred prototyping method?",
            options: ["Low-fidelity wireframes", "High-fidelity mockups", "Interactive prototypes", "Code prototypes"],
            correct: 2
        },
        {
            question: "How do you measure design success?",
            options: ["User satisfaction", "Conversion rates", "Task completion", "All metrics combined"],
            correct: 3
        }
    ],
    hr: [
        {
            question: "What's most important in a candidate?",
            options: ["Technical skills", "Cultural fit", "Experience", "Growth potential"],
            correct: 3
        },
        {
            question: "How do you evaluate soft skills?",
            options: ["Behavioral questions", "Case studies", "References", "All methods"],
            correct: 3
        },
        {
            question: "What's your hiring timeline preference?",
            options: ["Quick (1-2 weeks)", "Standard (3-4 weeks)", "Thorough (5+ weeks)", "Flexible"],
            correct: 3
        },
        {
            question: "How important is remote work capability?",
            options: ["Essential", "Preferred", "Nice to have", "Not important"],
            correct: 0
        },
        {
            question: "What attracts you to a candidate's portfolio?",
            options: ["Project variety", "Technical depth", "Problem-solving approach", "All aspects"],
            correct: 3
        }
    ],
    hm: [
        {
            question: "What technical skill is most valuable?",
            options: ["Frontend expertise", "Backend expertise", "Full-stack ability", "Problem-solving"],
            correct: 3
        },
        {
            question: "How do you assess code quality?",
            options: ["Code reviews", "Live coding", "Portfolio projects", "All methods"],
            correct: 3
        },
        {
            question: "What's your team structure preference?",
            options: ["Specialists", "Generalists", "Mixed team", "Depends on project"],
            correct: 3
        },
        {
            question: "How important is system design knowledge?",
            options: ["Critical", "Important", "Nice to have", "Can be learned"],
            correct: 0
        },
        {
            question: "What collaboration tool do you prefer?",
            options: ["Slack", "Teams", "Discord", "Any works"],
            correct: 3
        }
    ],
    general: [
        {
            question: "What interests you most about web development?",
            options: ["Creating beautiful UIs", "Solving complex problems", "Building useful tools", "All of it"],
            correct: 3
        },
        {
            question: "How do you stay updated with tech trends?",
            options: ["Blogs/articles", "Courses", "Projects", "Community engagement"],
            correct: 3
        },
        {
            question: "What's your learning style?",
            options: ["Reading documentation", "Video tutorials", "Hands-on practice", "All methods"],
            correct: 2
        },
        {
            question: "How do you approach new technologies?",
            options: ["Jump right in", "Read docs first", "Take a course", "Build a project"],
            correct: 3
        },
        {
            question: "What motivates you in tech?",
            options: ["Innovation", "Impact", "Learning", "All of these"],
            correct: 3
        }
    ]
};

let currentQuiz = null;
let currentQuestion = 0;
let userAnswers = [];

function openQuiz() {
    document.getElementById('quizModal').style.display = 'flex';
    showQuizIntro();
}

function closeQuiz() {
    document.getElementById('quizModal').style.display = 'none';
    resetQuiz();
}

function showQuizIntro() {
    document.getElementById('quizIntro').style.display = 'block';
    document.getElementById('quizQuestions').style.display = 'none';
    document.getElementById('quizResults').style.display = 'none';
}

function startQuiz(role) {
    currentQuiz = quizData[role];
    currentQuestion = 0;
    userAnswers = [];
    
    document.getElementById('quizIntro').style.display = 'none';
    document.getElementById('quizQuestions').style.display = 'block';
    
    showQuestion();
}

function showQuestion() {
    const question = currentQuiz[currentQuestion];
    const progress = ((currentQuestion + 1) / currentQuiz.length) * 100;
    
    document.querySelector('.progress-fill').style.width = progress + '%';
    document.getElementById('questionNumber').textContent = 
        `Question ${currentQuestion + 1} of ${currentQuiz.length}`;
    
    document.getElementById('currentQuestion').textContent = question.question;
    
    const optionsContainer = document.getElementById('answerOptions');
    optionsContainer.innerHTML = '';
    
    question.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'answer-option';
        button.textContent = option;
        button.onclick = () => selectAnswer(index);
        
        if (userAnswers[currentQuestion] === index) {
            button.classList.add('selected');
        }
        
        optionsContainer.appendChild(button);
    });
    
    document.getElementById('prevBtn').disabled = currentQuestion === 0;
    document.getElementById('nextBtn').style.display = 
        currentQuestion === currentQuiz.length - 1 ? 'none' : 'flex';
    document.getElementById('submitBtn').style.display = 
        currentQuestion === currentQuiz.length - 1 ? 'flex' : 'none';
}

function selectAnswer(index) {
    userAnswers[currentQuestion] = index;
    
    document.querySelectorAll('.answer-option').forEach((btn, i) => {
        btn.classList.toggle('selected', i === index);
    });
}

function previousQuestion() {
    if (currentQuestion > 0) {
        currentQuestion--;
        showQuestion();
    }
}

function nextQuestion() {
    if (currentQuestion < currentQuiz.length - 1) {
        currentQuestion++;
        showQuestion();
    }
}

function submitQuiz() {
    let score = 0;
    currentQuiz.forEach((question, index) => {
        if (userAnswers[index] === question.correct) {
            score++;
        }
    });
    
    showResults(score);
}

function showResults(score) {
    const percentage = (score / currentQuiz.length) * 100;
    
    document.getElementById('quizQuestions').style.display = 'none';
    document.getElementById('quizResults').style.display = 'block';
    
    document.getElementById('scorePercentage').textContent = Math.round(percentage);
    document.getElementById('scoreText').textContent = `${score} out of ${currentQuiz.length}`;
    
    // Animate score circle
    const circle = document.querySelector('.score-circle circle:last-child');
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (percentage / 100) * circumference;
    circle.style.strokeDashoffset = offset;
    
    let message = '';
    if (percentage >= 80) {
        message = "Excellent! You really know your stuff!";
    } else if (percentage >= 60) {
        message = "Great job! You're on the right track!";
    } else {
        message = "Good effort! Keep learning and growing!";
    }
    
    document.getElementById('resultMessage').textContent = message;
}

function retakeQuiz() {
    showQuizIntro();
}

function resetQuiz() {
    currentQuiz = null;
    currentQuestion = 0;
    userAnswers = [];
    showQuizIntro();
}
// ============================================================
// SCROLL PROGRESS BAR
// ============================================================
function updateScrollProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    const bar = document.getElementById('scrollProgress');
    if (bar) bar.style.width = progress + '%';
}

// ============================================================
// CURSOR GLOW
// ============================================================
function initCursorGlow() {
    const glow = document.getElementById('cursorGlow');
    if (!glow) return;
    document.addEventListener('mousemove', (e) => {
        glow.style.left = e.clientX + 'px';
        glow.style.top = e.clientY + 'px';
        glow.style.opacity = '1';
    });
    document.addEventListener('mouseleave', () => {
        glow.style.opacity = '0';
    });
}

// ============================================================
// BACK TO TOP
// ============================================================
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateBackToTop() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;
    if (window.scrollY > 400) {
        btn.classList.add('visible');
    } else {
        btn.classList.remove('visible');
    }
}

// ============================================================
// PROJECT FILTER TABS
// ============================================================
function initProjectFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.project-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.getAttribute('data-filter');

            cards.forEach(card => {
                const category = card.getAttribute('data-category');
                if (filter === 'all' || category === filter) {
                    card.classList.remove('hidden');
                    card.classList.add('fade-in');
                    setTimeout(() => card.classList.remove('fade-in'), 400);
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
}

// ============================================================
// WIRE UP SCROLL EVENTS & INIT
// ============================================================
window.addEventListener('scroll', () => {
    updateScrollProgress();
    updateBackToTop();
});

document.addEventListener('DOMContentLoaded', () => {
    initCursorGlow();
    initProjectFilters();
    updateScrollProgress();
    updateBackToTop();
});