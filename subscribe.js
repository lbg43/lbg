/**
 * 邮件订阅功能处理脚本
 * 用于处理用户在页脚的订阅表单提交
 * 使用Formspree服务，适用于GitHub Pages和Cloudflare Pages静态部署
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取所有订阅表单
    const subscribeForms = document.querySelectorAll('.subscribe-form');
    console.log('找到订阅表单数量:', subscribeForms.length);
    
    // 为每个订阅表单添加提交事件监听
    subscribeForms.forEach((form, index) => {
        // 确保表单有action属性，如果没有则添加Formspree URL
        if (!form.getAttribute('action')) {
            // 已替换为您的Formspree表单URL
            form.setAttribute('action', 'https://formspree.io/f/xldjqywr');
            form.setAttribute('method', 'POST');
            console.log(`表单${index+1}设置action属性:`, form.getAttribute('action'));
        }
        
        // 添加提交事件处理
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            console.log(`表单${index+1}提交触发`);
            
            // 获取邮箱输入
            const emailInput = form.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            console.log('提交的邮箱:', email);
            
            // 简单的邮箱格式验证
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(email)) {
                showSubscribeMessage(form, '请输入有效的邮箱地址', false);
                console.error('邮箱格式验证失败');
                return;
            }
            
            // 显示加载状态
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '处理中...';
            
            try {
                // 创建标准的表单数据对象
                const formData = new FormData();
                formData.append('email', email);
                formData.append('subscribeTime', new Date().toLocaleString());
                formData.append('_subject', '新网站订阅通知');
                
                // 添加管理员抄送
                const adminEmail = '1508611232@qq.com'; // 网站管理员邮箱
                formData.append('_cc', adminEmail);
                console.log('设置管理员抄送:', adminEmail);
                
                // 添加更详细的内容给管理员
                const message = `
网站有新的订阅者！

订阅者邮箱: ${email}
订阅时间: ${new Date().toLocaleString()}
订阅页面: ${window.location.href}
用户设备: ${navigator.userAgent}
                `;
                formData.append('message', message);
                
                console.log('准备发送表单数据到:', form.getAttribute('action'));
                
                // 尝试使用fetch API代替XMLHttpRequest
                try {
                    const response = await fetch(form.getAttribute('action'), {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'Accept': 'application/json'
                        }
                    });
                    
                    console.log('Formspree响应状态:', response.status);
                    const responseData = await response.json();
                    console.log('Formspree响应数据:', responseData);
                    
                    // 恢复按钮状态
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalButtonText;
                    
                    if (response.ok) {
                        showSubscribeMessage(form, '订阅成功，感谢您的关注！', true);
                        // 如果成功，清空输入框
                        emailInput.value = '';
                        // 记录订阅成功日志
                        console.log('新订阅成功: ' + email + ' - ' + new Date().toLocaleString());
                    } else {
                        console.error('Formspree返回错误:', responseData);
                        showSubscribeMessage(form, '订阅请求失败，请稍后重试', false);
                    }
                } catch (fetchError) {
                    console.error('Fetch请求失败:', fetchError);
                    
                    // 如果fetch失败，回退到XMLHttpRequest
                    console.log('尝试使用XMLHttpRequest作为备选方案');
                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', form.getAttribute('action'));
                    xhr.setRequestHeader('Accept', 'application/json');
                    
                    xhr.onload = function() {
                        console.log('XMLHttpRequest响应状态:', xhr.status);
                        // 恢复按钮状态
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalButtonText;
                        
                        if (xhr.status === 200) {
                            try {
                                const response = JSON.parse(xhr.responseText);
                                console.log('XMLHttpRequest响应数据:', response);
                                if (response.ok) {
                                    showSubscribeMessage(form, '订阅成功，感谢您的关注！', true);
                                    // 如果成功，清空输入框
                                    emailInput.value = '';
                                    // 记录订阅成功日志
                                    console.log('新订阅成功(XHR): ' + email + ' - ' + new Date().toLocaleString());
                                } else {
                                    console.error('XMLHttpRequest返回错误:', response);
                                    showSubscribeMessage(form, '订阅请求失败，请稍后重试', false);
                                }
                            } catch (parseError) {
                                console.error('解析XMLHttpRequest响应失败:', parseError, xhr.responseText);
                                showSubscribeMessage(form, '订阅处理出错，请联系管理员', false);
                            }
                        } else {
                            console.error('XMLHttpRequest请求失败，状态码:', xhr.status);
                            showSubscribeMessage(form, '订阅请求失败，请稍后重试', false);
                        }
                    };
                    
                    xhr.onerror = function(error) {
                        console.error('XMLHttpRequest发生错误:', error);
                        // 恢复按钮状态
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalButtonText;
                        showSubscribeMessage(form, '订阅请求失败，请稍后重试', false);
                    };
                    
                    xhr.send(formData);
                }
            } catch (error) {
                console.error('订阅过程中发生异常:', error);
                // 恢复按钮状态
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                
                // 显示错误消息
                showSubscribeMessage(form, '订阅请求失败，请稍后重试', false);
            }
        });
    });
    
    // 辅助函数：显示订阅消息
    function showSubscribeMessage(form, message, isSuccess) {
        console.log(`显示消息: ${message}, 成功状态: ${isSuccess}`);
        // 创建或获取消息元素
        let messageElement = form.querySelector('.subscribe-message');
        
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.className = 'subscribe-message';
            form.appendChild(messageElement);
            console.log('创建新的消息元素');
        }
        
        // 设置消息样式和内容
        messageElement.textContent = message;
        messageElement.className = 'subscribe-message ' + (isSuccess ? 'success' : 'error');
        messageElement.style.display = 'block';
        messageElement.style.opacity = '1';
        
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
