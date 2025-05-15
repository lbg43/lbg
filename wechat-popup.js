// 微信二维码弹窗脚本
// 由于微信弹窗功能已经整合到disable-effects.js中
// 这个文件仅作为兼容用途，确保所有页面都能正常显示微信弹窗
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
    
    // 获取所有微信链接
    const wechatLinks = [
        document.getElementById('wechat-link'),
        document.getElementById('footer-wechat-link'),
        document.getElementById('article-wechat-link')
    ].filter(Boolean); // 过滤掉不存在的元素
    
    // 为所有微信链接添加点击事件
    wechatLinks.forEach(function(link) {
        link.addEventListener('click', showWechatModal);
    });
    
    // 获取所有带有"分享到微信"标题的链接
    const shareWechatLinks = document.querySelectorAll('.social-link[title="分享到微信"], .social-link[title="微信"]');
    shareWechatLinks.forEach(function(link) {
        link.addEventListener('click', showWechatModal);
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
    
    console.log('微信弹窗功能已加载（来自wechat-popup.js）');
});
