# 使用示例
if __name__ == "__main__":
    # 替换为你的tushare token
    TUSHARE_TOKEN = "你的tushare_token"
    
    # 可选: 数据库连接字符串
    DB_CONNECTION_STRING = "sqlite:///ai_stock_data.db"
    
    # 创建数据获取器
    fetcher = AIDataFetcher(TUSHARE_TOKEN, DB_CONNECTION_STRING)
    
    # 设置日期范围 (获取最近一年的数据)
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    # 获取所有数据
    data = fetcher.fetch_all_data(start_date, end_date)
    
    # 打印数据概览
    for name, df in data.items():
        print(f"\n{name} 数据概览:")
        print(f"记录数: {len(df)}")
        print(df.head())