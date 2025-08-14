#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
详细调试DeepSeek页面动态加载
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def detailed_debug():
    """详细调试页面加载过程"""
    print("=== 详细调试DeepSeek页面 ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    try:
        print("1. 访问DeepSeek主页...")
        driver.get("https://chat.deepseek.com")
        time.sleep(3)
        
        print(f"   当前URL: {driver.current_url}")
        print(f"   页面标题: {driver.title}")
        driver.save_screenshot("debug_step1.png")
        
        print("\n2. 分析当前页面元素...")
        analyze_page_elements(driver, "step1")
        
        print("\n3. 访问登录页面...")
        driver.get("https://chat.deepseek.com/sign_in")
        time.sleep(5)  # 等待更长时间
        
        print(f"   当前URL: {driver.current_url}")
        print(f"   页面标题: {driver.title}")
        driver.save_screenshot("debug_step2.png")
        
        print("\n4. 等待页面完全加载...")
        for i in range(10):
            print(f"   等待 {i+1}/10 秒...")
            time.sleep(1)
            elements = driver.find_elements(By.CSS_SELECTOR, "input, button")
            print(f"   当前页面元素数量: {len(elements)}")
            if len(elements) >= 2:
                break
        
        print("\n5. 最终页面分析...")
        analyze_page_elements(driver, "final")
        
        print("\n6. 尝试查找特定元素...")
        
        # 尝试不同的选择器
        selectors_to_try = [
            ("邮箱输入框", [
                "input[type='text']",
                "input[type='email']", 
                "input[placeholder*='邮箱']",
                "input[placeholder*='email']",
                "input[placeholder*='手机']",
                "input[name*='email']",
                "input[name*='username']"
            ]),
            ("密码输入框", [
                "input[type='password']",
                "input[placeholder*='密码']",
                "input[name*='password']"
            ]),
            ("提交按钮", [
                "button[type='submit']",
                "button",
                "input[type='submit']",
                "[role='button']",
                "div[role='button']"
            ])
        ]
        
        for element_name, selectors in selectors_to_try:
            print(f"\n   查找 {element_name}:")
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"     {selector}: 找到 {len(elements)} 个")
                    for i, elem in enumerate(elements):
                        try:
                            text = elem.text.strip() or elem.get_attribute('placeholder') or elem.get_attribute('value') or '无'
                            print(f"       {i+1}. '{text}'")
                        except:
                            print(f"       {i+1}. [无法获取文本]")
                except Exception as e:
                    print(f"     {selector}: 错误 - {e}")
        
        print("\n7. 获取完整页面源码...")
        page_source = driver.page_source
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("   页面源码已保存到 page_source.html")
        
        print(f"   页面源码长度: {len(page_source)} 字符")
        if "登录" in page_source:
            print("   ✅ 页面包含'登录'文字")
        else:
            print("   ❌ 页面不包含'登录'文字")
            
        if "password" in page_source.lower():
            print("   ✅ 页面包含'password'")
        else:
            print("   ❌ 页面不包含'password'")
        
        print("\n8. 手动观察时间（60秒）...")
        print("   你可以在浏览器中手动操作来观察页面行为")
        time.sleep(60)
        
    except Exception as e:
        print(f"调试过程出错: {e}")
        driver.save_screenshot("debug_error.png")
        
    finally:
        driver.quit()
        print("\n调试完成！")

def analyze_page_elements(driver, step_name):
    """分析页面元素"""
    try:
        # 所有输入框
        inputs = driver.find_elements(By.CSS_SELECTOR, "input")
        print(f"   输入框数量: {len(inputs)}")
        for i, inp in enumerate(inputs):
            inp_type = inp.get_attribute('type') or '未知'
            placeholder = inp.get_attribute('placeholder') or '无'
            name = inp.get_attribute('name') or '无'
            value = inp.get_attribute('value') or '无'
            print(f"     {i+1}. type={inp_type}, placeholder='{placeholder}', name='{name}', value='{value}'")
        
        # 所有按钮
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        print(f"   按钮数量: {len(buttons)}")
        for i, btn in enumerate(buttons):
            btn_text = btn.text.strip() or '无文字'
            btn_type = btn.get_attribute('type') or '未知'
            print(f"     {i+1}. text='{btn_text}', type={btn_type}")
        
        # 表单
        forms = driver.find_elements(By.CSS_SELECTOR, "form")
        print(f"   表单数量: {len(forms)}")
        
        # div元素（可能是按钮）
        divs_with_role = driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
        print(f"   div[role='button']数量: {len(divs_with_role)}")
        
    except Exception as e:
        print(f"   分析页面元素时出错: {e}")

if __name__ == "__main__":
    detailed_debug()