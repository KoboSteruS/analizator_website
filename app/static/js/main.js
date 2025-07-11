/**
 * Основной JavaScript файл для LendingAnalyzer
 * Содержит логику навигации, анимации и взаимодействий
 */

// DOM загружен
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initAnimations();
    initScrollEffects();
    initContactForm();
});

/**
 * Инициализация навигации
 */
function initNavigation() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navbar = document.querySelector('.navbar');
    
    // Мобильное меню
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Закрытие меню при клике на ссылку
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }
    
    // Изменение прозрачности навбара при скролле
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                navbar.style.background = 'rgba(15, 15, 35, 0.98)';
            } else {
                navbar.style.background = 'rgba(15, 15, 35, 0.95)';
            }
        });
    }
    
    // Активная ссылка в навигации
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = 'var(--primary-color)';
        }
    });
}

/**
 * Инициализация анимаций
 */
function initAnimations() {
    // Настройка Intersection Observer для анимаций
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                
                // Анимация с задержкой для элементов в сетке
                const delay = entry.target.style.animationDelay || '0s';
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0) translateX(0)';
                }, parseFloat(delay) * 1000);
            }
        });
    }, observerOptions);
    
    // Наблюдение за элементами с анимацией
    const animatedElements = document.querySelectorAll('[class*="animate-"]');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        
        if (el.classList.contains('animate-fadeInUp')) {
            el.style.transform = 'translateY(30px)';
        } else if (el.classList.contains('animate-fadeInLeft')) {
            el.style.transform = 'translateX(-30px)';
        } else if (el.classList.contains('animate-fadeInRight')) {
            el.style.transform = 'translateX(30px)';
        }
        
        observer.observe(el);
    });
}

/**
 * Эффекты при скролле
 */
function initScrollEffects() {
    // Плавный скролл для якорных ссылок
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
    
    // Параллакс эффект для hero секции
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translate3d(0, ${rate}px, 0)`;
        });
    }
}

/**
 * Инициализация контактной формы
 */
function initContactForm() {
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            
            // Показать загрузку
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="loading"></span> Отправка...';
            
            try {
                const response = await fetch('/contact', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showNotification('Сообщение успешно отправлено!', 'success');
                    contactForm.reset();
                } else {
                    showNotification(result.message || 'Произошла ошибка', 'error');
                }
            } catch (error) {
                console.error('Ошибка отправки формы:', error);
                showNotification('Произошла ошибка при отправке', 'error');
            } finally {
                // Восстановить кнопку
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
}

/**
 * Показать уведомление
 */
function showNotification(message, type = 'info') {
    // Создать элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Стили для уведомления
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: 'var(--radius-lg)',
        color: 'white',
        fontWeight: '500',
        zIndex: '9999',
        opacity: '0',
        transform: 'translateX(100%)',
        transition: 'all 0.3s ease-out'
    });
    
    // Цвета в зависимости от типа
    switch (type) {
        case 'success':
            notification.style.background = 'var(--success-color)';
            break;
        case 'error':
            notification.style.background = 'var(--error-color)';
            break;
        default:
            notification.style.background = 'var(--primary-color)';
    }
    
    // Добавить в DOM
    document.body.appendChild(notification);
    
    // Показать с анимацией
    requestAnimationFrame(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    });
    
    // Автоматически скрыть через 5 секунд
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
    
    // Закрытие по клику
    notification.addEventListener('click', () => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    });
}

/**
 * Утилиты
 */

// Дебаунс функция
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Троттл функция
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Проверка мобильного устройства
function isMobile() {
    return window.innerWidth <= 768;
}

// Проверка поддержки touch
function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

// Экспорт функций для использования в других скриптах
window.LendingAnalyzer = {
    showNotification,
    debounce,
    throttle,
    isMobile,
    isTouchDevice
}; 