#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DeepSeek Web Chat 客户端演示
使用Selenium自动化登录DeepSeek并进行对话
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_client import DeepSeekWebClient


def interactive_demo():
    """交互式演示"""
    print("=== DeepSeek Web Chat 客户端演示 ===\n")
    
    # 获取用户输入
    email = input("请输入DeepSeek邮箱 (或回车使用.env中的配置): ").strip()
    if not email:
        email = None
        
    password = input("请输入DeepSeek密码 (或回车使用.env中的配置): ").strip()
    if not password:
        password = None
    
    headless = input("是否使用无头模式? (y/n, 默认n): ").strip().lower()
    headless = headless == 'y'
    
    # 初始化客户端
    client = DeepSeekWebClient(headless=headless)
    
    try:
        print("\n正在初始化浏览器...")
        if not client.init_driver():
            print("浏览器初始化失败")
            return
            
        print("正在登录...")
        if not client.login(email, password):
            print("登录失败，请检查凭据")
            return
            
        print("\n登录成功！现在可以开始对话了。")
        print("输入 'quit' 退出，输入 'new' 开始新对话，输入 'history' 查看对话历史")
        print("-" * 50)
        
        while True:
            message = input("\n你: ").strip()
            
            if message.lower() == 'quit':
                break
            elif message.lower() == 'new':
                client.start_new_chat()
                continue
            elif message.lower() == 'history':
                history = client.get_conversation_history()
                print(f"\n对话历史 ({len(history)} 条消息):")
                for i, msg in enumerate(history, 1):
                    print(f"{i}. {msg['content'][:100]}...")
                continue
            elif not message:
                continue
                
            # 发送消息并获取响应
            print("AI正在思考...")
            response = client.send_message(message)
            
            if response:
                print(f"\nDeepSeek: {response}")
            else:
                print("\n未收到响应，请重试")
                
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
    finally:
        print("\n正在关闭浏览器...")
        client.close()
        print("演示结束")


def batch_demo():
    """批量测试演示"""
    print("=== DeepSeek 批量测试演示 ===\n")
    
    questions = [
        "你好，请介绍一下你自己",
        "请用Python写一个读取CSV文件的示例",
        "什么是机器学习？",
        "请解释一下深度学习的基本概念"
    ]
    
    client = DeepSeekWebClient(headless=True)  # 批量模式使用无头浏览器
    
    try:
        if not client.init_driver():
            print("浏览器初始化失败")
            return
            
        if not client.login():
            print("登录失败")
            return
            
        print("开始批量测试...\n")
        
        for i, question in enumerate(questions, 1):
            print(f"问题 {i}: {question}")
            response = client.send_message(question)
            
            if response:
                print(f"回答: {response[:200]}...")
                print("-" * 60)
            else:
                print("未收到响应")
                print("-" * 60)
                
        # 截图保存结果
        client.take_screenshot("batch_demo_result.png")
        
    except Exception as e:
        print(f"批量测试出错: {e}")
    finally:
        client.close()


def main():
    """主函数"""
    print("请选择演示模式:")
    print("1. 交互式对话演示")
    print("2. 批量测试演示")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
    except EOFError:
        print("检测到非交互环境，默认使用批量测试演示")
        batch_demo()
        return
    
    if choice == "1":
        interactive_demo()
    elif choice == "2":
        batch_demo()
    else:
        print("无效选择，默认使用批量测试演示")
        batch_demo()


if __name__ == "__main__":
    main()