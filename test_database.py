"""
資料庫測試工具
用於驗證資料庫連接和表結構
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def test_database_comprehensive():
    """全面測試資料庫功能"""
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres')
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔗 資料庫連接測試...")
            
            # 1. 基本連接測試
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ 基本連接成功")
            
            # 2. 檢查所有表
            result = conn.execute(text("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = list(result)
            print(f"📊 發現 {len(tables)} 個表:")
            for table in tables:
                print(f"  - {table[0]} ({table[1]})")
            
            # 3. 檢查 LineBot 相關表結構
            linebot_tables = ['line_users', 'user_contexts', 'user_tasks']
            for table_name in linebot_tables:
                try:
                    result = conn.execute(text(f"""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}'
                        ORDER BY ordinal_position
                    """))
                    columns = list(result)
                    if columns:
                        print(f"🗂️  表 '{table_name}' 結構:")
                        for col in columns:
                            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                            print(f"    {col[0]}: {col[1]} ({nullable})")
                    else:
                        print(f"⚠️  表 '{table_name}' 不存在")
                except Exception as e:
                    print(f"❌ 檢查表 '{table_name}' 失敗: {e}")
            
            # 4. 測試基本 CRUD 操作
            print("\n🧪 測試基本操作...")
            
            # 清理測試數據
            conn.execute(text("DELETE FROM line_users WHERE line_id = 'test_user_123'"))
            conn.commit()
            
            # 插入測試
            conn.execute(text("""
                INSERT INTO line_users (line_id, name, email, user_metadata) 
                VALUES ('test_user_123', 'Test User', 'test@example.com', '{"test": true}')
            """))
            conn.commit()
            print("✅ 插入測試成功")
            
            # 查詢測試
            result = conn.execute(text("""
                SELECT line_id, name, email FROM line_users 
                WHERE line_id = 'test_user_123'
            """))
            user = result.fetchone()
            if user:
                print(f"✅ 查詢測試成功: {user[1]} ({user[2]})")
            
            # 更新測試
            conn.execute(text("""
                UPDATE line_users 
                SET name = 'Updated Test User' 
                WHERE line_id = 'test_user_123'
            """))
            conn.commit()
            print("✅ 更新測試成功")
            
            # 刪除測試
            conn.execute(text("DELETE FROM line_users WHERE line_id = 'test_user_123'"))
            conn.commit()
            print("✅ 刪除測試成功")
            
            print("\n🎉 所有資料庫測試通過！")
            return True
            
    except Exception as e:
        print(f"❌ 資料庫測試失敗: {e}")
        return False

if __name__ == "__main__":
    test_database_comprehensive()
