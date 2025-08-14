#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统环境检查脚本
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python版本符合要求")
        return True
    else:
        print("❌ Python版本过低，需要3.8+")
        return False

def check_chrome_installation():
    """检查Chrome安装"""
    print("\n检查Chrome浏览器安装...")
    
    # Mac常见Chrome路径
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser"
    ]
    
    for path in chrome_paths:
        if Path(path).exists():
            print(f"✅ 找到Chrome: {path}")
            return path
    
    # 尝试通过命令查找
    try:
        result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
        if result.returncode == 0:
            chrome_path = result.stdout.strip()
            print(f"✅ 找到Chrome: {chrome_path}")
            return chrome_path
    except:
        pass
    
    print("❌ 未找到Chrome浏览器")
    print("请安装Chrome浏览器: https://www.google.com/chrome/")
    return None

def check_selenium():
    """检查Selenium安装"""
    print("\n检查Selenium安装...")
    try:
        import selenium
        print(f"✅ Selenium版本: {selenium.__version__}")
        return True
    except ImportError:
        print("❌ Selenium未安装")
        return False

def test_webdriver():
    """测试WebDriver"""
    print("\n测试WebDriver...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 尝试不使用WebDriverManager
        print("尝试使用系统Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ WebDriver测试成功，页面标题: {title}")
        return True
        
    except Exception as e:
        print(f"❌ WebDriver测试失败: {e}")
        return False

def create_simple_demo():
    """创建简化版演示"""
    print("\n创建简化版演示...")
    
    demo_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版DeepSeek客户端演示
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def simple_demo():
    """简化版演示"""
    print("=== 简化版DeepSeek演示 ===")
    
    # Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 使用新版headless模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")
    
    driver = None
    try:
        print("正在启动Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("正在访问DeepSeek...")
        driver.get("https://chat.deepseek.com")
        
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        
        # 截图保存
        driver.save_screenshot("deepseek_page.png")
        print("页面截图已保存: deepseek_page.png")
        
        print("✅ 简化版演示成功！")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭")

if __name__ == "__main__":
    simple_demo()
'''
    
    with open("simple_demo.py", "w", encoding="utf-8") as f:
        f.write(demo_content)
    print("✅ 简化版演示已创建: simple_demo.py")

def main():
    """主函数"""
    print("=== DeepSeek客户端环境检查 ===")
    
    # 检查各个组件
    python_ok = check_python_version()
    chrome_path = check_chrome_installation()
    selenium_ok = check_selenium()
    
    if python_ok and chrome_path and selenium_ok:
        print("\n🎉 基础环境检查通过！")
        
        # 测试WebDriver
        if test_webdriver():
            print("\n🚀 系统已准备就绪，可以运行DeepSeek客户端")
        else:
            print("\n⚠️  WebDriver有问题，创建简化版演示...")
            create_simple_demo()
    else:
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        create_simple_demo()

if __name__ == "__main__":
    main()