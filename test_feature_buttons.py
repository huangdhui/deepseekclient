#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试功能按钮选择功能
"""

from src.deepseek_client import DeepSeekWebClient
import time

def test_feature_buttons():
    """测试功能按钮选择功能"""
    print("=== 测试功能按钮选择功能 ===")
    
    # 创建客户端（非无头模式便于观察）
    client = DeepSeekWebClient(headless=False, timeout=30)
    
    try:
        print("🔐 正在登录...")
        if client.login():
            print("✅ 登录成功")
            
            # 等待页面稳定
            time.sleep(3)
            
            print("🔍 测试功能按钮选择...")
            # 手动调用功能按钮选择方法
            client.select_feature_buttons()
            
            print("💬 发送测试消息...")
            test_message = "请介绍一下人工智能的发展历史"
            
            response = client.send_message(test_message)
            
            if response:
                print(f"✅ 成功接收到流式响应:")
                print(f"📝 响应长度: {len(response)} 字符")
                print(f"📄 响应内容: {response[:200]}...")
                
                # 截图保存结果
                client.take_screenshot("feature_buttons_test.png")
                
            else:
                print("❌ 未接收到响应")
                client.take_screenshot("feature_buttons_failed.png")
                
        else:
            print("❌ 登录失败")
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        client.take_screenshot("feature_buttons_error.png")
        
    finally:
        print("⏱️ 保持浏览器打开30秒以便观察...")
        time.sleep(30)
        client.close()
        print("🔧 测试完成")

if __name__ == "__main__":
    test_feature_buttons()
