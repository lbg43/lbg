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
    // 1. 通过类名查找微信链接
    document.querySelectorAll('.weixin, .fa-weixin, .fab.fa-weixin').forEach(function(element) {
        const link = element.tagName === 'A' ? element : element.closest('a');
        if (link) {
            link.addEventListener('click', showWechatModal);
        }
    });
    
    // 2. 通过ID查找微信链接
    const wechatLinks = [
        document.getElementById('wechat-link'),
        document.getElementById('footer-wechat-link'),
        document.getElementById('article-wechat-link')
    ].filter(Boolean); // 过滤掉不存在的元素
    
    wechatLinks.forEach(function(link) {
        link.addEventListener('click', showWechatModal);
    });
    
    // 3. 为文章页面中的社交分享按钮添加事件
    document.querySelectorAll('.social-share a').forEach(function(link) {
        if (link.classList.contains('weixin') || 
            link.querySelector('.fa-weixin') || 
            link.querySelector('.fab.fa-weixin')) {
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
