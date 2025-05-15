// 轮播图专用功能
document.addEventListener('DOMContentLoaded', function() {
    // 获取轮播图元素
    const carousel = document.querySelector('.carousel');
    if (!carousel) {
        console.log('未找到轮播图元素');
        return;
    }
    
    // 添加特定类名以匹配CSS
    carousel.classList.add('hero-carousel');
    
    // 获取轮播图项目
    const items = carousel.querySelectorAll('.carousel-item');
    if (!items.length) {
        console.log('轮播图中没有项目');
        return;
    }
    
    // 添加调试信息
    console.log('轮播图初始化 - 找到', items.length, '个项目');
    
    // 获取轮播图按钮
    const prevBtn = carousel.querySelector('.carousel-prev');
    const nextBtn = carousel.querySelector('.carousel-next');
    
    // 清理掉旧的导航点容器
    const oldDotsContainer = carousel.querySelector('.carousel-dots');
    if (oldDotsContainer) {
        oldDotsContainer.remove();
        console.log('移除了导航点容器');
    }
    
    // 当前项目索引
    let currentIndex = 0;
    let autoPlayTimer = null;
    
    // 初始化轮播图
    function initCarousel() {
        // 显示第一个项目
        showSlide(0);
        
        // 绑定按钮事件
        bindEvents();
        
        // 开始自动播放
        startAutoPlay();
    }
    
    // 绑定按钮和触摸事件
    function bindEvents() {
        // 上一张按钮
        if (prevBtn) {
            prevBtn.addEventListener('click', function(e) {
                e.preventDefault();
                prevSlide();
            });
        }
        
        // 下一张按钮
        if (nextBtn) {
            nextBtn.addEventListener('click', function(e) {
                e.preventDefault();
                nextSlide();
            });
        }
        
        // 键盘事件
        document.addEventListener('keydown', function(e) {
            if (!carousel.matches(':hover')) return;
            
            if (e.key === 'ArrowLeft') {
                prevSlide();
            } else if (e.key === 'ArrowRight') {
                nextSlide();
            }
        });
        
        // 触摸事件
        let touchStartX = 0;
        let touchEndX = 0;
        
        carousel.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
            // 暂停自动播放
            pauseAutoPlay();
        }, { passive: true });
        
        carousel.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            const diff = touchEndX - touchStartX;
            
            if (Math.abs(diff) > 50) {
                if (diff > 0) {
                    prevSlide(); // 右滑，上一张
                } else {
                    nextSlide(); // 左滑，下一张
                }
            }
            
            // 恢复自动播放
            startAutoPlay();
        }, { passive: true });
        
        // 鼠标悬停时暂停自动播放
        carousel.addEventListener('mouseenter', pauseAutoPlay);
        carousel.addEventListener('mouseleave', startAutoPlay);
        
        // 页面可见性变化
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'visible') {
                startAutoPlay();
            } else {
                pauseAutoPlay();
            }
        });
    }
    
    // 显示指定幻灯片
    function showSlide(index) {
        // 处理边界情况
        if (index < 0) {
            index = items.length - 1;
        } else if (index >= items.length) {
            index = 0;
        }
        
        // 更新当前索引
        currentIndex = index;
        
        // 隐藏所有幻灯片
        items.forEach(item => {
            item.classList.remove('active');
        });
        
        // 显示当前幻灯片
        items[currentIndex].classList.add('active');
        
        // 调试输出
        console.log('切换到幻灯片:', currentIndex);
    }
    
    // 上一张幻灯片
    function prevSlide() {
        pauseAutoPlay();
        showSlide(currentIndex - 1);
        startAutoPlay();
    }
    
    // 下一张幻灯片
    function nextSlide() {
        pauseAutoPlay();
        showSlide(currentIndex + 1);
        startAutoPlay();
    }
    
    // 开始自动播放
    function startAutoPlay() {
        pauseAutoPlay();
        autoPlayTimer = setInterval(nextSlide, 5000);
    }
    
    // 暂停自动播放
    function pauseAutoPlay() {
        if (autoPlayTimer) {
            clearInterval(autoPlayTimer);
            autoPlayTimer = null;
        }
    }
    
    // 初始化轮播图
    initCarousel();
}); 
