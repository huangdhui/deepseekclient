#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析DeepSeek的登录方式
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def analyze_login_methods():
    """分析登录方式"""
    print("=== 分析DeepSeek登录方式 ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("1. 访问登录页面...")
        driver.get("https://chat.deepseek.com/sign_in")
        time.sleep(5)
        
        driver.save_screenshot("login_analysis_1.png")
        
        print("\n2. 初始页面分析...")
        print("   查找所有可点击元素（可能是切换登录方式的按钮）...")
        
        clickable_elements = driver.find_elements(By.CSS_SELECTOR, 
            "a, button, div[role='button'], span[role='button'], [onclick], .clickable, .tab, .switch")
        
        print(f"找到 {len(clickable_elements)} 个可点击元素:")
        for i, elem in enumerate(clickable_elements):
            try:
                text = elem.text.strip()
                tag = elem.tag_name
                role = elem.get_attribute('role') or ''
                onclick = elem.get_attribute('onclick') or ''
                class_name = elem.get_attribute('class') or ''
                
                if text or 'button' in role or onclick or '登录' in class_name or 'login' in class_name:
                    print(f"  {i+1}. <{tag}> '{text}' role='{role}' class='{class_name}'")
                    
            except:
                continue
        
        print("\n3. 查找密码登录相关的文本...")
        page_text = driver.page_source.lower()
        password_keywords = ['密码登录', 'password', '账号密码', '邮箱登录', 'email login']
        
        for keyword in password_keywords:
            if keyword in page_text:
                print(f"   ✅ 找到关键词: '{keyword}'")
            else:
                print(f"   ❌ 未找到: '{keyword}'")
        
        print("\n4. 尝试输入邮箱看页面变化...")
        
        # 找到邮箱输入框
        email_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[placeholder*='邮箱'], input[placeholder*='手机']")
        if email_inputs:
            email_input = email_inputs[0]
            print("   输入测试邮箱...")
            email_input.clear()
            email_input.send_keys("test@example.com")
            time.sleep(3)
            
            driver.save_screenshot("login_analysis_2.png")
            
            print("   输入邮箱后的页面元素:")
            new_inputs = driver.find_elements(By.CSS_SELECTOR, "input")
            for i, inp in enumerate(new_inputs):
                inp_type = inp.get_attribute('type')
                placeholder = inp.get_attribute('placeholder')
                print(f"     输入框 {i+1}: type={inp_type}, placeholder='{placeholder}'")
        
        print("\n5. 尝试手机号...")
        if email_inputs:
            email_input = email_inputs[0]
            print("   清除并输入测试手机号...")
            email_input.clear()
            email_input.send_keys("13800138000")
            time.sleep(3)
            
            driver.save_screenshot("login_analysis_3.png")
            
            print("   输入手机号后的页面元素:")
            new_inputs = driver.find_elements(By.CSS_SELECTOR, "input")
            for i, inp in enumerate(new_inputs):
                inp_type = inp.get_attribute('type')
                placeholder = inp.get_attribute('placeholder')
                print(f"     输入框 {i+1}: type={inp_type}, placeholder='{placeholder}'")
        
        print("\n6. 查找页面上所有文本（寻找切换选项）...")
        all_text_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        relevant_texts = []
        
        for elem in all_text_elements:
            try:
                text = elem.text.strip()
                if text and len(text) < 50:  # 短文本，可能是按钮或链接
                    keywords = ['密码', 'password', '切换', 'switch', '其他', '登录方式', '验证码']
                    if any(keyword in text.lower() for keyword in keywords):
                        relevant_texts.append(text)
            except:
                continue
        
        print("   相关文本:")
        for text in set(relevant_texts):  # 去重
            print(f"     '{text}'")
        
        print("\n7. 手动观察时间（30秒）...")
        time.sleep(30)
        
    except Exception as e:
        print(f"分析过程出错: {e}")
        driver.save_screenshot("analysis_error.png")
        
    finally:
        driver.quit()
        print("\n分析完成！")

if __name__ == "__main__":
    analyze_login_methods()