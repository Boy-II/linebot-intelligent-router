#!/usr/bin/env python3
"""
LINE Bot 群組行為測試腳本

此腳本模擬不同的群組訊息情境，測試 bot 是否按預期回應或忽略訊息。
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot_config import bot_config

def test_group_message_handling():
    """測試群組訊息處理邏輯"""
    
    print("🧪 測試 LINE Bot 群組訊息處理邏輯\n")
    
    # 測試案例：各種訊息類型
    test_cases = [
        # (訊息內容, 預期是否回應, 描述)
        ("Hello everyone!", False, "一般群組聊天訊息"),
        ("@視覺設計組 你好", True, "直接 mention bot（新名稱）"),
        ("@assistant 你好", True, "直接 mention bot（舊名稱，相容）"), 
        ("@視覺設計組 /填表", True, "mention bot + 指令"), 
        ("/health", True, "健康檢查指令（無需 mention）"),
        ("/健康檢查", True, "健康檢查指令（中文）"),
        ("/help", True, "說明指令"),
        ("/說明", True, "說明指令（中文）"),
        ("/填表", False, "需要註冊的指令（群組中被限制）"),
        ("/註冊", True, "註冊指令（允許）"),
        ("大家好啊", False, "日常聊天"),
        ("@視覺設計組 畫一張圖", True, "mention + 自然語言需求"),
        ("@bot 你好", False, "錯誤的 mention 名稱"),
        ("誰可以幫我填表？", False, "隱含需求但無 mention"),
        ("@視覺設計組", True, "只有 mention 無內容"),
        ("@assistant /健康檢查", True, "舊名稱 + 指令（相容性測試）"),
    ]
    
    print("📋 測試結果：\n")
    
    for i, (message, expected_response, description) in enumerate(test_cases, 1):
        should_respond = bot_config.should_respond_in_group(message)
        status = "✅ PASS" if should_respond == expected_response else "❌ FAIL"
        
        print(f"{i:2d}. {status} | {description}")
        print(f"    訊息: '{message}'")
        print(f"    預期: {'回應' if expected_response else '忽略'} | 實際: {'回應' if should_respond else '忽略'}")
        
        if should_respond and bot_config.is_bot_mentioned(message):
            cleaned_message = bot_config.remove_mention(message)
            print(f"    清理後: '{cleaned_message}'")
        
        print()

def test_mention_removal():
    """測試 mention 移除功能"""
    
    print("🧹 測試 Mention 移除功能\n")
    
    test_cases = [
        ("@視覺設計組 你好", "你好"),
        ("@視覺設計組 /填表", "/填表"),
        ("@視覺設計組", ""),
        ("你好 @視覺設計組", "你好"),
        ("@視覺設計組 幫我畫一張貓的圖", "幫我畫一張貓的圖"),
        ("@assistant 你好", "你好"),  # 相容性測試
        ("沒有 mention", "沒有 mention"),
    ]
    
    for original, expected in test_cases:
        result = bot_config.remove_mention(original)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        print(f"{status} | '{original}' -> '{result}' (預期: '{expected}')")

def test_command_permissions():
    """測試指令權限"""
    
    print("🔐 測試指令權限\n")
    
    print("📌 群組允許指令（無需 mention）:")
    for cmd in bot_config.group_allowed_commands:
        print(f"  • {cmd}")
    
    print("\n📌 未註冊用戶允許指令:")
    for cmd in bot_config.unregistered_allowed_commands:
        print(f"  • {cmd}")
    
    print("\n📋 權限測試:")
    test_commands = ["/health", "/填表", "/註冊", "/help", "/畫圖", "/unknown"]
    
    for cmd in test_commands:
        group_ok = bot_config.is_group_allowed_command(cmd)
        unreg_ok = bot_config.is_unregistered_allowed_command(cmd)
        print(f"  {cmd:12} | 群組: {'✅' if group_ok else '❌'} | 未註冊: {'✅' if unreg_ok else '❌'}")

def main():
    """主測試函數"""
    print("=" * 60)
    print("LINE Bot 群組行為測試")
    print("=" * 60)
    print()
    
    # 顯示當前配置
    print("🔧 當前 Bot 配置:")
    print(f"  Bot 名稱: {bot_config.bot_name}")
    print(f"  Mention 關鍵字: {bot_config.mention_patterns}")
    print()
    
    # 執行各項測試
    test_group_message_handling()
    print("-" * 60)
    test_mention_removal()
    print("-" * 60)
    test_command_permissions()
    
    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
