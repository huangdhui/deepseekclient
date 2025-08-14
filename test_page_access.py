#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试页面访问的脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_client import DeepSeekWebClient
import time

def test_page_access():
    """测试访问DeepSeek页面"""
    print("=== 测试DeepSeek页面访问 ===")
    
    client = DeepSeekWebClient(headless=False, timeout=30)  # 非无头模式以便观看
    
    try:
        print("正在初始化浏览器...")
        if not client.init_driver():
            print("浏览器初始化失败")
            return False
        
        print("正在访问DeepSeek主页...")
        client.driver.get("https://chat.deepseek.com")
        
        # 等待页面加载
        time.sleep(3)
        
        print(f"页面标题: {client.driver.title}")
        print(f"当前URL: {client.driver.current_url}")
        
        # 截图
        client.take_screenshot("deepseek_homepage.png")
        
        # 访问登录页面
        print("正在访问登录页面...")
        client.driver.get("https://chat.deepseek.com/sign_in")
        time.sleep(3)
        
        print(f"登录页面标题: {client.driver.title}")
        client.take_screenshot("deepseek_login.png")
        
        # 查找页面元素
        print("正在分析页面元素...")
        try:
            email_inputs = client.driver.find_elements("css selector", "input[type='email'], input[placeholder*='邮箱'], input[placeholder*='email']")
            print(f"找到 {len(email_inputs)} 个邮箱输入框")
            
            password_inputs = client.driver.find_elements("css selector", "input[type='password']")
            print(f"找到 {len(password_inputs)} 个密码输入框")
            
            buttons = client.driver.find_elements("css selector", "button")
            print(f"找到 {len(buttons)} 个按钮")
            
        except Exception as e:
            print(f"页面元素分析出错: {e}")
        
        print("✅ 页面访问测试成功！")
        print("你可以查看截图文件来确认页面加载情况")
        
        # 保持浏览器打开一段时间以便观察
        print("浏览器将在10秒后自动关闭...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"❌ 页面访问测试失败: {e}")
        return False
        
    finally:
        client.close()

if __name__ == "__main__":
    test_page_access()