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
        const wechatModal = document.getElementById('wechat-modal');
        const closeModal = document.querySelector('.close-modal');
        
        // 定义显示弹窗的函数
        function showWechatModal(e) {
            if (e) e.preventDefault();
            if (wechatModal) {
                wechatModal.style.display = 'flex';
                document.body.style.overflow = 'hidden'; // 防止背景滚动
                console.log('显示微信弹窗 (disable-effects.js)');
            }
        }
        
        // 定义关闭弹窗的函数
        function closeWechatModal() {
            if (wechatModal) {
                wechatModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        }
        
        // 为页面上所有微信相关链接添加点击事件
        // 1. 通过ID查找微信链接
        const wechatLinks = [
            document.getElementById('wechat-link'),
            document.getElementById('footer-wechat-link'),
            document.getElementById('article-wechat-link')
        ].filter(Boolean); // 过滤掉不存在的元素
        
        // 2. 通过类名和标题查找微信链接
        document.querySelectorAll('.social-link[title="分享到微信"], .social-link[title="微信"], .fab.fa-weixin').forEach(function(link) {
            link.addEventListener('click', showWechatModal);
        });
        
        // 3. 为所有微信图标添加事件（不依赖于特定ID或标题）
        document.querySelectorAll('.fab.fa-weixin').forEach(function(icon) {
            // 找到包含此图标的最近的a标签
            const parentLink = icon.closest('a');
            if (parentLink) {
                parentLink.addEventListener('click', showWechatModal);
            }
        });
        
        // 4. 为找到的ID链接添加事件
        wechatLinks.forEach(function(link) {
            link.addEventListener('click', showWechatModal);
        });
        
        // 5. 为文章页面中的社交分享按钮添加事件
        document.querySelectorAll('.share-buttons a').forEach(function(link) {
            if (link.querySelector('.fa-weixin') || link.querySelector('.fab.fa-weixin')) {
                link.addEventListener('click', showWechatModal);
            }
        });
        
        // 为关闭按钮添加点击事件
        if (closeModal) {
            closeModal.addEventListener('click', closeWechatModal);
        }
        
        // 点击弹窗外部关闭弹窗
        window.addEventListener('click', function(e) {
            if (e.target === wechatModal) {
                closeWechatModal();
            }
        });

        console.log('微信弹窗功能已加载完成 (disable-effects.js)');
    });
})(); 
