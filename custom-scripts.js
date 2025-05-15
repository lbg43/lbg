/**
 * 增强微信二维码弹窗功能
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('初始化微信二维码弹窗功能');
    
    // 获取微信按钮和弹窗元素
    const wechatLink = document.getElementById('wechat-link');
    const footerWechatLink = document.getElementById('footer-wechat-link');
    const wechatModal = document.getElementById('wechat-modal');
    const closeModal = document.querySelector('.close-modal');
    
    // 确保弹窗初始状态为隐藏
    if (wechatModal) {
        wechatModal.style.display = 'none';
    }
    
    function showWechatModal(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        if (wechatModal) {
            console.log('显示微信二维码弹窗');
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
            console.log('隐藏微信二维码弹窗');
            wechatModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
    
    // 绑定点击事件
    if (wechatLink) {
        console.log('绑定微信图标点击事件');
        wechatLink.addEventListener('click', showWechatModal);
    }
    
    if (footerWechatLink) {
        console.log('绑定页脚微信图标点击事件');
        footerWechatLink.addEventListener('click', showWechatModal);
    }
    
    if (closeModal) {
        closeModal.addEventListener('click', hideWechatModal);
    }
    
    if (wechatModal) {
        wechatModal.addEventListener('click', function(e) {
            if (e.target === wechatModal) {
                hideWechatModal();
            }
        });
        
        const modalContent = wechatModal.querySelector('.wechat-modal-content');
        if (modalContent) {
            modalContent.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    }
    
    // 确保所有微信图标都能触发弹窗
    document.querySelectorAll('[id^="wechat-link"]').forEach(function(link) {
        if (link !== wechatLink && link !== footerWechatLink) {
            link.addEventListener('click', showWechatModal);
        }
    });
}); 
