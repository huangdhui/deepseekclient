#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试密码登录切换功能
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test_password_switch():
    """测试密码登录切换"""
    print("=== 测试密码登录切换 ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("1. 访问登录页面...")
        driver.get("https://chat.deepseek.com/sign_in")
        time.sleep(3)
        driver.save_screenshot("switch_test_1.png")
        
        print("\n2. 初始状态分析...")
        inputs = driver.find_elements(By.CSS_SELECTOR, "input")
        for i, inp in enumerate(inputs):
            print(f"   输入框 {i+1}: type={inp.get_attribute('type')}, placeholder={inp.get_attribute('placeholder')}")
        
        print("\n3. 查找所有包含'密码登录'的元素...")
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        password_elements = []
        
        for element in all_elements:
            try:
                text = element.text.strip()
                if "密码登录" in text:
                    tag = element.tag_name
                    class_name = element.get_attribute('class') or ''
                    role = element.get_attribute('role') or ''
                    clickable = element.is_enabled() and element.is_displayed()
                    
                    password_elements.append({
                        'element': element,
                        'text': text,
                        'tag': tag,
                        'class': class_name,
                        'role': role,
                        'clickable': clickable
                    })
                    
                    print(f"   找到: <{tag}> '{text}' clickable={clickable}")
                    print(f"         class='{class_name}'")
                    print(f"         role='{role}'")
                    print()
            except:
                continue
        
        print(f"总共找到 {len(password_elements)} 个包含'密码登录'的元素")
        
        print("\n4. 尝试点击每个元素...")
        for i, elem_info in enumerate(password_elements):
            print(f"\n   尝试点击元素 {i+1}: {elem_info['text']}")
            
            if elem_info['clickable']:
                try:
                    # 先滚动到元素位置
                    driver.execute_script("arguments[0].scrollIntoView();", elem_info['element'])
                    time.sleep(1)
                    
                    # 点击元素
                    elem_info['element'].click()
                    print("     ✅ 点击成功")
                    time.sleep(3)
                    
                    # 检查页面变化
                    new_inputs = driver.find_elements(By.CSS_SELECTOR, "input")
                    print("     点击后的输入框:")
                    for j, inp in enumerate(new_inputs):
                        inp_type = inp.get_attribute('type')
                        placeholder = inp.get_attribute('placeholder')
                        print(f"       {j+1}. type={inp_type}, placeholder={placeholder}")
                    
                    # 截图
                    driver.save_screenshot(f"switch_test_after_click_{i+1}.png")
                    
                    # 如果找到密码输入框，说明切换成功
                    password_inputs = [inp for inp in new_inputs if inp.get_attribute('type') == 'password']
                    if password_inputs:
                        print("     🎉 成功切换到密码登录！")
                        return True
                    else:
                        print("     ❌ 未切换到密码登录，继续尝试...")
                        
                except Exception as e:
                    print(f"     ❌ 点击失败: {e}")
            else:
                print("     ⚠️  元素不可点击")
        
        print("\n5. 尝试其他方法...")
        
        # 尝试查找特定的切换按钮或链接
        switch_selectors = [
            "a:contains('密码登录')",
            "button:contains('密码登录')",
            "[data-testid*='password']",
            ".password-login",
            ".login-type-switch"
        ]
        
        # 由于CSS :contains() 不被支持，我们用JavaScript查找
        js_script = """
        var elements = document.querySelectorAll('*');
        var result = [];
        for (var i = 0; i < elements.length; i++) {
            if (elements[i].textContent && elements[i].textContent.includes('密码登录')) {
                result.push(elements[i]);
            }
        }
        return result;
        """
        
        js_elements = driver.execute_script(js_script)
        print(f"   JavaScript找到 {len(js_elements)} 个元素")
        
        for i, elem in enumerate(js_elements[:3]):  # 只尝试前3个
            try:
                print(f"   尝试JavaScript点击元素 {i+1}...")
                driver.execute_script("arguments[0].click();", elem)
                time.sleep(3)
                
                # 检查结果
                new_inputs = driver.find_elements(By.CSS_SELECTOR, "input")
                password_inputs = [inp for inp in new_inputs if inp.get_attribute('type') == 'password']
                if password_inputs:
                    print("     🎉 JavaScript点击成功切换到密码登录！")
                    driver.save_screenshot(f"switch_success_js_{i+1}.png")
                    return True
                    
            except Exception as e:
                print(f"     JavaScript点击失败: {e}")
        
        print("\n❌ 所有切换尝试都失败了")
        return False
        
    except Exception as e:
        print(f"测试过程出错: {e}")
        driver.save_screenshot("switch_test_error.png")
        return False
        
    finally:
        print("\n手动观察时间（30秒）...")
        time.sleep(30)
        driver.quit()

if __name__ == "__main__":
    test_password_switch()