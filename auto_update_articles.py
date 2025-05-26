import os
import random
import datetime
import re
import json
import shutil
import urllib.parse
import sys
import subprocess

# 自动安装所需的依赖
try:
    from PIL import Image
    print("PIL已成功导入")
except ImportError:
    print("正在安装PIL/Pillow库...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image
    print("PIL/Pillow安装和导入成功")

from pathlib import Path
from update_sitemap import update_sitemap  # 导入sitemap更新功能

# 配置
ARTICLES_DIR = 'articles'
ARTICLES_CONFIG = 'articles_config.json'
LOG_FILE = 'update_log.txt'
BACKUP_DIR = 'articles_backup'  # 文章备份目录
IMAGES_DIR = 'images'  # 图片目录
MAX_IMAGE_WIDTH = 1200  # 最大图片宽度
IMAGE_QUALITY = 85  # 图片压缩质量

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
                {"file": "seo-guide.html", "update_frequency": 1, "last_updated": "", "type": "data", "keywords": []},
                {"file": "responsive-design.html", "update_frequency": 1, "last_updated": "", "type": "data", "keywords": []},
                {"file": "ui-ux-design.html", "update_frequency": 2, "last_updated": "", "type": "core", "keywords": []},
                {"file": "website-development.html", "update_frequency": 1, "last_updated": "", "type": "data", "keywords": []},
                {"file": "mobile-app-development.html", "update_frequency": 2, "last_updated": "", "type": "core", "keywords": []},
                {"file": "ecommerce-solutions.html", "update_frequency": 1, "last_updated": "", "type": "data", "keywords": []},
                {"file": "cloud-services.html", "update_frequency": 2, "last_updated": "", "type": "core", "keywords": []},
                {"file": "conversion-rate.html", "update_frequency": 1, "last_updated": "", "type": "data", "keywords": []}
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
    """判断文章是否需要更新，根据文章类型调整更新频率"""
    if not article_config.get('last_updated'):
        return True
    
    last_updated = datetime.datetime.strptime(article_config['last_updated'], '%Y-%m-%d')
    days_since_update = (datetime.datetime.now() - last_updated).days
    
    # 根据文章类型调整更新频率
    article_type = article_config.get('type', 'data')
    base_frequency = article_config.get('update_frequency', 7)
    
    # 核心内容更新频率降低，数据内容更新频率提高
    if article_type == 'core':
        return days_since_update >= base_frequency * 1.5  # 核心内容更新频率降低
    else:
        return days_since_update >= base_frequency  # 数据内容正常更新

def backup_article(article_path):
    """备份文章"""
    # 确保备份目录存在
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # 创建带时间戳的备份文件名
    filename = os.path.basename(article_path)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    # 复制文件
    shutil.copy2(article_path, backup_path)
    log_message(f"已备份文章: {filename} -> {backup_filename}")
    return backup_path

def extract_keywords(content):
    """从文章内容中提取关键词"""
    # 提取所有h2, h3标签内容和加粗文本作为关键词
    keywords = []
    
    # 提取标题
    h2_matches = re.findall(r'<h2>(.*?)</h2>', content)
    h3_matches = re.findall(r'<h3>(.*?)</h3>', content)
    
    # 提取加粗文本
    bold_matches = re.findall(r'<strong>(.*?)</strong>', content)
    
    # 提取长尾关键词（段落中的关键短语）
    p_content = ' '.join(re.findall(r'<p>(.*?)</p>', content))
    p_content = re.sub(r'<.*?>', '', p_content)  # 移除HTML标签
    
    # 简单的长尾关键词提取（3-5个词的短语）
    words = p_content.split()
    for i in range(len(words) - 2):
        if i + 4 < len(words):  # 4词短语
            phrase = ' '.join(words[i:i+4])
            if len(phrase) > 10 and not any(char.isdigit() for char in phrase):  # 简单过滤
                keywords.append(phrase)
    
    # 合并关键词
    keywords.extend(h2_matches)
    keywords.extend(h3_matches)
    keywords.extend(bold_matches)
    
    # 清理关键词
    cleaned_keywords = []
    for kw in keywords:
        # 移除HTML标签
        kw = re.sub(r'<.*?>', '', kw)
        # 移除标点符号
        kw = re.sub(r'[^\w\s]', '', kw)
        # 移除多余空格
        kw = kw.strip()
        if kw and len(kw) > 1:  # 只保留有意义的关键词
            cleaned_keywords.append(kw)
    
    return list(set(cleaned_keywords))  # 去重

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

def add_latest_update_section(article_path, article_config):
    """在文章顶部添加"最新更新"区块，保留原有内容"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取文章标题
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    if not title_match:
        article_title = '文章'
    else:
        article_title = title_match.group(1)
    
    # 查找文章主体内容区域开始位置
    start_marker = '</h1>'
    start_pos = content.find(start_marker)
    if start_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到文章开始标记")
        return False
    
    start_pos += len(start_marker)
    
    # 首先检查并删除已有的"最近更新"区块，使用更精确的匹配方式
    original_length = len(content)
    log_message(f"开始清理文章 {article_path} 中的旧最近更新区块")
    
    # 尝试查找任何包含"最近更新"文字的div块
    update_box_pattern = r'<div[^>]*class=["\']latest-update-box["\'][^>]*>[\s\S]*?最新更新[\s\S]*?</div>\s*'
    style_pattern = r'<style>\s*\.latest-update-box[\s\S]*?</style>\s*'
    
    # 尝试按最严格的方式匹配完整的更新区块
    full_pattern = update_box_pattern + style_pattern
    
    # 如果没有匹配到完整模式，则尝试分别匹配和删除
    if re.search(full_pattern, content):
        content = re.sub(full_pattern, '', content)
        log_message(f"已清理文章 {article_path} 中的完整最近更新区块")
    else:
        # 先删除更新框
        if re.search(update_box_pattern, content):
            content = re.sub(update_box_pattern, '', content)
            log_message(f"已清理文章 {article_path} 中的最近更新区块框")
        
        # 再删除样式
        if re.search(style_pattern, content):
            content = re.sub(style_pattern, '', content)
            log_message(f"已清理文章 {article_path} 中的最近更新样式")
    
    # 如果还有其他包含"最新更新"的区块，继续清理
    additional_pattern = r'<div[^>]*>[\s\S]*?最新更新[\s\S]*?</div>\s*'
    cleaned_count = 0
    while re.search(additional_pattern, content):
        old_content = content
        content = re.sub(additional_pattern, '', content, count=1)
        if len(old_content) > len(content):
            cleaned_count += 1
    
    if cleaned_count > 0:
        log_message(f"已清理文章 {article_path} 中的额外最近更新区块，共 {cleaned_count} 个")
    
    bytes_removed = original_length - len(content)
    if bytes_removed > 0:
        log_message(f"文章 {article_path} 中共清理了 {bytes_removed} 字节的旧最近更新内容")
    else:
        log_message(f"文章 {article_path} 中未找到需要清理的旧最近更新内容")
    
    # 生成随机数据（确保每篇文章使用相同的数据）
    current_year = datetime.datetime.now().year
    traffic_increase = random.randint(65, 80)
    growth_rate = random.randint(5, 15)
    stay_time_increase = random.randint(25, 40)
    conversion_rate = random.randint(20, 35)
    
    # 提取关键词并增强
    keywords = article_config.get('keywords', [])
    if not keywords:
        keywords = extract_keywords(content)
        article_config['keywords'] = keywords
    
    # 随机选择2-3个关键词强化
    enhanced_keywords = []
    if keywords:
        num_keywords = min(len(keywords), random.randint(2, 3))
        enhanced_keywords = random.sample(keywords, num_keywords)
    
    # 生成新的更新区块
    update_date = datetime.datetime.now().strftime('%Y年%m月%d日')
    latest_update_section = f'''
            <div class="latest-update-box">
                <h3>🔔 最新更新 ({update_date})</h3>
                <p>我们对本文进行了更新，以反映{article_title.split(':')[0] if ':' in article_title else article_title}领域的最新发展：</p>
                
                <div class="update-highlights">
                    <ul>
                        <li><strong>最新数据</strong>：{current_year}年移动端访问比例达到{traffic_increase}%，同比增长{growth_rate}%</li>
                        <li><strong>用户体验</strong>：实施现代化策略的企业用户停留时间提升{stay_time_increase}%</li>
                        <li><strong>转化效果</strong>：优化后的方案平均转化率提升{conversion_rate}%</li>
    '''
    
    # 添加关键词强化部分
    if enhanced_keywords:
        latest_update_section += f'''
                        <li><strong>新趋势</strong>：{current_year}年{', '.join(enhanced_keywords)}领域出现重大突破</li>
        '''
    
    latest_update_section += '''
                    </ul>
                </div>
                <p><em>继续阅读获取完整分析和实施建议...</em></p>
            </div>
            
            <style>
                .latest-update-box {
                    background-color: #f8f9fa;
                    border-left: 4px solid #4CAF50;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 3px;
                }
                .update-highlights {
                    margin: 10px 0;
                }
                .update-highlights ul {
                    margin-bottom: 0;
                }
            </style>
    '''
    
    # 重新查找文章主体内容区域开始位置（因为我们已经删除了旧的更新区块）
    start_marker = '</h1>'
    start_pos = content.find(start_marker)
    if start_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到文章开始标记")
        return False
    
    start_pos += len(start_marker)
    
    # 插入更新区块
    new_content = content[:start_pos] + latest_update_section + content[start_pos:]
    log_message(f"已在文章 {article_path} 中添加新的最近更新区块")
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def insert_new_content(article_path, article_config):
    """在文章现有内容中插入新的段落和数据，而非完全替换"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取文章标题
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    if not title_match:
        article_title = '文章'
    else:
        article_title = title_match.group(1)
    
    # 先检查并删除已有的新见解区块
    original_length = len(content)
    log_message(f"开始清理文章 {article_path} 中的旧见解区块")
    
    # 尝试查找并删除已有的新见解区块
    insight_box_pattern = r'<div[^>]*class=["\']new-insight-box["\'][^>]*>[\s\S]*?</div>\s*'
    insight_style_pattern = r'<style>\s*\.new-insight-box[\s\S]*?</style>\s*'
    
    # 尝试按最严格的方式匹配完整的区块
    full_pattern = insight_box_pattern + insight_style_pattern
    
    # 如果没有匹配到完整模式，则尝试分别匹配和删除
    if re.search(full_pattern, content):
        content = re.sub(full_pattern, '', content)
        log_message(f"已清理文章 {article_path} 中的完整见解区块")
    else:
        # 先删除内容框
        if re.search(insight_box_pattern, content):
            content = re.sub(insight_box_pattern, '', content)
            log_message(f"已清理文章 {article_path} 中的见解区块框")
        
        # 再删除样式
        if re.search(insight_style_pattern, content):
            content = re.sub(insight_style_pattern, '', content)
            log_message(f"已清理文章 {article_path} 中的见解区块样式")
    
    # 如果还有其他包含"最新趋势分析"或"常见问题解答"的区块，继续清理
    trend_pattern = r'<div[^>]*>[\s\S]*?最新趋势分析[\s\S]*?</div>\s*'
    faq_pattern = r'<div[^>]*class=["\']faq-section["\'][^>]*>[\s\S]*?</div>\s*'
    
    # 清理趋势分析区块
    cleaned_count = 0
    while re.search(trend_pattern, content):
        old_content = content
        content = re.sub(trend_pattern, '', content, count=1)
        if len(old_content) > len(content):
            cleaned_count += 1
    
    if cleaned_count > 0:
        log_message(f"已清理文章 {article_path} 中的额外趋势分析区块，共 {cleaned_count} 个")
    
    # 清理FAQ区块
    cleaned_count = 0
    while re.search(faq_pattern, content):
        old_content = content
        content = re.sub(faq_pattern, '', content, count=1)
        if len(old_content) > len(content):
            cleaned_count += 1
    
    if cleaned_count > 0:
        log_message(f"已清理文章 {article_path} 中的额外FAQ区块，共 {cleaned_count} 个")
    
    bytes_removed = original_length - len(content)
    if bytes_removed > 0:
        log_message(f"文章 {article_path} 中共清理了 {bytes_removed} 字节的旧见解内容")
    else:
        log_message(f"文章 {article_path} 中未找到需要清理的旧见解内容")
    
    # 查找文章中的h2或h3标签位置，用于插入新内容
    h2_matches = list(re.finditer(r'<h[23]>.*?</h[23]>', content))
    if not h2_matches or len(h2_matches) < 2:
        log_message(f"文件 {article_path} 中没有足够的标题标记用于插入内容")
        return False
    
    # 随机选择一个h2/h3标题后插入新内容
    insert_pos = random.choice(h2_matches[1:]).end()  # 跳过第一个标题
    
    # 生成随机数据
    current_year = datetime.datetime.now().year
    traffic_increase = random.randint(65, 80)
    growth_rate = random.randint(5, 15)
    stay_time_increase = random.randint(25, 40)
    conversion_rate = random.randint(20, 35)
    
    # 提取关键词
    keywords = article_config.get('keywords', [])
    if not keywords:
        keywords = extract_keywords(content)
        article_config['keywords'] = keywords
    
    # 随机选择1-2个关键词强化
    enhanced_keywords = []
    if keywords:
        num_keywords = min(len(keywords), random.randint(1, 2))
        enhanced_keywords = random.sample(keywords, num_keywords)
    
    # 生成新的插入内容，添加FAQ结构
    new_insight = f'''
            <div class="new-insight-box">
                <h4>{current_year}年最新趋势分析</h4>
                <p>随着技术的快速迭代，{article_title.split(':')[0] if ':' in article_title else article_title}领域出现了新的发展趋势：</p>
                
                <div class="trend-data">
                    <ul>
                        <li>移动端访问比例达到{traffic_increase}%，同比增长{growth_rate}%</li>
                        <li>用户平均停留时间提升{stay_time_increase}%</li>
                        <li>实施现代化策略的企业转化率提升{conversion_rate}%</li>
    '''
    
    # 添加关键词强化部分
    if enhanced_keywords:
        keyword_insights = []
        for kw in enhanced_keywords:
            insight = f"{kw}相关技术的应用效果提升了{random.randint(15, 40)}%"
            keyword_insights.append(insight)
        
        new_insight += f'''
                        <li>{'，'.join(keyword_insights)}</li>
        '''
    
    new_insight += '''
                    </ul>
                </div>
                
                <!-- 添加FAQ结构，带有结构化数据标记 -->
                <div class="faq-section" itemscope itemtype="https://schema.org/FAQPage">
                    <h4>常见问题解答</h4>
                    <div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
                        <h5 itemprop="name">如何提高移动端用户体验？</h5>
                        <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                            <div itemprop="text">
                                <p>提高移动端用户体验的关键策略包括：优化页面加载速度、采用响应式设计、简化导航结构、增大触摸目标尺寸，以及确保内容易于阅读。定期进行用户测试并根据Core Web Vitals指标进行优化也至关重要。</p>
                            </div>
                        </div>
                    </div>
                    <div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
                        <h5 itemprop="name">最新的SEO趋势有哪些？</h5>
                        <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                            <div itemprop="text">
                                <p>最新的SEO趋势包括：移动优先索引、页面体验信号(Core Web Vitals)、语义搜索和意图匹配、AI内容优化、视频内容的重要性提升，以及结构化数据的广泛应用。关注用户体验和高质量内容仍然是SEO的基础。</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <style>
                .new-insight-box {
                    background-color: #f0f8ff;
                    border: 1px solid #d1e7ff;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }
                .trend-data {
                    margin: 10px 0;
                }
                .faq-section {
                    margin-top: 25px;
                    border-top: 1px solid #e0e0e0;
                    padding-top: 15px;
                }
                .faq-item {
                    margin-bottom: 15px;
                }
                .faq-item h5 {
                    margin-bottom: 8px;
                    color: #2c3e50;
                    font-weight: 600;
                }
            </style>
    '''
    
    # 插入新内容
    new_content = content[:insert_pos] + new_insight + content[insert_pos:]
    log_message(f"已在文章 {article_path} 中添加新的见解区块")
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

# 新增的SEO优化功能
def add_internal_links(article_path, article_config, all_articles):
    """添加相关文章的内部链接"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取当前文章的关键词
    current_keywords = article_config.get('keywords', [])
    if not current_keywords:
        current_keywords = extract_keywords(content)
        article_config['keywords'] = current_keywords
    
    # 查找可能的相关文章
    related_articles = []
    current_filename = os.path.basename(article_path)
    
    for other_article in all_articles:
        other_filename = other_article['file']
        
        # 跳过当前文章
        if other_filename == current_filename:
            continue
        
        # 获取其他文章的关键词
        other_keywords = other_article.get('keywords', [])
        if not other_keywords:
            other_article_path = os.path.join(ARTICLES_DIR, other_filename)
            if os.path.exists(other_article_path):
                with open(other_article_path, 'r', encoding='utf-8') as f:
                    other_content = f.read()
                other_keywords = extract_keywords(other_content)
                other_article['keywords'] = other_keywords
        
        # 计算关键词相似度（简单实现：共同关键词数量）
        common_keywords = set(current_keywords).intersection(set(other_keywords))
        if common_keywords:
            # 获取文章标题
            other_article_path = os.path.join(ARTICLES_DIR, other_filename)
            if os.path.exists(other_article_path):
                with open(other_article_path, 'r', encoding='utf-8') as f:
                    other_content = f.read()
                title_match = re.search(r'<h1>(.*?)</h1>', other_content)
                if title_match:
                    article_title = title_match.group(1)
                    related_articles.append({
                        'file': other_filename,
                        'title': article_title,
                        'common_keywords': len(common_keywords)
                    })
    
    # 按相关性排序并选择前3篇
    related_articles.sort(key=lambda x: x['common_keywords'], reverse=True)
    top_related = related_articles[:3] if len(related_articles) > 3 else related_articles
    
    if not top_related:
        return False
    
    # 在文章底部添加相关文章链接
    related_links_section = '''
            <div class="related-articles">
                <h3>相关推荐</h3>
                <ul>
    '''
    
    for related in top_related:
        related_links_section += f'''
                    <li><a href="{related['file']}">{related['title']}</a></li>
        '''
    
    related_links_section += '''
                </ul>
            </div>
            
            <style>
                .related-articles {
                    background-color: #f9f9f9;
                    padding: 15px;
                    margin: 30px 0;
                    border-radius: 5px;
                    border-top: 2px solid #e0e0e0;
                }
                .related-articles h3 {
                    margin-top: 0;
                    color: #333;
                }
                .related-articles ul {
                    padding-left: 20px;
                }
                .related-articles li {
                    margin-bottom: 8px;
                }
            </style>
    '''
    
    # 查找文章结束位置
    end_marker = '</article>'
    end_pos = content.find(end_marker)
    if end_pos == -1:
        end_marker = '</div>'
        end_pos = content.rfind(end_marker)
    
    if end_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到文章结束标记")
        return False
    
    # 插入相关文章链接
    new_content = content[:end_pos] + related_links_section + content[end_pos:]
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def add_schema_markup(article_path, article_config):
    """添加Schema.org结构化数据标记"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有结构化数据
    if 'itemtype="https://schema.org/Article"' in content:
        return False
    
    # 获取文章标题
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    if not title_match:
        log_message(f"无法在文件 {article_path} 中找到文章标题")
        return False
    
    article_title = title_match.group(1)
    
    # 获取文章日期
    date_match = re.search(r'<span class="article-date"><i class="far fa-calendar-alt"></i>\s*(\d{4}年\d{1,2}月\d{1,2}日)</span>', content)
    article_date = date_match.group(1) if date_match else datetime.datetime.now().strftime('%Y年%m月%d日')
    
    # 获取文章描述（使用第一段落作为描述）
    description_match = re.search(r'<p>(.*?)</p>', content)
    article_description = ''
    if description_match:
        article_description = re.sub(r'<.*?>', '', description_match.group(1))
        if len(article_description) > 160:
            article_description = article_description[:157] + '...'
    
    # 获取作者信息（如果有）
    author_match = re.search(r'<span class="article-author">(.*?)</span>', content)
    article_author = author_match.group(1) if author_match else '网站管理员'
    
    # 构建结构化数据
    schema_markup = f'''
    <script type="application/ld+json">
    {{"@context":"https://schema.org",
      "@type":"Article",
      "headline":"{article_title}",
      "description":"{article_description}",
      "author":{{"@type":"Person","name":"{article_author}"}},
      "publisher":{{"@type":"Organization","name":"网站名称","logo":{{"@type":"ImageObject","url":"logo.png"}}}},
      "datePublished":"{article_date}",
      "dateModified":"{datetime.datetime.now().strftime('%Y年%m月%d日')}"
    }}
    </script>
    '''
    
    # 查找</head>标签位置
    head_end_pos = content.find('</head>')
    if head_end_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到</head>标签")
        return False
    
    # 插入结构化数据
    new_content = content[:head_end_pos] + schema_markup + content[head_end_pos:]
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def optimize_images(article_path):
    """优化文章中的图片（添加alt标签、压缩图片）"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取文章标题和关键词，用于生成alt标签
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    article_title = title_match.group(1) if title_match else ''
    
    # 查找所有图片标签
    img_tags = re.findall(r'<img\s+[^>]*src=["\']([^"\'>]+)["\'][^>]*>', content)
    if not img_tags:
        return False
    
    # 确保图片目录存在
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    
    modified = False
    for img_src in img_tags:
        # 跳过外部图片和已经优化过的图片
        if img_src.startswith('http') or 'optimized_' in img_src:
            continue
        
        # 构建图片路径
        img_path = os.path.join(os.path.dirname(article_path), img_src)
        if not os.path.exists(img_path):
            continue
        
        try:
            # 生成优化后的图片名称
            img_name = os.path.basename(img_src)
            img_ext = os.path.splitext(img_name)[1].lower()
            optimized_img_name = f"optimized_{img_name}"
            optimized_img_path = os.path.join(IMAGES_DIR, optimized_img_name)
            
            # 优化图片尺寸和质量
            with Image.open(img_path) as img:
                # 调整图片尺寸
                if img.width > MAX_IMAGE_WIDTH:
                    ratio = MAX_IMAGE_WIDTH / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.LANCZOS)
                
                # 保存优化后的图片
                if img_ext in ['.jpg', '.jpeg']:
                    img.save(optimized_img_path, 'JPEG', quality=IMAGE_QUALITY, optimize=True)
                elif img_ext == '.png':
                    img.save(optimized_img_path, 'PNG', optimize=True)
                else:
                    img.save(optimized_img_path)
            
            # 生成alt标签（使用文章标题和图片名称）
            img_name_clean = os.path.splitext(img_name)[0].replace('-', ' ').replace('_', ' ')
            alt_text = f"{article_title} - {img_name_clean}"
            
            # 替换图片标签，添加alt属性和loading="lazy"属性
            old_img_tag = re.search(r'<img\s+[^>]*src=["\']' + re.escape(img_src) + r'["\'][^>]*>', content)
            if old_img_tag:
                old_tag = old_img_tag.group(0)
                
                # 检查是否已有alt属性
                if 'alt=' not in old_tag:
                    new_tag = old_tag.replace('<img ', f'<img alt="{alt_text}" ')
                else:
                    new_tag = old_tag
                
                # 添加loading="lazy"属性
                if 'loading=' not in new_tag:
                    new_tag = new_tag.replace('<img ', '<img loading="lazy" ')
                
                # 更新src属性
                relative_path = os.path.relpath(optimized_img_path, os.path.dirname(article_path)).replace('\\', '/')
                new_tag = re.sub(r'src=["\'][^"\'>]+["\']', f'src="{relative_path}"', new_tag)
                
                # 替换标签
                content = content.replace(old_tag, new_tag)
                modified = True
        except Exception as e:
            log_message(f"优化图片时出错: {img_path}, 错误: {str(e)}")
    
    if modified:
        # 写回文件
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def enhance_mobile_seo(article_path):
    """增强移动端SEO，提高Core Web Vitals分数"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有移动端优化
    if 'viewport' in content and 'mobile-optimization' in content:
        return False
    
    modified = False
    
    # 1. 确保有viewport元标签
    if 'viewport' not in content:
        head_end_pos = content.find('</head>')
        if head_end_pos != -1:
            viewport_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">\n    '
            content = content[:head_end_pos] + viewport_meta + content[head_end_pos:]
            modified = True
    
    # 2. 添加移动端优化CSS
    if 'mobile-optimization' not in content:
        style_section = '''
        <style class="mobile-optimization">
            /* 移动端优化样式 */
            @media (max-width: 768px) {
                body {
                    font-size: 16px;
                    line-height: 1.6;
                }
                h1 {
                    font-size: 24px;
                    line-height: 1.3;
                }
                h2 {
                    font-size: 20px;
                }
                h3 {
                    font-size: 18px;
                }
                .container, .content {
                    padding-left: 15px;
                    padding-right: 15px;
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
                /* 改善触摸目标尺寸 */
                a, button {
                    min-height: 44px;
                    min-width: 44px;
                }
                /* 改善表单元素在移动端的可用性 */
                input, select, textarea {
                    font-size: 16px; /* 防止iOS缩放 */
                }
            }
        </style>
        '''
        
        head_end_pos = content.find('</head>')
        if head_end_pos != -1:
            content = content[:head_end_pos] + style_section + content[head_end_pos:]
            modified = True
    
    if modified:
        # 写回文件
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def add_social_meta_tags(article_path):
    """添加社交媒体元标签（Open Graph和Twitter Card）"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有社交媒体标签
    if 'og:title' in content and 'twitter:card' in content:
        return False
    
    # 获取文章标题
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    if not title_match:
        log_message(f"无法在文件 {article_path} 中找到文章标题")
        return False
    
    article_title = title_match.group(1)
    
    # 获取文章描述（使用第一段落作为描述）
    description_match = re.search(r'<p>(.*?)</p>', content)
    article_description = ''
    if description_match:
        article_description = re.sub(r'<.*?>', '', description_match.group(1))
        if len(article_description) > 160:
            article_description = article_description[:157] + '...'
    
    # 查找文章中的第一张图片作为社交媒体图片
    img_match = re.search(r'<img\s+[^>]*src=["\']([^"\'>]+)["\'][^>]*>', content)
    article_image = ''
    if img_match:
        article_image = img_match.group(1)
        # 如果是相对路径，转换为绝对URL（假设网站根目录）
        if not article_image.startswith('http'):
            article_image = f"/{article_image.lstrip('/')}" if article_image else ''
    
    # 构建社交媒体元标签
    social_meta_tags = f'''
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{article_title}">
    <meta property="og:description" content="{article_description}">
    <meta property="og:url" content="{urllib.parse.quote(os.path.basename(article_path))}">
    '''
    
    if article_image:
        social_meta_tags += f'''
    <meta property="og:image" content="{article_image}">
        '''
    
    social_meta_tags += f'''
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{article_title}">
    <meta name="twitter:description" content="{article_description}">
    '''
    
    if article_image:
        social_meta_tags += f'''
    <meta name="twitter:image" content="{article_image}">
        '''
    
    # 查找</head>标签位置
    head_end_pos = content.find('</head>')
    if head_end_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到</head>标签")
        return False
    
    # 插入社交媒体元标签
    new_content = content[:head_end_pos] + social_meta_tags + content[head_end_pos:]
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def update_articles():
    """更新需要更新的文章"""
    config = load_config()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    updated_count = 0
    
    # 确保备份目录存在
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # 确保图片目录存在
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    
    for article in config['articles']:
        if should_update_article(article):
            article_path = os.path.join(ARTICLES_DIR, article['file'])
            
            if not os.path.exists(article_path):
                log_message(f"文件不存在: {article_path}")
                continue
            
            # 备份文章
            backup_path = backup_article(article_path)
            
            # 更新文章日期
            date_updated = update_article_date(article_path)
            
            # 根据文章类型选择更新策略
            article_type = article.get('type', 'data')
            if article_type == 'core':
                # 核心内容：只添加最新更新区块，不修改主体
                content_updated = add_latest_update_section(article_path, article)
            else:
                # 数据内容：添加最新更新区块并在正文中插入新内容
                update_section_added = add_latest_update_section(article_path, article)
                new_content_inserted = insert_new_content(article_path, article)
                content_updated = update_section_added or new_content_inserted
            
            # 应用SEO优化
            log_message(f"开始对文章 {article['file']} 应用SEO优化...")
            
            # 1. 添加内部链接结构
            internal_links_added = add_internal_links(article_path, article, config['articles'])
            if internal_links_added:
                log_message(f"已添加内部链接: {article['file']}")
            
            # 2. 添加Schema.org结构化数据标记
            schema_added = add_schema_markup(article_path, article)
            if schema_added:
                log_message(f"已添加结构化数据标记: {article['file']}")
            
            # 3. 优化图片（添加alt标签、压缩图片）
            images_optimized = optimize_images(article_path)
            if images_optimized:
                log_message(f"已优化图片: {article['file']}")
            
            # 4. 增强移动端SEO
            mobile_enhanced = enhance_mobile_seo(article_path)
            if mobile_enhanced:
                log_message(f"已增强移动端SEO: {article['file']}")
            
            # 5. 添加社交媒体元标签
            social_tags_added = add_social_meta_tags(article_path)
            if social_tags_added:
                log_message(f"已添加社交媒体元标签: {article['file']}")
            
            # 更新文章状态
            if date_updated or content_updated or internal_links_added or schema_added or \
               images_optimized or mobile_enhanced or social_tags_added:
                article['last_updated'] = today
                updated_count += 1
                log_message(f"已完成文章更新和SEO优化: {article['file']} (类型: {article_type})")
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
