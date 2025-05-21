import os
import re

def update_css_link_in_file(file_path):
    """在HTML文件中添加update_content.css链接"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有update_content.css链接
    if '../update_content.css' in content:
        print(f"{file_path} 已包含update_content.css链接")
        return False
    
    # 查找微信弹窗CSS链接行
    wechat_css_pattern = r'<link rel="stylesheet" href="../wechat-popup.css">'
    
    # 如果找到了微信弹窗CSS链接，在其后添加update_content.css链接
    if re.search(wechat_css_pattern, content):
        new_content = re.sub(
            wechat_css_pattern,
            '<link rel="stylesheet" href="../wechat-popup.css">\n    <!-- 自动更新内容样式 -->\n    <link rel="stylesheet" href="../update_content.css">',
            content
        )
    else:
        # 如果没有找到微信弹窗CSS链接，在</head>标签前添加
        new_content = re.sub(
            r'</head>',
            '    <!-- 自动更新内容样式 -->\n    <link rel="stylesheet" href="../update_content.css">\n</head>',
            content
        )
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"已更新 {file_path}")
    return True

def main():
    """更新所有文章中的CSS链接"""
    articles_dir = 'articles'
    updated_count = 0
    
    # 遍历articles目录下的所有HTML文件
    for file_name in os.listdir(articles_dir):
        if file_name.endswith('.html'):
            file_path = os.path.join(articles_dir, file_name)
            if update_css_link_in_file(file_path):
                updated_count += 1
    
    print(f"完成！共更新了 {updated_count} 个文件")

if __name__ == "__main__":
    main() 