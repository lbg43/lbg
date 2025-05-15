/**
 * 增强微信二维码弹窗功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 微信二维码弹窗优化
    const wechatLink = document.getElementById('wechat-link');
    const footerWechatLink = document.getElementById('footer-wechat-link');
    const wechatModal = document.getElementById('wechat-modal');
    const closeModal = document.querySelector('.close-modal');
    
    function showWechatModal(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        if (wechatModal) {
            wechatModal.style.display = 'flex'; // 使用flex布局
            document.body.style.overflow = 'hidden'; // 防止背景滚动
        }
    }
    
    function hideWechatModal(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        if (wechatModal) {
            wechatModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
    
    if (wechatLink) {
        // 优化点击微信图标显示弹窗
        wechatLink.addEventListener('click', showWechatModal);
    }
    
    // 点击页脚微信图标显示弹窗
    if (footerWechatLink) {
        footerWechatLink.addEventListener('click', showWechatModal);
    }
    
    // 优化关闭按钮
    if (closeModal) {
        closeModal.addEventListener('click', hideWechatModal);
    }
    
    // 点击弹窗外区域关闭弹窗
    if (wechatModal) {
        wechatModal.addEventListener('click', function(e) {
            if (e.target === wechatModal) {
                hideWechatModal();
            }
        });
        
        // 防止点击弹窗内容关闭弹窗
        const modalContent = wechatModal.querySelector('.wechat-modal-content');
        if (modalContent) {
            modalContent.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    }
    
    // 确保微信图标在所有其他模块中也能工作
    document.querySelectorAll('[id^="wechat-link"]').forEach(function(link) {
        if (link !== wechatLink && link !== footerWechatLink) {
            link.addEventListener('click', showWechatModal);
        }
    });
}); 
