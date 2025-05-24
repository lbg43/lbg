import os
import datetime
import re
import logging
import sys
import subprocess

# 自动安装所需的依赖（如果需要的话）
def ensure_dependencies():
    """确保所有依赖都已安装"""
    required_packages = []  # 目前这个脚本没有特殊依赖，但可以根据需要添加
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"{package}已成功导入")
        except ImportError:
            print(f"正在安装{package}库...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package}安装成功")

# 确保依赖已安装
ensure_dependencies()

# 配置
SITEMAP_FILE = 'sitemap.xml'
LOG_FILE = 'update_log.txt'

def log_message(message):
    """记录日志"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')
    print(f'[{timestamp}] {message}')

def update_sitemap():
    """更新sitemap.xml中的lastmod日期"""
    if not os.path.exists(SITEMAP_FILE):
        log_message(f"文件不存在: {SITEMAP_FILE}")
        return False
    
    try:
        with open(SITEMAP_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 获取当前日期
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # 更新所有lastmod标签
        updated_content = re.sub(
            r'<lastmod>\d{4}-\d{2}-\d{2}</lastmod>',
            f'<lastmod>{today}</lastmod>',
            content
        )
        
        # 写回文件
        with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        log_message(f"已成功更新sitemap.xml中的lastmod日期为 {today}")
        return True
    
    except Exception as e:
        log_message(f"更新sitemap.xml时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        log_message("开始更新sitemap.xml...")
        update_sitemap()
        log_message("sitemap.xml更新完成")
    except Exception as e:
        log_message(f"更新过程中发生错误: {str(e)}") 
