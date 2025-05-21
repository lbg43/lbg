import os
import random
import datetime
import re
import json
from pathlib import Path

# 配置
ARTICLES_DIR = 'articles'
ARTICLES_CONFIG = 'articles_config.json'
LOG_FILE = 'update_log.txt'

def log_message(message):
    """记录日志"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')
    print(f'[{timestamp}] {message}')

def load_config():
    """加载文章配置"""
    if os.path.exists(ARTICLES_CONFIG):
        with open(ARTICLES_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 默认配置
        default_config = {
            "articles": [
                {"file": "seo-guide.html", "update_frequency": 7, "last_updated": ""},
                {"file": "responsive-design.html", "update_frequency": 5, "last_updated": ""},
                {"file": "ui-ux-design.html", "update_frequency": 10, "last_updated": ""},
                {"file": "website-development.html", "update_frequency": 7, "last_updated": ""},
                {"file": "mobile-app-development.html", "update_frequency": 10, "last_updated": ""},
                {"file": "ecommerce-solutions.html", "update_frequency": 8, "last_updated": ""},
                {"file": "cloud-services.html", "update_frequency": 12, "last_updated": ""},
                {"file": "conversion-rate.html", "update_frequency": 6, "last_updated": ""}
            ]
        }
        with open(ARTICLES_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        return default_config

def save_config(config):
    """保存文章配置"""
    with open(ARTICLES_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def should_update_article(article_config):
    """判断文章是否需要更新"""
    if not article_config.get('last_updated'):
        return True
    
    last_updated = datetime.datetime.strptime(article_config['last_updated'], '%Y-%m-%d')
    days_since_update = (datetime.datetime.now() - last_updated).days
    return days_since_update >= article_config.get('update_frequency', 7)

def update_article_date(article_path):
    """更新文章的发布日期"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新文章日期
    today = datetime.datetime.now().strftime('%Y年%m月%d日')
    new_content = re.sub(
        r'<span class="article-date"><i class="far fa-calendar-alt"></i>\s*\d{4}年\d{1,2}月\d{1,2}日</span>',
        f'<span class="article-date"><i class="far fa-calendar-alt"></i> {today}</span>',
        content
    )
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def add_new_content(article_path):
    """为文章添加新内容"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找文章正文的结尾位置
    body_end = content.find('<h2>结论</h2>')
    if body_end == -1:
        body_end = content.find('<div class="article-footer">')
    
    if body_end == -1:
        log_message(f"无法在文件 {article_path} 中找到合适的插入点")
        return False
    
    # 获取文章标题，用于生成相关内容
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    if not title_match:
        article_title = '文章'
    else:
        article_title = title_match.group(1)
    
    # 随机选择一种更新方式
    update_types = ['add_tip', 'add_section', 'update_statistics']
    update_type = random.choice(update_types)
    
    current_year = datetime.datetime.now().year
    
    if update_type == 'add_tip':
        new_content_block = f'''
                <div class="info-box">
                    <h4>最新提示 ({current_year}年更新)</h4>
                    <p>随着技术和行业标准的不断发展，我们建议您定期检查并更新您的策略。最近的研究表明，持续优化和适应新趋势的企业比竞争对手获得了30%以上的市场份额增长。</p>
                </div>
                
                '''
    elif update_type == 'add_section':
        new_content_block = f'''
                <h3>{current_year}年最新趋势更新</h3>
                <p>随着数字环境的快速发展，最新的行业数据显示了几个值得关注的新兴趋势：</p>
                <ul>
                    <li><strong>人工智能集成</strong>：企业正在将AI工具整合到其{article_title.split(':')[0] if ':' in article_title else article_title}策略中，实现更高效的流程和个性化体验。</li>
                    <li><strong>数据驱动决策</strong>：基于实时数据分析的决策流程正在成为标准做法，帮助企业更准确地预测市场变化。</li>
                    <li><strong>可持续发展实践</strong>：消费者越来越关注企业的环保措施，将其纳入您的业务战略可以增强品牌形象。</li>
                </ul>
                
                '''
    else:  # update_statistics
        new_content_block = f'''
                <h4>{current_year}年最新数据统计</h4>
                <p>根据最新行业报告，我们更新了以下关键统计数据：</p>
                <ul>
                    <li>移动设备访问占总网站流量的{random.randint(65, 80)}%，比去年增长了{random.randint(5, 15)}%</li>
                    <li>用户平均在响应迅速的网站上停留时间增加了{random.randint(25, 40)}%</li>
                    <li>采用现代化{article_title.split(':')[0] if ':' in article_title else article_title}策略的企业报告转化率提高了{random.randint(20, 35)}%</li>
                </ul>
                
                '''
    
    # 插入新内容
    new_content = content[:body_end] + new_content_block + content[body_end:]
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def update_articles():
    """更新需要更新的文章"""
    config = load_config()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    updated_count = 0
    
    for article in config['articles']:
        if should_update_article(article):
            article_path = os.path.join(ARTICLES_DIR, article['file'])
            
            if not os.path.exists(article_path):
                log_message(f"文件不存在: {article_path}")
                continue
            
            # 更新文章
            date_updated = update_article_date(article_path)
            content_updated = add_new_content(article_path)
            
            if date_updated or content_updated:
                article['last_updated'] = today
                updated_count += 1
                log_message(f"已更新文章: {article['file']}")
            else:
                log_message(f"更新失败: {article['file']}")
    
    # 保存更新后的配置
    save_config(config)
    log_message(f"完成更新，共更新 {updated_count} 篇文章")

if __name__ == "__main__":
    try:
        log_message("开始自动更新文章...")
        update_articles()
        log_message("更新完成")
    except Exception as e:
        log_message(f"更新过程中发生错误: {str(e)}") 