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
        
        // 微信二维码弹窗功能
        // 获取所有微信链接元素
        const wechatLink = document.getElementById('wechat-link');
        const footerWechatLink = document.getElementById('footer-wechat-link');
        const articleWechatLink = document.getElementById('article-wechat-link');
        const wechatModal = document.getElementById('wechat-modal');
        const closeModal = document.querySelector('.close-modal');
        
        // 为所有微信链接添加点击事件
        if (wechatLink && wechatModal) {
            wechatLink.addEventListener('click', function(e) {
                e.preventDefault();
                wechatModal.style.display = 'flex';
                document.body.style.overflow = 'hidden'; // 防止背景滚动
            });
        }
        
        if (footerWechatLink && wechatModal) {
            footerWechatLink.addEventListener('click', function(e) {
                e.preventDefault();
                wechatModal.style.display = 'flex';
                document.body.style.overflow = 'hidden'; // 防止背景滚动
            });
        }
        
        if (articleWechatLink && wechatModal) {
            articleWechatLink.addEventListener('click', function(e) {
                e.preventDefault();
                wechatModal.style.display = 'flex';
                document.body.style.overflow = 'hidden'; // 防止背景滚动
            });
        }
        
        // 为关闭按钮添加点击事件
        if (closeModal && wechatModal) {
            closeModal.addEventListener('click', function() {
                wechatModal.style.display = 'none';
                document.body.style.overflow = '';
            });
        }
        
        // 点击弹窗外部关闭弹窗
        window.addEventListener('click', function(e) {
            if (e.target === wechatModal) {
                wechatModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        });

        // 检查页面上是否有微信分享按钮，并为其添加事件处理
        const shareWechatButtons = document.querySelectorAll('.share-buttons .social-link[title="分享到微信"]');
        shareWechatButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                if (wechatModal) {
                    wechatModal.style.display = 'flex';
                    document.body.style.overflow = 'hidden';
                }
            });
        });
    });
})(); 
