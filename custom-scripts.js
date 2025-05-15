/**
 * 增强微信二维码弹窗功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 微信二维码弹窗优化
    const wechatLink = document.getElementById('wechat-link');
    const footerWechatLink = document.getElementById('footer-wechat-link');
    const wechatModal = document.getElementById('wechat-modal');
    const closeModal = document.querySelector('.close-modal');
    
    if (wechatModal && wechatLink) {
        // 优化点击微信图标显示弹窗
        wechatLink.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            wechatModal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // 防止背景滚动
        });
        
        // 点击页脚微信图标显示弹窗
        if (footerWechatLink) {
            footerWechatLink.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                wechatModal.style.display = 'block';
                document.body.style.overflow = 'hidden'; // 防止背景滚动
            });
        }
        
        // 优化关闭按钮
        if (closeModal) {
            closeModal.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                wechatModal.style.display = 'none';
                document.body.style.overflow = '';
            });
        }
        
        // 点击弹窗外区域关闭弹窗
        window.addEventListener('click', function(e) {
            if (e.target === wechatModal) {
                wechatModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
        
        // 防止点击弹窗内容关闭弹窗
        document.querySelector('.wechat-modal-content').addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
}); 