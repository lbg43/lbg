import os
import urllib.request
import ssl
from PIL import Image, ImageDraw, ImageFont

# 创建images目录（如果不存在）
if not os.path.exists('images'):
    os.makedirs('images')

# 禁用SSL证书验证（仅用于演示目的）
ssl._create_default_https_context = ssl._create_unverified_context

# 图片URL列表（使用免费图片网站的示例图片）
image_urls = {
    # 其他图片（使用Unsplash的免费图片）
    "hero-image.jpg": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&q=80",
    "about-image.jpg": "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    
    # 文章图片
    "article1.jpg": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    "article2.jpg": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    "article3.jpg": "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    
    # 作品集图片
    "gallery1.jpg": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    "gallery2.jpg": "https://images.unsplash.com/photo-1551650975-87deedd944c3?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    "gallery3.jpg": "https://images.unsplash.com/photo-1482062364825-616fd23b8fc1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    "gallery4.jpg": "https://images.unsplash.com/photo-1547119957-637f8679db1e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    "gallery5.jpg": "https://images.unsplash.com/photo-1559028012-481c04fa702d?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    "gallery6.jpg": "https://images.unsplash.com/photo-1481887328591-3e277f9473dc?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
}

# 创建Logo图片
def create_logo(filename, bg_color, text_color):
    try:
        print(f"正在创建 {filename}...")
        # 创建一个新的图像，带有指定的背景色
        img = Image.new('RGB', (150, 50), color=bg_color)
        d = ImageDraw.Draw(img)
        
        # 使用简单的文本作为logo
        # 注意：这会使用系统默认字体，如果需要特定字体，需要指定字体文件路径
        try:
            # 尝试加载一个常见的字体
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            # 如果找不到字体，使用默认字体
            font = ImageFont.load_default()
        
        # 添加文字
        text = "COMPANY"
        # PIL 8.0.0及以上版本使用textlength，旧版本使用textsize
        try:
            text_width = d.textlength(text, font=font)
            text_position = ((150 - text_width) / 2, 15)
        except AttributeError:
            text_width, text_height = d.textsize(text, font=font)
            text_position = ((150 - text_width) / 2, (50 - text_height) / 2)
        
        d.text(text_position, text, fill=text_color, font=font)
        
        # 保存图像
        filepath = os.path.join('images', filename)
        img.save(filepath)
        print(f"已创建并保存到 {filepath}")
        return True
    except Exception as e:
        print(f"创建 {filename} 时出错: {e}")
        return False

# 创建favicon图标
def create_favicon():
    try:
        print("正在创建 favicon.ico...")
        # 创建一个32x32的正方形图像
        img = Image.new('RGB', (32, 32), color="#4a6cf7")
        d = ImageDraw.Draw(img)
        
        # 使用简单的文本作为图标
        try:
            # 尝试加载一个常见的字体
            font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            # 如果找不到字体，使用默认字体
            font = ImageFont.load_default()
        
        # 添加文字（只使用首字母C）
        text = "C"
        try:
            text_width = d.textlength(text, font=font)
            text_position = ((32 - text_width) / 2, 8)
        except AttributeError:
            text_width, text_height = d.textsize(text, font=font)
            text_position = ((32 - text_width) / 2, (32 - text_height) / 2)
        
        d.text(text_position, text, fill="#ffffff", font=font)
        
        # 保存为ICO格式
        img.save("favicon.ico", format="ICO")
        print("已创建并保存 favicon.ico")
        return True
    except Exception as e:
        print(f"创建 favicon.ico 时出错: {e}")
        return False

# 创建Logo
create_logo("logo.png", "#4a6cf7", "#ffffff")
create_logo("logo-white.png", "#ffffff", "#4a6cf7")

# 创建favicon
create_favicon()

# 下载所有图片
for filename, url in image_urls.items():
    try:
        print(f"正在下载 {filename}...")
        filepath = os.path.join('images', filename)
        urllib.request.urlretrieve(url, filepath)
        print(f"已保存到 {filepath}")
    except Exception as e:
        print(f"下载 {filename} 时出错: {e}")

print("\n所有图片下载完成！")
