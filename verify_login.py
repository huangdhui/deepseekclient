#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证登录过程 - 详细调试版本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_client import DeepSeekWebClient
import time

def verify_login():
    """验证登录过程"""
    print("=== 验证DeepSeek登录过程 ===")
    
    # 使用非无头模式以便观察整个过程
    client = DeepSeekWebClient(headless=False, timeout=60)
    
    try:
        print("1. 初始化浏览器...")
        if not client.init_driver():
            print("❌ 浏览器初始化失败")
            return False
        
        print("2. 执行登录...")
        login_result = client.login()
        
        if login_result:
            print("🎉 登录成功！")
            
            # 截图保存成功状态
            client.take_screenshot("login_success.png")
            
            print("3. 测试发送消息...")
            test_message = "你好，请简单介绍一下你自己"
            print(f"发送消息: {test_message}")
            
            response = client.send_message(test_message)
            
            if response:
                print(f"✅ 收到回复: {response[:200]}...")
                
                # 再发送一个消息
                print("\n4. 发送第二个消息...")
                second_message = "请用一句话总结Python的特点"
                response2 = client.send_message(second_message)
                
                if response2:
                    print(f"✅ 收到第二个回复: {response2[:200]}...")
                
                # 保存对话历史
                history = client.get_conversation_history()
                print(f"\n📝 对话历史: {len(history)} 条消息")
                
                # 最终截图
                client.take_screenshot("conversation_complete.png")
                
                print("\n🎊 验证完全成功！客户端完全可用！")
                return True
            else:
                print("❌ 未收到回复")
                return False
        else:
            print("❌ 登录失败")
            
            # 登录失败时的详细分析
            print("\n=== 登录失败分析 ===")
            
            # 检查当前页面状态
            current_url = client.driver.current_url
            page_title = client.driver.title
            
            print(f"当前URL: {current_url}")
            print(f"页面标题: {page_title}")
            
            # 截图用于分析
            client.take_screenshot("login_failed_analysis.png")
            
            # 检查页面上是否有错误信息
            try:
                error_elements = client.driver.find_elements("css selector", 
                    ".error, .alert, .warning, [class*='error'], [class*='alert']")
                
                if error_elements:
                    print("发现页面错误信息:")
                    for i, elem in enumerate(error_elements):
                        try:
                            error_text = elem.text.strip()
                            if error_text:
                                print(f"  错误 {i+1}: {error_text}")
                        except:
                            continue
                else:
                    print("页面上未发现明显的错误信息")
                    
                # 检查是否还在登录页面
                if "sign_in" in current_url:
                    print("仍在登录页面，可能是:")
                    print("  1. 用户名/密码错误")
                    print("  2. 需要验证码或其他验证")
                    print("  3. 账号被锁定")
                    print("  4. 网络延迟导致的超时")
                elif "chat.deepseek.com" in current_url:
                    print("已跳转到主页面，但登录检测逻辑可能有问题")
                else:
                    print(f"跳转到意外页面: {current_url}")
                    
            except Exception as e:
                print(f"分析页面时出错: {e}")
                
            return False
            
    except Exception as e:
        print(f"验证过程出错: {e}")
        if hasattr(client, 'driver') and client.driver:
            client.take_screenshot("verify_error.png")
        return False
        
    finally:
        print("\n5. 保持浏览器打开30秒供观察...")
        time.sleep(30)
        client.close()

if __name__ == "__main__":
    verify_login()