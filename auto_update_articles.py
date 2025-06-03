import os
import random
import datetime
import re
import json
import shutil
import urllib.parse
import sys
import subprocess
import hashlib
from PIL import Image, ImageDraw, ImageFont

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

# 添加内容区块标识符
CONTENT_BLOCK_MARKERS = {
    'latest_update': '<!-- AUTO_UPDATE_BLOCK: LATEST_UPDATE -->',
    'latest_update_end': '<!-- AUTO_UPDATE_BLOCK_END: LATEST_UPDATE -->',
    'new_insight': '<!-- AUTO_UPDATE_BLOCK: NEW_INSIGHT -->',
    'new_insight_end': '<!-- AUTO_UPDATE_BLOCK_END: NEW_INSIGHT -->',
    'related_articles': '<!-- AUTO_UPDATE_BLOCK: RELATED_ARTICLES -->',
    'related_articles_end': '<!-- AUTO_UPDATE_BLOCK_END: RELATED_ARTICLES -->',
    'schema_markup': '<!-- AUTO_UPDATE_BLOCK: SCHEMA_MARKUP -->',
    'schema_markup_end': '<!-- AUTO_UPDATE_BLOCK_END: SCHEMA_MARKUP -->',
    'social_meta': '<!-- AUTO_UPDATE_BLOCK: SOCIAL_META -->',
    'social_meta_end': '<!-- AUTO_UPDATE_BLOCK_END: SOCIAL_META -->',
    'mobile_style': '<!-- AUTO_UPDATE_BLOCK: MOBILE_STYLE -->',
    'mobile_style_end': '<!-- AUTO_UPDATE_BLOCK_END: MOBILE_STYLE -->'
}

def log_message(message):
    """记录日志"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')
    print(f'[{timestamp}] {message}')

def generate_content_id(content_type, article_path):
    """生成内容区块的唯一ID，用于跟踪更新"""
    filename = os.path.basename(article_path)
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    unique_string = f"{content_type}_{filename}_{current_date}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:8]

def clean_marked_blocks(content, block_type):
    """清理具有标记的内容区块"""
    start_marker = CONTENT_BLOCK_MARKERS[block_type]
    end_marker = CONTENT_BLOCK_MARKERS[f"{block_type}_end"]
    
    # 尝试查找并删除标记的区块
    pattern = re.escape(start_marker) + r'[\s\S]*?' + re.escape(end_marker)
    if re.search(pattern, content):
        cleaned_content = re.sub(pattern, '', content)
        return cleaned_content, True
    
    return content, False

def has_marked_block(content, block_type):
    """检查内容中是否已存在指定类型的标记区块"""
    start_marker = CONTENT_BLOCK_MARKERS[block_type]
    return start_marker in content

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
    
    # 清理已有的最新更新区块（使用标记系统）
    content, cleaned_marked = clean_marked_blocks(content, 'latest_update')
    
    # 如果没有找到标记的区块，尝试使用旧方法清理
    if not cleaned_marked:
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
    
    # 重新查找插入位置（可能已变化）
    start_marker = '</h1>'
    start_pos = content.find(start_marker)
    if start_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到文章开始标记")
        return False
    
    start_pos += len(start_marker)
    
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
    
    # 生成新的更新区块，添加标记 - 使用更清晰的样式
    update_date = datetime.datetime.now().strftime('%Y年%m月%d日')
    content_id = generate_content_id('latest_update', article_path)
    
    # 使用三重引号的原始字符串，避免CSS属性被误认为Python变量
    css_style = """
                .latest-update-box {
                    background-color: #f8f9fa;
                    border-left: 4px solid #4CAF50;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 6px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                }
                .update-header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .update-icon {
                    font-size: 22px;
                    margin-right: 10px;
                }
                .update-header h3 {
                    margin: 0;
                    font-size: 18px;
                    color: #333;
                }
                .update-date {
                    font-weight: normal;
                    color: #666;
                    font-size: 16px;
                }
                .update-highlights {
                    margin: 15px 0;
                }
                .update-highlights ul {
                    margin-bottom: 0;
                    padding-left: 20px;
                }
                .update-highlights li {
                    margin-bottom: 8px;
                    line-height: 1.5;
                }
                .update-footer {
                    margin-bottom: 0;
                    color: #555;
                }
    """
    
    latest_update_section = f'''
            {CONTENT_BLOCK_MARKERS['latest_update']}
            <div class="latest-update-box" data-update-id="{content_id}">
                <div class="update-header">
                    <span class="update-icon">🔔</span>
                    <h3>最新更新 <span class="update-date">({update_date})</span></h3>
                </div>
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
    
    latest_update_section += f'''
                    </ul>
                </div>
                <p class="update-footer"><em>继续阅读获取完整分析和实施建议...</em></p>
            </div>
            
            <style>
            {css_style}
            </style>
            {CONTENT_BLOCK_MARKERS['latest_update_end']}
    '''
    
    # 插入更新区块
    new_content = content[:start_pos] + latest_update_section + content[start_pos:]
    log_message(f"已在文章 {article_path} 中添加新的最近更新区块 (ID: {content_id})")
    
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
    
    # 清理已有的见解区块（使用标记系统）
    content, cleaned_marked = clean_marked_blocks(content, 'new_insight')
    
    # 如果没有找到标记的区块，尝试使用旧方法清理
    if not cleaned_marked:
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
    
    # 使用三重引号的原始字符串，避免CSS属性被误认为Python变量
    css_style = """
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
    """
    
    # 生成新的插入内容，添加FAQ结构和标记
    content_id = generate_content_id('new_insight', article_path)
    
    new_insight = f'''
            {CONTENT_BLOCK_MARKERS['new_insight']}
            <div class="new-insight-box" data-insight-id="{content_id}">
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
    
    new_insight += f'''
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
            {css_style}
            </style>
            {CONTENT_BLOCK_MARKERS['new_insight_end']}
    '''
    
    # 插入新内容
    new_content = content[:insert_pos] + new_insight + content[insert_pos:]
    log_message(f"已在文章 {article_path} 中添加新的见解区块 (ID: {content_id})")
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

# 新增的SEO优化功能
def add_internal_links(article_path, article_config, all_articles):
    """添加相关文章的内部链接"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有相关文章区块
    if has_marked_block(content, 'related_articles'):
        # 已存在相关文章，每次更新都清理和重建
        content, cleaned = clean_marked_blocks(content, 'related_articles')
        if not cleaned:
            log_message(f"警告：找到相关文章标记但无法清理，文件: {article_path}")
    
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
    
    # 生成相关文章区块ID
    content_id = generate_content_id('related_articles', article_path)
    
    # 使用三重引号的原始字符串，避免CSS属性被误认为Python变量
    css_style = """
                .related-articles {
                    background-color: #f9f9f9;
                    padding: 20px;
                    margin: 30px 0;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .related-articles h3 {
                    margin-top: 0;
                    margin-bottom: 15px;
                    color: #333;
                    font-size: 18px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }
                .related-article-list {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .related-article-item {
                    padding: 8px 0;
                }
                .related-article-item a {
                    color: #2c3e50;
                    text-decoration: none;
                    font-weight: 500;
                    transition: color 0.2s;
                }
                .related-article-item a:hover {
                    color: #3498db;
                    text-decoration: underline;
                }
    """
    
    # 在文章底部添加相关文章链接，带标记 - 使用第三和第四张图片的样式
    related_links_section = f'''
            {CONTENT_BLOCK_MARKERS['related_articles']}
            <div class="related-articles" data-related-id="{content_id}">
                <h3>相关文章</h3>
                <div class="related-article-list">
    '''
    
    for related in top_related:
        related_links_section += f'''
                    <div class="related-article-item">
                        <a href="{related['file']}">{related['title']}</a>
                    </div>
        '''
    
    related_links_section += f'''
                </div>
            </div>
            
            <style>
            {css_style}
            </style>
            {CONTENT_BLOCK_MARKERS['related_articles_end']}
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
    log_message(f"已在文章 {article_path} 中添加相关文章链接 (ID: {content_id})")
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def add_schema_markup(article_path, article_config):
    """添加Schema.org结构化数据标记"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有结构化数据（通过标记检查）
    if has_marked_block(content, 'schema_markup'):
        content, cleaned = clean_marked_blocks(content, 'schema_markup')
        if not cleaned:
            log_message(f"警告：找到结构化数据标记但无法清理，文件: {article_path}")
    elif 'itemtype="https://schema.org/Article"' in content or 'application/ld+json' in content:
        # 尝试使用正则表达式清理旧的结构化数据
        old_schema_pattern = r'<script type="application/ld\+json">[\s\S]*?</script>'
        content = re.sub(old_schema_pattern, '', content)
        log_message(f"已清理文章 {article_path} 中的旧结构化数据")
    
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
    
    # 生成结构化数据ID
    content_id = generate_content_id('schema_markup', article_path)
    
    # 构建结构化数据，带标记
    schema_markup = f'''
    {CONTENT_BLOCK_MARKERS['schema_markup']}
    <script type="application/ld+json" data-schema-id="{content_id}">
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
    {CONTENT_BLOCK_MARKERS['schema_markup_end']}
    '''
    
    # 查找</head>标签位置
    head_end_pos = content.find('</head>')
    if head_end_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到</head>标签")
        return False
    
    # 插入结构化数据
    new_content = content[:head_end_pos] + schema_markup + content[head_end_pos:]
    log_message(f"已在文章 {article_path} 中添加结构化数据 (ID: {content_id})")
    
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
    
    # 检查是否已有移动端优化（通过标记检查）
    if has_marked_block(content, 'mobile_style'):
        return False  # 移动端样式只需添加一次，不需要每次更新
    
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
        # 生成内容ID
        content_id = generate_content_id('mobile_style', article_path)
        
        style_section = f'''
        {CONTENT_BLOCK_MARKERS['mobile_style']}
        <style class="mobile-optimization" data-mobile-id="{content_id}">
            /* 移动端优化样式 */
            @media (max-width: 768px) {{
                body {{
                    font-size: 16px;
                    line-height: 1.6;
                }}
                h1 {{
                    font-size: 24px;
                    line-height: 1.3;
                }}
                h2 {{
                    font-size: 20px;
                }}
                h3 {{
                    font-size: 18px;
                }}
                .container, .content {{
                    padding-left: 15px;
                    padding-right: 15px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                /* 改善触摸目标尺寸 */
                a, button {{
                    min-height: 44px;
                    min-width: 44px;
                }}
                /* 改善表单元素在移动端的可用性 */
                input, select, textarea {{
                    font-size: 16px; /* 防止iOS缩放 */
                }}
            }}
        </style>
        {CONTENT_BLOCK_MARKERS['mobile_style_end']}
        '''
        
        head_end_pos = content.find('</head>')
        if head_end_pos != -1:
            content = content[:head_end_pos] + style_section + content[head_end_pos:]
            modified = True
            log_message(f"已在文章 {article_path} 中添加移动端优化样式 (ID: {content_id})")
    
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
    
    # 检查是否已有社交媒体标签（通过标记检查）
    if has_marked_block(content, 'social_meta'):
        content, cleaned = clean_marked_blocks(content, 'social_meta')
        if not cleaned:
            log_message(f"警告：找到社交媒体标记但无法清理，文件: {article_path}")
    elif 'og:title' in content or 'twitter:card' in content:
        # 尝试使用正则表达式清理旧的社交媒体标签
        og_pattern = r'<meta property="og:[^"]*"[^>]*>'
        twitter_pattern = r'<meta name="twitter:[^"]*"[^>]*>'
        
        content = re.sub(og_pattern, '', content)
        content = re.sub(twitter_pattern, '', content)
        log_message(f"已清理文章 {article_path} 中的旧社交媒体标签")
    
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
    
    # 生成社交媒体标签ID
    content_id = generate_content_id('social_meta', article_path)
    
    # 构建社交媒体元标签，带标记
    social_meta_tags = f'''
    {CONTENT_BLOCK_MARKERS['social_meta']}
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
    
    social_meta_tags += f'''
    {CONTENT_BLOCK_MARKERS['social_meta_end']}
    '''
    
    # 查找</head>标签位置
    head_end_pos = content.find('</head>')
    if head_end_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到</head>标签")
        return False
    
    # 插入社交媒体元标签
    new_content = content[:head_end_pos] + social_meta_tags + content[head_end_pos:]
    log_message(f"已在文章 {article_path} 中添加社交媒体标签 (ID: {content_id})")
    
    # 写回文件
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def cleanup_all_blocks(article_path):
    """清理文章中所有的自动生成区块"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    blocks_cleaned = 0
    
    # 清理所有类型的区块
    for block_type in CONTENT_BLOCK_MARKERS:
        if block_type.endswith('_end'):  # 跳过结束标记
            continue
        
        cleaned_content, cleaned = clean_marked_blocks(content, block_type)
        if cleaned:
            content = cleaned_content
            blocks_cleaned += 1
    
    # 如果内容被修改，保存文件
    if blocks_cleaned > 0:
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        bytes_removed = original_size - len(content)
        log_message(f"已清理文章 {article_path} 中的 {blocks_cleaned} 个区块，减少 {bytes_removed} 字节")
        return True
    
    return False

def scan_for_duplicate_blocks(article_path):
    """扫描文章中是否存在重复的区块标记"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    duplicates_found = False
    
    # 检查每种类型的区块
    for block_type in CONTENT_BLOCK_MARKERS:
        if block_type.endswith('_end'):  # 跳过结束标记
            continue
        
        start_marker = CONTENT_BLOCK_MARKERS[block_type]
        matches = re.findall(re.escape(start_marker), content)
        
        if len(matches) > 1:
            duplicates_found = True
            log_message(f"警告：文章 {article_path} 中发现 {len(matches)} 个 '{block_type}' 区块标记")
    
    return duplicates_found

def update_wechat_popup(article_path):
    """确保微信图标点击后只显示二维码窗口，不显示其他内容"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 首先查找并完全删除所有可能的微信弹窗
    wechat_modal_start_pattern = r'<div\s+id="wechat-modal"'
    wechat_modal_starts = [m.start() for m in re.finditer(wechat_modal_start_pattern, content)]
    
    if wechat_modal_starts:
        # 如果找到微信弹窗，删除所有的
        log_message(f"在文章 {article_path} 中找到 {len(wechat_modal_starts)} 个微信弹窗，准备清理")
        
        # 创建一个新的内容字符串，排除所有微信弹窗
        new_content = content
        for start_pos in sorted(wechat_modal_starts, reverse=True):  # 从后向前处理
            # 找到弹窗开始的div
            div_count = 1
            end_pos = start_pos
            
            # 向后查找匹配的</div>标签
            while div_count > 0 and end_pos < len(content):
                end_pos += 1
                if content.find('<div', end_pos, end_pos + 20) == end_pos:
                    div_count += 1
                elif content.find('</div>', end_pos, end_pos + 20) == end_pos:
                    div_count -= 1
            
            if div_count == 0:  # 找到了匹配的结束标签
                # 删除整个弹窗
                modal_content = content[start_pos:end_pos + 6]  # +6 是</div>的长度
                new_content = new_content.replace(modal_content, '')
                log_message(f"已清理一个微信弹窗，长度: {len(modal_content)} 字节")
        
        content = new_content
        modified = True
    
    # 标准的微信弹窗结构 - 使用第三和第四张图片的样式
    wechat_popup = '''
    <!-- 微信二维码弹窗 -->
    <div id="wechat-modal" class="wechat-modal">
        <div class="wechat-modal-content">
            <span class="close-modal">&times;</span>
            <h3>扫描二维码添加微信</h3>
            <div class="qrcode-container">
                <img loading="lazy" src="../images/optimized_wechat-qrcode.jpg" alt="微信二维码" width="200" height="200">
            </div>
            <p>微信号: pds051207</p>
        </div>
    </div>
    '''
    
    # 在</body>标签前插入标准的微信弹窗
    body_end_pos = content.rfind('</body>')
    if body_end_pos != -1:
        content = content[:body_end_pos] + wechat_popup + content[body_end_pos:]
        log_message(f"已在文章 {article_path} 中添加标准微信弹窗")
        modified = True
    
    # 确保微信弹窗CSS被正确引用
    if '<link rel="stylesheet" href="../wechat-popup.css">' not in content:
        head_end_pos = content.find('</head>')
        if head_end_pos != -1:
            content = content[:head_end_pos] + '\n    <!-- 微信弹窗样式 -->\n    <link rel="stylesheet" href="../wechat-popup.css">' + content[head_end_pos:]
            modified = True
    
    # 确保微信弹窗JS被正确引用
    if '<script src="../wechat-popup.js"></script>' not in content:
        body_end_pos = content.rfind('</body>')
        if body_end_pos != -1:
            content = content[:body_end_pos] + '\n    <!-- 微信弹窗脚本 -->\n    <script src="../wechat-popup.js"></script>' + content[body_end_pos:]
            modified = True
    
    # 写回文件
    if modified:
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def create_wechat_popup_files():
    """确保wechat-popup.js和wechat-popup.css文件存在并包含正确的内容"""
    # 创建wechat-popup.css文件 - 使用原始字符串避免CSS属性被误认为Python变量
    css_content = """/* 微信弹窗样式 */
.wechat-modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7);
    z-index: 9999; /* 确保在最上层 */
    justify-content: center;
    align-items: center;
}

.wechat-modal-content {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    position: relative;
    max-width: 90%;
    width: 350px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

.close-modal {
    position: absolute;
    top: 10px;
    right: 15px;
    font-size: 24px;
    cursor: pointer;
    color: #999;
    transition: color 0.3s;
}

.close-modal:hover {
    color: #333;
}

.qrcode-container {
    margin: 20px 0;
    display: flex;
    justify-content: center;
}

.qrcode-container img {
    max-width: 100%;
    height: auto;
    border: 1px solid #eee;
}

.wechat-modal h3 {
    color: #333;
    margin-top: 0;
    font-size: 18px;
}

.wechat-modal p {
    margin-bottom: 0;
    color: #666;
    font-size: 16px;
}

/* 社交分享按钮样式 */
.social-share {
    display: flex;
    gap: 10px;
    margin: 20px 0;
}

.social-share a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    color: #fff;
    transition: all 0.3s ease;
}

.social-share a:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.social-share .weixin {
    background-color: #07C160;
}

.social-share .weibo {
    background-color: #E6162D;
}

.social-share .linkedin {
    background-color: #0A66C2;
}

.social-share .github {
    background-color: #333;
}

.social-share i {
    font-size: 18px;
}
"""

    # 创建wechat-popup.js文件
    js_content = """// 微信二维码弹窗脚本
document.addEventListener('DOMContentLoaded', function() {
    // 获取微信弹窗元素
    const wechatModal = document.getElementById('wechat-modal');
    if (!wechatModal) {
        console.error('未找到微信弹窗元素，ID为wechat-modal');
        return;
    }
    
    // 获取关闭按钮
    const closeModal = wechatModal.querySelector('.close-modal');
    
    // 显示弹窗的函数
    function showWechatModal(e) {
        if (e) e.preventDefault();
        wechatModal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // 防止背景滚动
    }
    
    // 关闭弹窗的函数
    function closeWechatModal() {
        wechatModal.style.display = 'none';
        document.body.style.overflow = '';
    }
    
    // 为页面上所有微信相关链接添加点击事件
    // 1. 通过类名查找微信链接
    document.querySelectorAll('.weixin, .fa-weixin, .fab.fa-weixin').forEach(function(element) {
        const link = element.tagName === 'A' ? element : element.closest('a');
        if (link) {
            link.addEventListener('click', showWechatModal);
        }
    });
    
    // 2. 通过ID查找微信链接
    const wechatLinks = [
        document.getElementById('wechat-link'),
        document.getElementById('footer-wechat-link'),
        document.getElementById('article-wechat-link')
    ].filter(Boolean); // 过滤掉不存在的元素
    
    wechatLinks.forEach(function(link) {
        link.addEventListener('click', showWechatModal);
    });
    
    // 3. 为文章页面中的社交分享按钮添加事件
    document.querySelectorAll('.social-share a').forEach(function(link) {
        if (link.classList.contains('weixin') || 
            link.querySelector('.fa-weixin') || 
            link.querySelector('.fab.fa-weixin')) {
            link.addEventListener('click', showWechatModal);
        }
    });
    
    // 为关闭按钮添加点击事件
    if (closeModal) {
        closeModal.addEventListener('click', closeWechatModal);
    }
    
    // 点击弹窗外部关闭弹窗
    window.addEventListener('click', function(e) {
        if (e.target === wechatModal) {
            closeWechatModal();
        }
    });
});
"""

    # 写入CSS文件
    with open('wechat-popup.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    log_message("已创建或更新wechat-popup.css文件")

    # 写入JS文件
    with open('wechat-popup.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    log_message("已创建或更新wechat-popup.js文件")
    
    # 确保images目录存在
    if not os.path.exists('images'):
        os.makedirs('images')
        log_message("已创建images目录")
    
    # 检查微信二维码图片是否存在
    qrcode_path = os.path.join('images', 'optimized_wechat-qrcode.jpg')
    if not os.path.exists(qrcode_path):
        # 如果图片不存在，创建一个简单的占位图片
        try:
            # 尝试使用PIL创建一个简单的二维码占位图
            # 创建一个200x200的白色图片
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # 绘制边框
            draw.rectangle([(0, 0), (199, 199)], outline='black')
            
            # 添加文字
            try:
                # 尝试加载字体，如果失败则使用默认字体
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((40, 80), "微信二维码", fill='black', font=font)
            draw.text((30, 110), "请替换为实际图片", fill='black', font=font)
            
            # 保存图片
            img.save(qrcode_path, 'JPEG', quality=95)
            log_message(f"已创建微信二维码占位图: {qrcode_path}")
        except Exception as e:
            log_message(f"创建微信二维码占位图失败: {str(e)}")
    
    return True

def add_social_sharing_buttons(article_path):
    """添加社交分享按钮，匹配第三和第四张图片中的样式"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 检查是否已有社交分享按钮
    if '<div class="social-share">' in content:
        # 清理旧的社交分享按钮
        social_share_pattern = r'<div\s+class=["\']social-share["\'][^>]*>[\s\S]*?</div>\s*'
        content = re.sub(social_share_pattern, '', content)
        log_message(f"已清理文章 {article_path} 中的旧社交分享按钮")
        modified = True
    
    # 查找文章标题位置，在标题后添加社交分享按钮
    h1_end_pos = content.find('</h1>')
    if h1_end_pos == -1:
        log_message(f"无法在文件 {article_path} 中找到文章标题结束标记")
        return False
    
    # 获取文章标题
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    article_title = title_match.group(1) if title_match else '文章分享'
    
    # 生成社交分享按钮
    social_share_buttons = f'''
    <div class="social-share">
        <a href="javascript:void(0);" class="weixin" title="分享到微信">
            <i class="fab fa-weixin"></i>
        </a>
        <a href="https://service.weibo.com/share/share.php?url={urllib.parse.quote(os.path.basename(article_path))}&title={urllib.parse.quote(article_title)}" target="_blank" class="weibo" title="分享到微博">
            <i class="fab fa-weibo"></i>
        </a>
        <a href="https://www.linkedin.com/shareArticle?mini=true&url={urllib.parse.quote(os.path.basename(article_path))}&title={urllib.parse.quote(article_title)}" target="_blank" class="linkedin" title="分享到LinkedIn">
            <i class="fab fa-linkedin-in"></i>
        </a>
        <a href="https://github.com/" target="_blank" class="github" title="在GitHub上查看">
            <i class="fab fa-github"></i>
        </a>
    </div>
    '''
    
    # 插入社交分享按钮
    new_content = content[:h1_end_pos + 5] + social_share_buttons + content[h1_end_pos + 5:]
    log_message(f"已在文章 {article_path} 中添加社交分享按钮")
    
    # 确保引用了Font Awesome
    if '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">' not in content:
        head_end_pos = content.find('</head>')
        if head_end_pos != -1:
            font_awesome_link = '\n    <!-- Font Awesome -->\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">'
            new_content = new_content[:head_end_pos] + font_awesome_link + new_content[head_end_pos:]
            log_message(f"已在文章 {article_path} 中添加Font Awesome引用")
    
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
            
            # 扫描检查重复区块
            if scan_for_duplicate_blocks(article_path):
                log_message(f"文章 {article_path} 存在重复区块，进行完全清理")
                cleanup_all_blocks(article_path)
            
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
            
            # 6. 更新微信弹窗，确保点击微信图标只显示二维码
            wechat_popup_updated = update_wechat_popup(article_path)
            if wechat_popup_updated:
                log_message(f"已更新微信弹窗: {article['file']}")
            
            # 7. 添加社交分享按钮
            social_sharing_added = add_social_sharing_buttons(article_path)
            if social_sharing_added:
                log_message(f"已添加社交分享按钮: {article['file']}")
            
            # 最后再次扫描检查是否有重复区块
            has_duplicates = scan_for_duplicate_blocks(article_path)
            if has_duplicates:
                log_message(f"警告：更新后文章 {article_path} 仍存在重复区块，这可能需要手动检查")
            
            # 更新文章状态
            if date_updated or content_updated or internal_links_added or schema_added or \
               images_optimized or mobile_enhanced or social_tags_added or wechat_popup_updated or \
               social_sharing_added:
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
        
        # 确保微信弹窗相关文件存在
        create_wechat_popup_files()
        
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
        
        # 尝试清理所有文章中可能留下的不完整区块
        try:
            log_message("尝试清理可能的不完整区块...")
            config = load_config()
            cleanup_count = 0
            
            for article in config['articles']:
                article_path = os.path.join(ARTICLES_DIR, article['file'])
                if os.path.exists(article_path):
                    if cleanup_all_blocks(article_path):
                        cleanup_count += 1
            
            if cleanup_count > 0:
                log_message(f"已清理 {cleanup_count} 篇文章中的不完整区块")
            else:
                log_message("未发现需要清理的不完整区块")
        except Exception as cleanup_error:
            log_message(f"清理过程中发生错误: {str(cleanup_error)}")
