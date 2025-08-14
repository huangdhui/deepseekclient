#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试凭据格式和输入过程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_client import DeepSeekWebClient
import time
from dotenv import load_dotenv

def test_credentials():
    """测试凭据和输入过程"""
    print("=== 测试凭据和输入过程 ===")
    
    # 加载环境变量
    load_dotenv()
    
    email = os.getenv('DEEPSEEK_EMAIL')
    password = os.getenv('DEEPSEEK_PASSWORD')
    
    print(f"从.env文件读取到:")
    print(f"  邮箱: {email}")
    print(f"  密码: {'*' * len(password) if password else 'None'}")
    
    if not email or not password:
        print("❌ 未找到登录凭据")
        print("请检查.env文件是否正确配置:")
        print("DEEPSEEK_EMAIL=your_email@example.com")
        print("DEEPSEEK_PASSWORD=your_password")
        return False
    
    # 非无头模式以便观察
    client = DeepSeekWebClient(headless=False, timeout=60)
    
    try:
        print("\n1. 初始化浏览器...")
        if not client.init_driver():
            return False
        
        print("2. 访问登录页面...")
        client.driver.get("https://chat.deepseek.com/sign_in")
        time.sleep(3)
        
        print("3. 切换到密码登录...")
        # 查找并点击密码登录
        all_elements = client.driver.find_elements("css selector", "*")
        password_login_element = None
        
        for element in all_elements:
            try:
                if element.text.strip() == "密码登录":
                    password_login_element = element
                    break
            except:
                continue
        
        if password_login_element:
            password_login_element.click()
            time.sleep(3)
            print("✅ 切换到密码登录模式")
        
        print("4. 详细输入过程观察...")
        
        # 找到邮箱输入框
        email_input = client.driver.find_element("css selector", "input[type='text']")
        print(f"邮箱输入框当前值: '{email_input.get_attribute('value')}'")
        
        # 清空并慢慢输入邮箱
        email_input.clear()
        time.sleep(1)
        
        print(f"正在输入邮箱: {email}")
        for char in email:
            email_input.send_keys(char)
            time.sleep(0.1)  # 慢慢输入以模拟人工操作
        
        time.sleep(2)
        print(f"邮箱输入后的值: '{email_input.get_attribute('value')}'")
        
        # 找到密码输入框
        password_input = client.driver.find_element("css selector", "input[type='password']")
        print(f"密码输入框当前值长度: {len(password_input.get_attribute('value'))}")
        
        # 清空并慢慢输入密码
        password_input.clear()
        time.sleep(1)
        
        print("正在输入密码...")
        for char in password:
            password_input.send_keys(char)
            time.sleep(0.1)
        
        time.sleep(2)
        print(f"密码输入后的值长度: {len(password_input.get_attribute('value'))}")
        
        # 截图查看输入状态
        client.take_screenshot("credentials_input_check.png")
        
        print("\n5. 现在可以手动检查输入是否正确...")
        print("   - 查看浏览器中的输入内容")
        print("   - 可以手动尝试登录来验证凭据")
        print("   - 程序会在60秒后自动关闭")
        
        # 等待用户观察
        time.sleep(60)
        
        return True
        
    except Exception as e:
        print(f"测试过程出错: {e}")
        client.take_screenshot("credentials_test_error.png")
        return False
        
    finally:
        client.close()

if __name__ == "__main__":
    test_credentials()