/**
 * 邮件订阅功能处理脚本
 * 用于处理用户在页脚的订阅表单提交
 * 使用Formspree服务，适用于GitHub Pages和Cloudflare Pages静态部署
 */

document.addEventListener('DOMContentLoaded', function() {
    // 查找所有订阅表单
    const forms = document.querySelectorAll('.subscribe-form');
    console.log(`Found ${forms.length} subscription forms`);

    forms.forEach(form => {
        // 重置表单状态，确保从感谢页面返回时按钮正常显示
        resetSubscribeFormState(form);

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = form.querySelector('input[name="email"]').value;
            const messageDiv = form.querySelector('.subscribe-message');
            
            // 验证邮箱格式
            if (!isValidEmail(email)) {
                showSubscribeMessage(messageDiv, '请输入有效的邮箱地址', false);
                return;
            }

            // 检查是否已订阅
            const subscribers = JSON.parse(localStorage.getItem('subscribers') || '[]');
            if (subscribers.includes(email)) {
                showSubscribeMessage(messageDiv, '该邮箱已经订阅过了', false);
                return;
            }

            try {
                const formData = new FormData(form);
                formData.append('_autoresponse', '感谢您的订阅！我们会定期发送最新资讯给您。');
                
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Accept': 'application/json'
                    }
                });

                if (response.ok) {
                    // 保存订阅者信息
                    subscribers.push(email);
                    localStorage.setItem('subscribers', JSON.stringify(subscribers));
                    
                    // 记录订阅时间
                    const subscriptionTime = new Date().toISOString();
                    localStorage.setItem(`subscription_time_${email}`, subscriptionTime);
                    
                    // 发送成功消息
                    showSubscribeMessage(messageDiv, '订阅成功！感谢您的关注', true);
                    
                    // 清空表单
                    form.reset();
                    
                    // 发送通知邮件到管理员邮箱
                    const adminEmail = '1508611232@qq.com';
                    const notificationData = new FormData();
                    notificationData.append('_to', adminEmail);
                    notificationData.append('_subject', '新订阅通知');
                    notificationData.append('message', `新用户订阅：${email}\n订阅时间：${subscriptionTime}`);
                    
                    await fetch(form.action, {
                        method: 'POST',
                        body: notificationData,
                        headers: {
                            'Accept': 'application/json'
                        }
                    });
                    
                    // 记录到百度统计
                    if (window._hmt) {
                        window._hmt.push(['_trackEvent', '订阅', '成功', email]);
                    }
                    
                    // 记录到Google Analytics
                    if (window.gtag) {
                        gtag('event', 'subscribe', {
                            'event_category': 'engagement',
                            'event_label': email
                        });
                    }
                    
                } else {
                    throw new Error('提交失败');
                }
            } catch (error) {
                console.error('订阅出错:', error);
                showSubscribeMessage(messageDiv, '订阅失败，请稍后重试', false);
                
                // 记录错误到统计
                if (window._hmt) {
                    window._hmt.push(['_trackEvent', '订阅', '失败', error.message]);
                }
            }
        });
    });
});

// 验证邮箱格式
function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email.toLowerCase());
}

// 显示订阅消息
function showSubscribeMessage(element, message, isSuccess) {
    if (!element) return;
    
    element.textContent = message;
    element.className = 'subscribe-message ' + (isSuccess ? 'success' : 'error');
    element.style.display = 'block';
    
    // 3秒后自动隐藏消息
    setTimeout(() => {
        element.style.display = 'none';
    }, 3000);
}

// 监听页面可见性变化和历史返回事件
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // 页面变为可见时重置表单状态
        const forms = document.querySelectorAll('.subscribe-form');
        forms.forEach(form => {
            resetSubscribeFormState(form);
        });
    }
});

// 页面加载时也重置表单状态
window.addEventListener('pageshow', function(event) {
    // 如果是从缓存加载的页面，也需要重置表单
    if (event.persisted) {
        const forms = document.querySelectorAll('.subscribe-form');
        forms.forEach(form => {
            resetSubscribeFormState(form);
        });
    }
});

/**
 * 重置订阅表单状态
 * @param {HTMLFormElement} form - 要重置的表单
 */
function resetSubscribeFormState(form) {
    form.removeAttribute('data-submitting');
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
    }
} 
