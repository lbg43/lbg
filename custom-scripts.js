/**
 * 微信二维码弹窗功能
 * 只有点击微信图标才会显示二维码
 * (已由script.min.js实现，此处代码暂时注释掉以避免冲突)
 */
/*
document.addEventListener('DOMContentLoaded', function() {
    // 获取微信按钮和弹窗元素
    const wechatLink = document.getElementById('wechat-link');
    const footerWechatLink = document.getElementById('footer-wechat-link');
    const wechatModal = document.getElementById('wechat-modal');
    const closeModal = document.querySelector('.close-modal');
    
    // 确保弹窗初始状态为隐藏
    if (wechatModal) {
        wechatModal.style.display = 'none';
    }
    
    // 显示二维码弹窗
    function showWechatModal(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        if (wechatModal) {
            wechatModal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // 防止背景滚动
        }
    }
    
    // 隐藏二维码弹窗
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
    
    // 点击微信图标显示弹窗
    if (wechatLink) {
        wechatLink.addEventListener('click', showWechatModal);
    }
    
    // 点击页脚微信图标显示弹窗
    if (footerWechatLink) {
        footerWechatLink.addEventListener('click', showWechatModal);
    }
    
    // 点击关闭按钮隐藏弹窗
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
        
        // 防止点击弹窗内容导致弹窗关闭
        const modalContent = wechatModal.querySelector('.wechat-modal-content');
        if (modalContent) {
            modalContent.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    }
});
*/ 
