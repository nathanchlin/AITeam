import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import akshare as ak
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings

# 忽略警告
warnings.filterwarnings('ignore')

print("环境验证:")
print(f"pandas版本: {pd.__version__}")
print(f"numpy版本: {np.__version__}")
print(f"matplotlib版本: {plt.__version__}")
print(f"seaborn版本: {sns.__version__}")
print(f"akshare版本: {ak.__version__}")

# 测试数据获取
try:
    # 获取AI概念股列表
    ai_stocks = ak.stock_board_industry_name_em()
    ai_stocks = ai_stocks[ai_stocks['板块名称'].str.contains('AI|人工智能|智能|科技', na=False)]
    print(f"\n成功获取AI相关板块股票，共{len(ai_stocks)}只")
    print(ai_stocks.head())
    
    # 获取某只股票的历史数据
    stock_code = ai_stocks.iloc[0]['板块代码']
    stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date="20230101", end_date="20231231", adjust="")
    print(f"\n成功获取{stock_code}的历史数据，共{len(stock_data)}条记录")
    print(stock_data.head())
    
    # 测试机器学习模型
    X = np.random.rand(100, 5)
    y = np.random.rand(100)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"\n机器学习模型测试得分: {score:.4f}")
    
    print("\n✅ 所有环境验证通过！")
    
except Exception as e:
    print(f"\n❌ 环境验证失败: {str(e)}")