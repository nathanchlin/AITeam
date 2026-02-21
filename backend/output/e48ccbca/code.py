import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional
import sqlalchemy
from sqlalchemy import create_engine

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIDataFetcher:
    """
    A股AI概念股票数据获取模块
    """
    
    def __init__(self, tushare_token: str, db_connection_string: Optional[str] = None):
        """
        初始化数据获取器
        
        :param tushare_token: tushare API token
        :param db_connection_string: 数据库连接字符串(可选)
        """
        self.ts_pro = ts.pro_api(tushare_token)
        self.ai_stocks = self._get_ai_concept_stocks()
        self.engine = None
        
        if db_connection_string:
            self.engine = create_engine(db_connection_string)
            logger.info("数据库连接已建立")
    
    def _get_ai_concept_stocks(self) -> List[str]:
        """
        获取AI概念股票列表
        
        :return: AI概念股票代码列表
        """
        try:
            # 获取AI概念板块成分股
            df = self.ts_pro概念板块名称='AI')
            if df.empty:
                logger.warning("未获取到AI概念板块数据，使用预设股票列表")
                # 预设一些知名的AI概念股票代码
                return [
                    '000002', '000858', '002415', '002230', '002236', 
                    '002429', '002439', '002460', '002594', '002624',
                    '002657', '002714', '600000', '600036', '600588',
                    '600706', '600745', '600809', '600900', '600936',
                    '601138', '601318', '601857', '601888', '601939'
                ]
            return df.ts_code.tolist()
        except Exception as e:
            logger.error(f"获取AI概念股票列表失败: {e}")
            return []
    
    def fetch_daily_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取AI概念股票的日线数据
        
        :param start_date: 开始日期 (YYYYMMDD)
        :param end_date: 结束日期 (YYYYMMDD)
        :return: 日线数据DataFrame
        """
        all_data = []
        
        for ts_code in self.ai_stocks:
            try:
                # 获取日线数据
                df = self.ts_pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                
                if not df.empty:
                    df['ts_code'] = ts_code
                    all_data.append(df)
                
                # 避免API频率限制
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"获取股票 {ts_code} 日线数据失败: {e}")
                continue
        
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            logger.info(f"成功获取 {len(result)} 条日线数据")
            return result
        else:
            logger.warning("未获取到任何日线数据")
            return pd.DataFrame()
    
    def fetch_basic_info(self) -> pd.DataFrame:
        """
        获取AI概念股票的基本信息
        
        :return: 基本信息DataFrame
        """
        try:
            df = self.ts_pro.stock_basic(exchange='', list_status='L', 
                                         fields='ts_code,symbol,name,area,industry,list_date')
            ai_info = df[df['ts_code'].isin(self.ai_stocks)]
            logger.info(f"获取到 {len(ai_info)} 只AI概念股票的基本信息")
            return ai_info
        except Exception as e:
            logger.error(f"获取基本信息失败: {e}")
            return pd.DataFrame()
    
    def fetch_financial_data(self) -> pd.DataFrame:
        """
        获取AI概念股票的财务数据
        
        :return: 财务数据DataFrame
        """
        all_data = []
        
        for ts_code in self.ai_stocks:
            try:
                # 获取财务数据 - 这里以利润表为例
                df = self.ts_pro.income(ts_code=ts_code, 
                                       start_date='20200101', 
                                       end_date=datetime.now().strftime('%Y%m%d'))
                
                if not df.empty:
                    df['ts_code'] = ts_code
                    all_data.append(df)
                
                # 避免API频率限制
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"获取股票 {ts_code} 财务数据失败: {e}")
                continue
        
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            logger.info(f"成功获取 {len(result)} 条财务数据")
            return result
        else:
            logger.warning("未获取到任何财务数据")
            return pd.DataFrame()
    
    def fetch_industry_data(self, industry: str = '人工智能') -> pd.DataFrame:
        """
        获取特定行业的板块数据
        
        :param industry: 行业名称
        :return: 行业数据DataFrame
        """
        try:
            df = self.ts_pro.board(name=industry)
            logger.info(f"获取到 {len(df)} 条 {industry} 行业数据")
            return df
        except Exception as e:
            logger.error(f"获取行业数据失败: {e}")
            return pd.DataFrame()
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗
        
        :param df: 原始数据DataFrame
        :return: 清洗后的DataFrame
        """
        if df.empty:
            return df
        
        # 删除重复数据
        df = df.drop_duplicates()
        
        # 处理缺失值
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # 处理日期格式
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        logger.info("数据清洗完成")
        return df
    
    def save_to_database(self, df: pd.DataFrame, table_name: str) -> bool:
        """
        将数据保存到数据库
        
        :param df: 要保存的数据DataFrame
        :param table_name: 表名
        :return: 是否保存成功
        """
        if self.engine is None:
            logger.error("未配置数据库连接")
            return False
        
        try:
            df.to_sql(table_name, self.engine, if_exists='append', index=False)
            logger.info(f"成功将 {len(df)} 条数据保存到表 {table_name}")
            return True
        except Exception as e:
            logger.error(f"保存数据到数据库失败: {e}")
            return False
    
    def fetch_all_data(self, start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        获取所有数据
        
        :param start_date: 开始日期 (YYYYMMDD)
        :param end_date: 结束日期 (YYYYMMDD)
        :return: 包含所有数据的字典
        """
        logger.info("开始获取所有数据...")
        
        # 获取数据
        daily_data = self.fetch_daily_data(start_date, end_date)
        basic_info = self.fetch_basic_info()
        financial_data = self.fetch_financial_data()
        industry_data = self.fetch_industry_data()
        
        # 数据清洗
        daily_data = self.clean_data(daily_data)
        basic_info = self.clean_data(basic_info)
        financial_data = self.clean_data(financial_data)
        industry_data = self.clean_data(industry_data)
        
        # 保存到数据库
        if self.engine:
            self.save_to_database(daily_data, 'ai_daily_data')
            self.save_to_database(basic_info, 'ai_basic_info')
            self.save_to_database(financial_data, 'ai_financial_data')
            self.save_to_database(industry_data, 'ai_industry_data')
        
        return {
            'daily_data': daily_data,
            'basic_info': basic_info,
            'financial_data': financial_data,
            'industry_data': industry_data
        }