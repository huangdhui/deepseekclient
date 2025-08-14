#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试登录过程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_client import DeepSeekWebClient
import time

def debug_login():
    """调试登录过程"""
    print("=== 调试DeepSeek登录过程 ===")
    
    # 使用非无头模式以便观察
    client = DeepSeekWebClient(headless=False, timeout=60)
    
    try:
        print("正在初始化浏览器...")
        if not client.init_driver():
            print("浏览器初始化失败")
            return
        
        print("正在访问登录页面...")
        client.driver.get("https://chat.deepseek.com/sign_in")
        time.sleep(5)
        
        print(f"当前URL: {client.driver.current_url}")
        print(f"页面标题: {client.driver.title}")
        
        # 截图保存当前状态
        client.take_screenshot("debug_login_start.png")
        
        print("\n=== 分析页面元素 ===")
        
        # 查找所有输入框
        all_inputs = client.driver.find_elements("css selector", "input")
        print(f"总共找到 {len(all_inputs)} 个输入框:")
        for i, inp in enumerate(all_inputs):
            inp_type = inp.get_attribute('type') or '未知'
            placeholder = inp.get_attribute('placeholder') or '无'
            name = inp.get_attribute('name') or '无'
            print(f"  {i+1}. type={inp_type}, placeholder={placeholder}, name={name}")
        
        # 查找所有按钮
        all_buttons = client.driver.find_elements("css selector", "button")
        print(f"\n总共找到 {len(all_buttons)} 个按钮:")
        for i, btn in enumerate(all_buttons):
            btn_text = btn.text.strip() or '无文字'
            btn_type = btn.get_attribute('type') or '未知'
            print(f"  {i+1}. text='{btn_text}', type={btn_type}")
        
        # 查找表单
        forms = client.driver.find_elements("css selector", "form")
        print(f"\n找到 {len(forms)} 个表单")
        
        print("\n=== 手动等待（你可以在浏览器中观察页面） ===")
        print("程序会在30秒后自动关闭浏览器...")
        time.sleep(30)
        
    except Exception as e:
        print(f"调试过程出错: {e}")
        client.take_screenshot("debug_error.png")
        
    finally:
        client.close()

if __name__ == "__main__":
    debug_login()