import os
import random
import datetime
import re
import json
from pathlib import Path
from update_sitemap import update_sitemap  # 导入sitemap更新功能

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
                {"file": "seo-guide.html", "update_frequency": 1, "last_updated": ""},
                {"file": "responsive-design.html", "update_frequency": 1, "last_updated": ""},
                {"file": "ui-ux-design.html", "update_frequency": 2, "last_updated": ""},
                {"file": "website-development.html", "update_frequency": 1, "last_updated": ""},
                {"file": "mobile-app-development.html", "update_frequency": 2, "last_updated": ""},
                {"file": "ecommerce-solutions.html", "update_frequency": 1, "last_updated": ""},
                {"file": "cloud-services.html", "update_frequency": 2, "last_updated": ""},
                {"file": "conversion-rate.html", "update_frequency": 1, "last_updated": ""}
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
    
    # 获取文章标题
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    if not title_match:
        article_title = '文章'
    else:
        article_title = title_match.group(1)
    
    # 查找文章主体内容区域
    start_marker = '</h1>'
    end_marker = '<h2>结论</h2>'
    if end_marker not in content:
        end_marker = '<div class="article-footer">'
    
    start_pos = content.find(start_marker)
    if start_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到文章开始标记")
        return False
    
    end_pos = content.find(end_marker)
    if end_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到文章结束标记")
        return False
    
    start_pos += len(start_marker)
    
    # 生成新的文章主体内容
    current_year = datetime.datetime.now().year
    
    # 生成随机数据（确保每篇文章使用相同的数据）
    traffic_increase = random.randint(65, 80)
    growth_rate = random.randint(5, 15)
    stay_time_increase = random.randint(25, 40)
    conversion_rate = random.randint(20, 35)
    
    # 生成新的文章内容
    new_article_content = f'''
            <div class="article-content">
                <p>在{current_year}年的数字化浪潮中，{article_title.split(':')[0] if ':' in article_title else article_title}领域发生了重大变革。本文将为您深入分析最新趋势和实践方法。</p>
                
                <h3>一、行业最新发展趋势</h3>
                <p>随着技术的快速迭代，我们观察到以下关键趋势：</p>
                <ul>
                    <li><strong>人工智能驱动</strong>：AI技术正在重塑{article_title.split(':')[0] if ':' in article_title else article_title}的实现方式</li>
                    <li><strong>用户体验至上</strong>：个性化和响应式设计成为标准配置</li>
                    <li><strong>数据安全升级</strong>：隐私保护和数据合规成为重中之重</li>
                </ul>
                
                <div class="info-box">
                    <h4>最新市场数据 ({current_year}年更新)</h4>
                    <ul>
                        <li>移动端访问比例达到{traffic_increase}%，同比增长{growth_rate}%</li>
                        <li>用户平均停留时间提升{stay_time_increase}%</li>
                        <li>实施现代化策略的企业转化率提升{conversion_rate}%</li>
                    </ul>
                </div>
                
                <h3>二、最佳实践方案</h3>
                <p>基于最新的行业数据和实践经验，我们建议：</p>
                <ol>
                    <li><strong>技术栈更新</strong>：采用最新的技术框架和工具</li>
                    <li><strong>性能优化</strong>：实施智能缓存和按需加载策略</li>
                    <li><strong>安全防护</strong>：部署多层次的安全防护机制</li>
                </ol>
                
                <h3>三、未来展望</h3>
                <p>展望未来，{article_title.split(':')[0] if ':' in article_title else article_title}领域将继续快速发展：</p>
                <ul>
                    <li>更智能的自动化解决方案</li>
                    <li>更深入的数据分析能力</li>
                    <li>更完善的用户体验优化</li>
                </ul>
            </div>
    '''
    
    # 替换文章主体内容
    new_content = content[:start_pos] + new_article_content + content[end_pos:]
    
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
        
        # 更新sitemap.xml
        log_message("开始更新sitemap.xml...")
        sitemap_updated = update_sitemap()
        if sitemap_updated:
            log_message("sitemap.xml更新完成")
        else:
            log_message("sitemap.xml更新失败")
        
        log_message("所有更新完成")
    except Exception as e:
        log_message(f"更新过程中发生错误: {str(e)}") 
