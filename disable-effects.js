// 立即执行函数，禁用加载动画和滚动效果
(function() {
    // 禁用页面加载器
    window.initPageLoader = function() {
        console.log('页面加载器已禁用');
    };
    
    // 移除任何可能已经创建的加载器
    const existingLoader = document.querySelector('.page-loader');
    if (existingLoader) {
        existingLoader.remove();
    }
    
    // 恢复body滚动
    document.body.style.overflow = '';
    
    // 立即显示所有元素，不需要滚动触发
    function showAllElements() {
        const scrollItems = document.querySelectorAll('.service-item, .about-content, .article-card, .gallery-item, .contact-method, .article-body p, .article-body h2, .article-body h3, .article-body ul, .article-body ol, .article-body li, .article-image, .article-header, .article-footer, .related-articles');
        scrollItems.forEach(function(item) {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        });
    }
    
    // 立即执行一次
    showAllElements();
    
    // DOM加载完成后再次执行，确保捕获所有元素
    document.addEventListener('DOMContentLoaded', function() {
        showAllElements();
        
        // 阻止原initScrollEffects函数的滚动监听
        window.initScrollEffects = function() {
            console.log('滚动效果已禁用');
        };
    });
})(); 