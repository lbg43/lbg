// 微信二维码弹窗脚本
document.addEventListener('DOMContentLoaded', function() {
    // 获取微信弹窗元素
    const wechatModal = document.getElementById('wechat-modal');
    if (!wechatModal) {
        console.error('未找到微信弹窗元素，ID为wechat-modal');
        return;
    }
    
    // 获取关闭按钮
    const closeModal = wechatModal.querySelector('.close-modal');
    
    // 显示弹窗的函数
    function showWechatModal(e) {
        if (e) e.preventDefault();
        wechatModal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // 防止背景滚动
    }
    
    // 关闭弹窗的函数
    function closeWechatModal() {
        wechatModal.style.display = 'none';
        document.body.style.overflow = '';
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
});
