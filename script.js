// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化导航菜单
    initNavigation();
    
    // 初始化滚动效果
    initScrollEffects();
    
    // 初始化画廊过滤
    initGalleryFilter();
    
    // 初始化表单验证
    initFormValidation();
    
    // 初始化统计数字动画
    initCountAnimation();
    
    // 初始化滚动到顶部按钮
    initScrollToTop();
    
    // 初始化平滑滚动
    initSmoothScroll();
    
    // 加载动画
    initPageLoader();
    
    // 初始化微信弹窗
    initWechatModal();
    
    // 重置所有表单状态，确保从感谢页面返回后表单状态正常
    resetAllForms();
    
    // 轮播图功能增强
    const carousel = document.querySelector('.carousel');
    if (carousel) {
        const items = carousel.querySelectorAll('.carousel-item');
        const prevBtn = carousel.querySelector('.carousel-prev');
        const nextBtn = carousel.querySelector('.carousel-next');
        const dotsContainer = carousel.querySelector('.carousel-dots');
        let currentIndex = 0;
        let autoSlideInterval;
        let touchStartX = 0;
        let touchEndX = 0;
        let isAnimating = false;
        
        // 初始化轮播图
        function initCarousel() {
            // 创建导航点
            if (dotsContainer) {
                dotsContainer.innerHTML = '';
                items.forEach((_, index) => {
                    const dot = document.createElement('div');
                    dot.classList.add('carousel-dot');
                    if (index === 0) dot.classList.add('active');
                    dot.addEventListener('click', () => {
                        if (!isAnimating && index !== currentIndex) {
                            goToSlide(index);
                        }
                    });
                    dotsContainer.appendChild(dot);
                });
            }
            
            // 设置第一个幻灯片为活动状态
            items[0].classList.add('active');
            startAutoSlide();
        }
        
        // 上一张幻灯片
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                if (isAnimating) return;
                
                clearInterval(autoSlideInterval);
                const prevIndex = (currentIndex - 1 + items.length) % items.length;
                goToSlide(prevIndex);
                startAutoSlide();
            });
        }
        
        // 下一张幻灯片
        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                if (isAnimating) return;
                
                clearInterval(autoSlideInterval);
                const nextIndex = (currentIndex + 1) % items.length;
                goToSlide(nextIndex);
                startAutoSlide();
            });
        }
        
        // 键盘导航
        document.addEventListener('keydown', function(e) {
            if (!carousel.matches(':hover')) return;
            
            if (e.key === 'ArrowLeft') {
                prevBtn.click();
            } else if (e.key === 'ArrowRight') {
                nextBtn.click();
            }
        });
        
        // 触摸支持
        carousel.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        carousel.addEventListener('touchend', function(e) {
            if (isAnimating) return;
            
            touchEndX = e.changedTouches[0].screenX;
            const diffX = touchEndX - touchStartX;
            
            if (Math.abs(diffX) > 50) { // 最小滑动距离
                if (diffX > 0) {
                    prevBtn.click(); // 右滑，上一张
                } else {
                    nextBtn.click(); // 左滑，下一张
                }
            }
        }, { passive: true });
        
        // 切换到指定幻灯片
        function goToSlide(index) {
            if (currentIndex === index) return;
            
            isAnimating = true;
            
            // 移除之前活动幻灯片的类
            const currentSlide = items[currentIndex];
            currentSlide.classList.add('leaving');
            currentSlide.classList.remove('active');
            
            // 设置新的活动幻灯片
            const nextSlide = items[index];
            nextSlide.classList.add('active', 'entering');
            
            // 更新导航点
            if (dotsContainer) {
                const dots = dotsContainer.querySelectorAll('.carousel-dot');
                dots[currentIndex].classList.remove('active');
                dots[index].classList.add('active');
            }
            
            // 动画完成后清理类
            setTimeout(() => {
                currentSlide.classList.remove('leaving');
                nextSlide.classList.remove('entering');
                isAnimating = false;
            }, 800);
            
            currentIndex = index;
        }
        
        // 自动轮播
        function startAutoSlide() {
            clearInterval(autoSlideInterval);
            autoSlideInterval = setInterval(() => {
                // 检查页面是否可见，避免后台切换动画
                if (document.visibilityState === 'visible' && !isAnimating) {
                    const nextIndex = (currentIndex + 1) % items.length;
                    goToSlide(nextIndex);
                }
            }, 5000);
        }
        
        // 页面可见性改变时处理自动轮播
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'visible') {
                startAutoSlide();
            } else {
                clearInterval(autoSlideInterval);
            }
        });
        
        // 初始化轮播图
        initCarousel();
    }
});

/**
 * 导航菜单初始化
 */
function initNavigation() {
    const header = document.querySelector('.main-header');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('nav');
    const navLinks = document.querySelectorAll('nav a');
    
    // 固定导航栏
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            header.classList.add('fixed');
        } else {
            header.classList.remove('fixed');
        }
    });
    
    // 移动菜单切换
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenuBtn.classList.toggle('active');
            nav.classList.toggle('active');
        });
    }
    
    // 导航链接点击关闭菜单
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            nav.classList.remove('active');
            mobileMenuBtn.classList.remove('active');
        });
    });
    
    // 活动链接高亮
    highlightActiveLink();
    window.addEventListener('scroll', throttle(highlightActiveLink, 100));
}

/**
 * 高亮当前活动的导航链接
 */
function highlightActiveLink() {
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('nav a');
    
    // 获取当前滚动位置
    const scrollPosition = window.scrollY + 150;
    
    // 检查每个部分是否在视图中
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');
        
        if (sectionId && scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            // 移除所有活动类
            navLinks.forEach(link => {
                link.classList.remove('active');
            });
            
            // 给当前部分的链接添加活动类
            const activeLink = document.querySelector(`nav a[href="#${sectionId}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
    });
}

/**
 * 节流函数，限制函数调用频率
 */
function throttle(func, delay) {
    let lastCall = 0;
    return function(...args) {
        const now = new Date().getTime();
        if (now - lastCall < delay) {
            return;
        }
        lastCall = now;
        return func(...args);
    };
}

/**
 * 滚动效果初始化
 */
function initScrollEffects() {
    // 滚动显示元素
    const scrollItems = document.querySelectorAll('.service-item, .about-content, .article-card, .gallery-item, .contact-method');
    
    // 初始隐藏元素
    scrollItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });
    
    // 检查元素是否在视图中
    const checkInView = function() {
        scrollItems.forEach((item, index) => {
            const rect = item.getBoundingClientRect();
            const windowHeight = window.innerHeight || document.documentElement.clientHeight;
            
            if (rect.top <= windowHeight * 0.85) {
                // 添加延迟动画
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    };
    
    // 首次检查
    checkInView();
    
    // 滚动时检查
    window.addEventListener('scroll', throttle(checkInView, 100));
}

/**
 * 画廊过滤初始化
 */
function initGalleryFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    if (filterBtns.length > 0) {
        // 默认激活"全部"按钮
        filterBtns[0].classList.add('active');
        
        // 过滤按钮点击事件
        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // 移除所有活动类
                filterBtns.forEach(b => b.classList.remove('active'));
                
                // 添加活动类到当前按钮
                this.classList.add('active');
                
                // 获取过滤器值
                const filterValue = this.getAttribute('data-filter');
                
                // 过滤项目
                galleryItems.forEach(item => {
                    if (filterValue === 'all') {
                        // 显示所有项目
                        showGalleryItem(item);
                    } else if (item.classList.contains(filterValue)) {
                        // 显示匹配项
                        showGalleryItem(item);
                    } else {
                        // 隐藏不匹配项
                        hideGalleryItem(item);
                    }
                });
            });
        });
    }
}

/**
 * 显示画廊项目
 */
function showGalleryItem(item) {
    // 检查项目是否已经隐藏
    if (item.style.display === 'none') {
        // 设置为不可见但占据空间
        item.style.display = 'block';
        item.style.opacity = '0';
        item.style.transform = 'scale(0.8)';
        
        // 使用延迟触发过渡动画
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'scale(1)';
        }, 10);
    }
}

/**
 * 隐藏画廊项目
 */
function hideGalleryItem(item) {
    // 首先淡出
    item.style.opacity = '0';
    item.style.transform = 'scale(0.8)';
    
    // 完成淡出后移除元素
    setTimeout(() => {
        item.style.display = 'none';
    }, 300);
}

/**
 * 表单验证初始化
 */
function initFormValidation() {
    const contactForm = document.querySelector('.contact-form form');
    
    if (contactForm) {
        console.log('找到联系表单:', contactForm.id);
        
        // 确保表单状态初始化
        resetSubmitButton(contactForm);
        
        // 添加自定义表单验证
        contactForm.addEventListener('submit', function(e) {
            // 暂时阻止表单提交，先进行验证
            e.preventDefault();
            console.log('联系表单提交触发');
            
            let isValid = true;
            
            // 获取所有必填字段
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const subject = document.getElementById('subject');
            const message = document.getElementById('message');
            const submitButton = contactForm.querySelector('button[type="submit"]');
            
            // 清除所有错误
            clearErrors();
            
            // 验证姓名
            if (!name || name.value.trim() === '') {
                showError(name, '请输入您的姓名');
                isValid = false;
                console.error('姓名验证失败');
            }
            
            // 验证邮箱
            if (!email || email.value.trim() === '') {
                showError(email, '请输入您的邮箱');
                isValid = false;
                console.error('邮箱为空验证失败');
            } else if (!isValidEmail(email.value)) {
                showError(email, '请输入有效的邮箱地址');
                isValid = false;
                console.error('邮箱格式验证失败');
            }
            
            // 验证主题
            if (!subject || subject.value.trim() === '') {
                showError(subject, '请输入主题');
                isValid = false;
                console.error('主题验证失败');
            }
            
            // 验证消息
            if (!message || message.value.trim() === '') {
                showError(message, '请输入您的消息');
                isValid = false;
                console.error('消息验证失败');
            }
            
            // 如果验证通过，提交表单
            if (isValid) {
                console.log('表单验证通过，准备提交');
                
                // 禁用提交按钮，防止重复提交
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';
                    
                    // 设置一个短暂的超时，如果网络问题导致表单无法提交，也能恢复按钮状态
                    setTimeout(function() {
                        if (submitButton.disabled) {
                            submitButton.disabled = false;
                            submitButton.innerHTML = '发送留言';
                        }
                    }, 10000); // 10秒后自动恢复
                }
                
                // 记录到百度统计
                if (window._hmt) {
                    window._hmt.push(['_trackEvent', '联系表单', '提交', email.value]);
                }
                
                // 提交表单
                contactForm.submit();
            } else {
                // 验证失败时，滚动到第一个错误字段
                const firstError = contactForm.querySelector('.error');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
}

/**
 * 显示错误消息
 */
function showError(input, message) {
    const formGroup = input.parentElement;
    const errorMessage = document.createElement('div');
    
    errorMessage.className = 'error-message';
    errorMessage.textContent = message;
    
    input.classList.add('error');
    formGroup.appendChild(errorMessage);
}

/**
 * 清除所有错误消息
 */
function clearErrors() {
    const errorMessages = document.querySelectorAll('.error-message');
    const errorInputs = document.querySelectorAll('.error');
    
    errorMessages.forEach(error => error.remove());
    errorInputs.forEach(input => input.classList.remove('error'));
}

/**
 * 验证邮箱格式
 */
function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

/**
 * 初始化统计数字动画
 */
function initCountAnimation() {
    const statNumbers = document.querySelectorAll('.stat-item .number');
    
    if (statNumbers.length > 0) {
        const animateNumbers = function() {
            statNumbers.forEach(number => {
                const rect = number.getBoundingClientRect();
                const windowHeight = window.innerHeight || document.documentElement.clientHeight;
                
                if (rect.top <= windowHeight * 0.8 && !number.classList.contains('animated')) {
                    const target = parseInt(number.getAttribute('data-count'));
                    const duration = 2000; // 动画持续时间（毫秒）
                    const start = 0;
                    const increment = target / (duration / 16);
                    
                    number.classList.add('animated');
                    
                    let current = start;
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            number.textContent = target;
                            clearInterval(timer);
                        } else {
                            number.textContent = Math.floor(current);
                        }
                    }, 16);
                }
            });
        };
        
        // 首次检查
        animateNumbers();
        
        // 滚动时检查
        window.addEventListener('scroll', throttle(animateNumbers, 100));
    }
}

/**
 * 初始化滚动到顶部按钮
 */
function initScrollToTop() {
    const scrollTopBtn = document.querySelector('.scroll-top');
    
    if (scrollTopBtn) {
        // 显示/隐藏按钮
        window.addEventListener('scroll', function() {
            if (window.scrollY > 500) {
                scrollTopBtn.classList.add('visible');
            } else {
                scrollTopBtn.classList.remove('visible');
            }
        });
        
        // 点击滚动到顶部
        scrollTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * 初始化平滑滚动
 */
function initSmoothScroll() {
    const scrollLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // 获取目标位置
                const headerHeight = document.querySelector('.main-header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight;
                
                // 平滑滚动
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * 初始化页面加载器
 */
function initPageLoader() {
    const body = document.body;
    
    // 添加页面加载器
    const loader = document.createElement('div');
    loader.className = 'page-loader';
    loader.innerHTML = '<div class="loader-spinner"></div>';
    body.appendChild(loader);
    
    // 添加加载器样式
    const style = document.createElement('style');
    style.textContent = `
        .page-loader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.5s ease, visibility 0.5s ease;
        }
        .loader-spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(74, 108, 250, 0.3);
            border-radius: 50%;
            border-top-color: var(--primary-color);
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    // 页面加载完成后淡出加载器
    window.addEventListener('load', function() {
        setTimeout(() => {
            loader.style.opacity = '0';
            loader.style.visibility = 'hidden';
            
            // 加载完成后移除加载器
            setTimeout(() => {
                loader.remove();
            }, 500);
        }, 500);
    });
}

/**
 * 初始化微信二维码弹窗
 */
function initWechatModal() {
    const wechatLink = document.getElementById('wechat-link');
    const footerWechatLink = document.getElementById('footer-wechat-link');
    const wechatModal = document.getElementById('wechat-modal');
    const closeModal = document.querySelector('.close-modal');
    
    if (wechatModal) {
        // 点击顶部微信图标显示弹窗
        if (wechatLink) {
            wechatLink.addEventListener('click', function(e) {
                e.preventDefault();
                wechatModal.style.display = 'block';
                document.body.style.overflow = 'hidden'; // 防止背景滚动
            });
        }
        
        // 点击页脚微信图标显示弹窗
        if (footerWechatLink) {
            footerWechatLink.addEventListener('click', function(e) {
                e.preventDefault();
                wechatModal.style.display = 'block';
                document.body.style.overflow = 'hidden'; // 防止背景滚动
            });
        }
        
        // 点击关闭按钮关闭弹窗
        if (closeModal) {
            closeModal.addEventListener('click', function() {
                wechatModal.style.display = 'none';
                document.body.style.overflow = '';
            });
        }
        
        // 点击弹窗外区域关闭弹窗
        window.addEventListener('click', function(e) {
            if (e.target === wechatModal) {
                wechatModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
    }
}

/**
 * 滚动到指定的服务卡片
 * @param {string} serviceName 服务名称
 */
function scrollToService(serviceName) {
    // 防止默认链接行为
    event.preventDefault();
    
    // 获取所有服务卡片
    const serviceItems = document.querySelectorAll('.service-item');
    
    // 查找匹配的服务卡片
    for (let i = 0; i < serviceItems.length; i++) {
        const serviceTitle = serviceItems[i].querySelector('h3').textContent;
        
        if (serviceTitle === serviceName) {
            // 计算目标位置
            const servicesSection = document.getElementById('services');
            const headerHeight = document.querySelector('.main-header').offsetHeight;
            const serviceItemPosition = serviceItems[i].offsetTop + servicesSection.offsetTop - headerHeight - 20;
            
            // 平滑滚动到目标位置
            window.scrollTo({
                top: serviceItemPosition,
                behavior: 'smooth'
            });
            
            // 添加高亮效果
            serviceItems[i].style.transition = 'all 0.5s ease';
            serviceItems[i].style.boxShadow = '0 10px 30px rgba(74, 108, 250, 0.3)';
            
            // 延时移除高亮效果
            setTimeout(() => {
                serviceItems[i].style.boxShadow = '';
            }, 2000);
            
            break;
        }
    }
}

/**
 * 重置所有表单状态，确保从感谢页面返回后表单状态正常
 */
function resetAllForms() {
    const contactForms = document.querySelectorAll('.contact-form form');
    
    contactForms.forEach(form => {
        // 重置表单提交状态，确保从感谢页面返回后按钮正常显示
        form.removeAttribute('data-submitting');
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton && submitButton.disabled) {
            submitButton.disabled = false;
            submitButton.innerHTML = '发送留言';
            console.log('重置提交按钮状态');
        }
    });
}

/**
 * 重置表单提交按钮状态
 * @param {HTMLFormElement} form - 要重置的表单
 */
function resetSubmitButton(form) {
    if (!form) return;
    
    form.removeAttribute('data-submitting');
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = form.classList.contains('subscribe-form') ? 
            '<i class="fas fa-paper-plane"></i>' : 
            '发送留言';
    }
}

// 监听页面可见性变化，处理从历史返回的情况
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // 页面变为可见时，重置所有表单状态
        resetAllForms();
    }
});

// 处理页面从历史记录返回的情况
window.addEventListener('pageshow', function(event) {
    // 如果是从缓存加载的页面（如浏览器后退按钮）
    if (event.persisted) {
        console.log('页面从缓存加载，重置所有表单状态');
        resetAllForms();
    }
}); 
