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
        // 添加提交状态属性，防止重复提交
        form.setAttribute('data-submitting', 'false');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // 检查表单是否已在提交中
            if (form.getAttribute('data-submitting') === 'true') {
                console.log('订阅表单正在提交中，请勿重复点击');
                return;
            }
            
            // 设置表单状态为提交中
            form.setAttribute('data-submitting', 'true');
            
            const email = form.querySelector('input[name="email"]').value;
            const messageDiv = form.querySelector('.subscribe-message');
            const submitButton = form.querySelector('button[type="submit"]');
            
            // 禁用提交按钮
            if (submitButton) {
                submitButton.disabled = true;
                const originalButtonHTML = submitButton.innerHTML;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            }
            
            // 验证邮箱格式
            if (!isValidEmail(email)) {
                showSubscribeMessage(messageDiv, '请输入有效的邮箱地址', false);
                resetFormState(form, submitButton);
                return;
            }

            // 检查是否已订阅
            const subscribers = JSON.parse(localStorage.getItem('subscribers') || '[]');
            if (subscribers.includes(email)) {
                showSubscribeMessage(messageDiv, '该邮箱已经订阅过了', false);
                resetFormState(form, submitButton);
                return;
            }

            try {
                const formData = new FormData(form);
                
                // 添加必要的Formspree字段
                formData.append('_autoresponse', '感谢您的订阅！我们会定期发送最新资讯给您。');
                
                // 添加replyto字段
                formData.append('_replyto', email);
                
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Accept': 'application/json'
                    }
                });

                let result;
                try {
                    result = await response.json();
                } catch (error) {
                    console.error('解析响应失败:', error);
                }

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
                    // 显示Formspree返回的错误信息
                    let errorMessage = '提交失败，请稍后重试';
                    if (result && result.error) {
                        errorMessage = `提交失败: ${result.error}`;
                        console.error('Formspree错误:', result);
                    }
                    showSubscribeMessage(messageDiv, errorMessage, false);
                    
                    // 记录错误到统计
                    if (window._hmt) {
                        window._hmt.push(['_trackEvent', '订阅', '失败', errorMessage]);
                    }
                }
            } catch (error) {
                console.error('订阅出错:', error);
                showSubscribeMessage(messageDiv, '订阅失败，请稍后重试', false);
                
                // 记录错误到统计
                if (window._hmt) {
                    window._hmt.push(['_trackEvent', '订阅', '失败', error.message]);
                }
            } finally {
                // 恢复表单状态
                resetFormState(form, submitButton);
            }
        });
    });
    
    // 重置表单状态
    function resetFormState(form, submitButton) {
        if (!form) return;
        
        // 延迟重置状态，避免快速重复点击
        setTimeout(() => {
            form.setAttribute('data-submitting', 'false');
            
            if (submitButton) {
                submitButton.disabled = false;
                // 恢复原始按钮内容
                if (submitButton.innerHTML.includes('fa-spinner')) {
                    submitButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
                }
            }
        }, 1000);
    }
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
