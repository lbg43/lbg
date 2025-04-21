/**
 * 邮件订阅功能处理脚本
 * 用于处理用户在页脚的订阅表单提交
 * 使用Formspree服务，适用于GitHub Pages和Cloudflare Pages静态部署
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取所有订阅表单
    const subscribeForms = document.querySelectorAll('.subscribe-form');
    
    // 为每个订阅表单添加提交事件监听
    subscribeForms.forEach(form => {
        // 确保表单有action属性，如果没有则添加Formspree URL
        if (!form.getAttribute('action')) {
            // 已替换为您的Formspree表单URL
            form.setAttribute('action', 'https://formspree.io/f/xldjqywr');
            form.setAttribute('method', 'POST');
        }
        
        // 添加提交事件处理
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // 获取邮箱输入
            const emailInput = form.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            
            // 简单的邮箱格式验证
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(email)) {
                showSubscribeMessage(form, '请输入有效的邮箱地址', false);
                return;
            }
            
            // 显示加载状态
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '处理中...';
            
            // 创建FormData对象
            const formData = new FormData(form);
            
            // 添加订阅时间
            formData.append('subscribeTime', new Date().toLocaleString());
            
            // 添加管理员通知邮箱 - 自动接收通知
            formData.append('_cc', '1508611232@qq.com');
            
            // 发送AJAX请求到Formspree
            fetch(form.getAttribute('action'), {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                // 恢复按钮状态
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                
                // 显示结果消息
                if (data.ok) {
                    showSubscribeMessage(form, '订阅成功，感谢您的关注！', true);
                    // 如果成功，清空输入框
                    emailInput.value = '';
                } else {
                    showSubscribeMessage(form, '订阅请求失败，请稍后重试', false);
                }
            })
            .catch(error => {
                // 恢复按钮状态
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                
                // 显示错误消息
                showSubscribeMessage(form, '订阅请求失败，请稍后重试', false);
                console.error('订阅请求错误:', error);
            });
        });
    });
    
    // 辅助函数：显示订阅消息
    function showSubscribeMessage(form, message, isSuccess) {
        // 创建或获取消息元素
        let messageElement = form.querySelector('.subscribe-message');
        
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.className = 'subscribe-message';
            form.appendChild(messageElement);
        }
        
        // 设置消息样式和内容
        messageElement.textContent = message;
        messageElement.className = 'subscribe-message ' + (isSuccess ? 'success' : 'error');
        
        // 3秒后自动隐藏消息
        setTimeout(() => {
            messageElement.style.opacity = '0';
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.textContent = '';
                    messageElement.className = 'subscribe-message';
                    messageElement.style.opacity = '';
                }
            }, 300);
        }, 3000);
    }
}); 
