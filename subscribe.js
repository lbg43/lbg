/**
 * 邮件订阅功能处理脚本
 * 用于处理用户在页脚的订阅表单提交
 * 使用Formspree服务，适用于GitHub Pages和Cloudflare Pages静态部署
 */

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-subscribe="true"]');
    console.log(`找到 ${forms.length} 个订阅表单`);

    forms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailInput = form.querySelector('input[type="email"]');
            const email = emailInput.value;
            
            if (!validateEmail(email)) {
                showSubscribeMessage(form, '请输入有效的邮箱地址', 'error');
                return;
            }

            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = '提交中...';
            submitButton.disabled = true;

            try {
                // 发送订阅请求
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'Accept': 'application/json'
                    }
                });

                if (response.ok) {
                    // 发送管理员通知
                    await sendNotification(email);
                    // 发送用户确认邮件
                    await sendConfirmation(email);
                    
                    showSubscribeMessage(form, '订阅成功！确认邮件已发送到您的邮箱', 'success');
                    saveSubscriber(email);
                    form.reset();
                } else {
                    throw new Error('订阅请求失败');
                }
            } catch (error) {
                console.error('订阅错误:', error);
                showSubscribeMessage(form, '订阅失败，请稍后重试', 'error');
            } finally {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    });
});

// 发送管理员通知
async function sendNotification(email) {
    const adminEmail = "1508611232@qq.com"; // 管理员邮箱
    const formData = new FormData();
    formData.append("_replyto", email);
    formData.append("_subject", "新订阅通知");
    formData.append("_cc", adminEmail);
    formData.append("message", `新用户 ${email} 已订阅您的网站更新`);
    
    try {
        const response = await fetch("https://formspree.io/f/xldjqywr", {
            method: "POST",
            body: formData,
            headers: {
                Accept: "application/json"
            }
        });
        console.log('管理员通知发送成功');
    } catch (error) {
        console.error('管理员通知发送失败:', error);
    }
}

// 发送订阅确认邮件
async function sendConfirmation(email) {
    const formData = new FormData();
    formData.append("_replyto", email);
    formData.append("_subject", "订阅确认");
    formData.append("message", `感谢您订阅我们的更新！`);
    
    try {
        const response = await fetch("https://formspree.io/f/xldjqywr", {
            method: "POST",
            body: formData,
            headers: {
                Accept: "application/json"
            }
        });
        console.log('确认邮件发送成功');
    } catch (error) {
        console.error('确认邮件发送失败:', error);
    }
}

// 验证邮箱格式
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// 显示订阅消息
function showSubscribeMessage(form, message, type) {
    let messageDiv = form.querySelector('.subscribe-message');
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.className = 'subscribe-message';
        form.appendChild(messageDiv);
    }

    messageDiv.textContent = message;
    messageDiv.className = `subscribe-message ${type}`;
    messageDiv.style.opacity = '1';

    setTimeout(() => {
        messageDiv.style.opacity = '0';
    }, 5000);
}

// 保存订阅者信息到本地存储
function saveSubscriber(email) {
    try {
        let subscribers = JSON.parse(localStorage.getItem('subscribers')) || [];
        if (!subscribers.includes(email)) {
            subscribers.push({
                email: email,
                date: new Date().toISOString()
            });
            localStorage.setItem('subscribers', JSON.stringify(subscribers));
            console.log('订阅者信息已保存');
        }
    } catch (error) {
        console.error('保存订阅者信息失败:', error);
    }
} 
