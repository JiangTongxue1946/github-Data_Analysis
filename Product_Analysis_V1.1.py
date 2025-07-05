import pandas as pd
import matplotlib.pyplot as plt
import pymysql
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import warnings
import numpy as np

warnings.filterwarnings('ignore')  # 忽略警告


class ECommerceScraper:

    #  数据库配置
    def __init__(self, db_config=None):
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',
            'database': 'product_data'
        }
        self.driver = None

    def init_driver(self, headless=False):
        """初始化WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")  # 启动无头模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)  # ✅ 无论是否 headless，都初始化 driver
        return self.driver

    #  关闭WebDriver
    def close_driver(self):
        """关闭WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    #  获取淘宝数据
    def get_taobao_data(self, keyword='huaweipurax', max_items=10):
        """获取淘宝数据"""
        print("开始爬取淘宝数据...")
        self.init_driver(headless=False)  # 淘宝需要登录，不使用无头模式

        try:
            url = f"https://s.taobao.com/search?q={keyword}"
            self.driver.get(url)

            print("请在60秒内扫码登录...")
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.doubleCard--gO3Bz6bu'))  # 等待加载更多商品
            )
            print("登录成功，开始采集数据")

            # 滚动页面加载更多商品
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')  # 创建BeautifulSoup对象
            items = soup.find_all('div', class_='doubleCard--gO3Bz6bu')  # 获取所有商品

            data = []
            for item in items[:max_items]:
                try:
                    # 获取价格
                    price_div = item.find('div', class_='priceInt--yqqZMJ5a')  # 获取价格
                    price = float(price_div.get_text(strip=True)) if price_div else 0  # 处理价格文本

                    # 获取销量
                    sales_span = item.find('span', class_='shopTagText--wujObz6g')  # 获取销量
                    sales_text = sales_span.get_text(strip=True) if sales_span else '0'  # 处理销量文本

                    # 处理销量文本（如"1万+"转换为10000）
                    if '万' in sales_text:
                        sales = float(''.join(filter(str.isdigit, sales_text))) * 10000  # 处理销量文本
                    else:
                        sales = float(''.join(filter(str.isdigit, sales_text)))  # 处理销量文本

                    data.append({
                        'platform': 'taobao',
                        'price': price,
                        'sales': sales
                    })
                except Exception as e:
                    print(f"处理商品时出错: {e}")

            print(f"成功获取{len(data)}条淘宝数据")
            return data
        except Exception as e:
            print(f"获取淘宝数据时出错: {e}")
            return []
        finally:
            self.close_driver()

    #  京东
    def get_jd_data(self, keyword='huaweipurax', max_items=10):
        """获取京东数据"""
        print("开始爬取京东数据...")
        self.init_driver(headless=False)  # 京东需登录不使用无头模式

        try:
            url = f"https://search.jd.com/Search?keyword={keyword}"
            self.driver.get(url)

            #  等待登录
            print("请在60秒内扫码登录京东账号...")

            #  等待加载更多商品
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "J_goodsList"))
            )
            print("登录成功，开始采集京东数据")

            # 滚动页面加载更多内容
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')  # 创建BeautifulSoup对象
            items = soup.find_all('li', class_='gl-item')  # 获取所有商品

            data = []
            for item in items[:max_items]:
                try:
                    # 获取价格
                    price_tag = item.find('div', class_='p-price').find('i')
                    price = float(price_tag.text.strip()) if price_tag else 0

                    # 获取销量
                    sales_tag = item.find('div', class_='p-commit').find('strong')
                    sales_text = sales_tag.text.strip() if sales_tag else '0'

                    # 处理销量文本
                    if '万' in sales_text:
                        sales = float(sales_text.replace('万+', '')) * 10000
                    else:
                        sales = float(''.join(filter(str.isdigit, sales_text)))

                    data.append({
                        'platform': 'jingdong',
                        'price': price,
                        'sales': sales
                    })
                except Exception as e:
                    print(f"处理商品时出错: {e}")

            print(f"成功获取{len(data)}条京东数据")
            return data
        except Exception as e:
            print(f"获取京东数据时出错: {e}")
            return []
        finally:
            self.close_driver()

    #  拼多多
    def get_pinduoduo_data(self, keyword='huaweipurax', max_items=10):
        """获取拼多多数据"""
        print("开始爬取拼多多数据...")

        chrome_options = Options()

        # 你可以根据需要添加其他选项
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        driver = webdriver.Chrome(options=chrome_options)

        url = f"https://mobile.yangkeduo.com/search_result.html?search_key={keyword}"
        print("正在打开拼多多搜索页面...")
        driver.get(url)

        #  等待商品加载
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div._3glhOBhU"))
            )
        except:
            print("等待商品加载超时，可能被反爬或页面结构变化")
            driver.quit()
            return []

        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

        # 获取页面源代码
        page_source = driver.page_source
        driver.quit()

        #  创建BeautifulSoup对象
        soup = BeautifulSoup(page_source, 'html.parser')
        items = soup.find_all('div', class_='_3glhOBhU')

        #  处理数据
        data = []
        for item in items[:max_items]:
            try:
                price_div = item.find('div', class_='_3z6X2mz1')
                if price_div:
                    price_span = price_div.find('span', class_='_3_U04GgA')
                    if price_span:
                        price_parts = price_span.find_all('span')
                        if len(price_parts) >= 2:
                            price = float(price_parts[1].get_text(strip=True))  # 获取价格文本
                        else:
                            price = 0
                    else:
                        price = 0
                else:
                    price = 0
            except Exception as e:
                price = 0
                print(f"价格解析错误: {e}")

            #  销量
            try:
                sales_tag = item.find('span', class_='_32q8gNKM')
                if sales_tag:
                    sales_text = sales_tag.get_text(strip=True)  # 获取销量文本
                    sales = ''.join(filter(str.isdigit,
                                           sales_text.replace('万+', '0000').replace('+', '').replace('人已拼',
                                                                                                      ''))) or '0'  # 使用正则表达式处理拼多多的销量文本
                    sales = int(sales)  # 转换为整数
                else:
                    sales = 0
            except Exception as e:
                sales = 0
                print(f"销量解析错误: {e}")

            data.append({
                'platform': 'pinduoduo',
                'price': price,
                'sales': sales
            })

        print(f"成功获取{len(data)}条拼多多数据")
        return data

    #  获取所有平台数据
    def get_all_data(self, keyword='huaweipurax', max_items_per_platform=10):
        """获取所有平台数据"""
        taobao_data = self.get_taobao_data(keyword, max_items_per_platform)
        jd_data = self.get_jd_data(keyword, max_items_per_platform)
        pinduoduo_data = self.get_pinduoduo_data(keyword, max_items_per_platform)

        all_data = taobao_data + jd_data + pinduoduo_data
        print(f"总共获取{len(all_data)}条数据")
        return all_data

    #  可视化分析数据
    def visualize_data(self, df):
        """可视化分析数据"""
        if df.empty:
            print("没有数据可进行可视化")
            return

        platforms = df['platform'].unique()
        avg_prices = df.groupby('platform')['price'].mean()
        total_sales = df.groupby('platform')['sales'].sum()

        x = np.arange(len(platforms))
        width = 0.4

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 主图：柱状图
        ax1.bar(x, avg_prices, width=width, color='#4ECDC4')
        ax1.set_title('The average price of each platform')  # 标题为各平台平均价格
        ax1.set_xlabel('platform')  # x轴标签为平台名称
        ax1.set_ylabel('avgp_rice')  # y轴标签为平均价格
        ax1.set_xticks(x)
        ax1.set_xticklabels(platforms)

        # 副图：双 Y 轴折线图
        ax2.set_title(
            'Comparison of average price and total sales volume by platform (dual axis)')  # 标题为各平台平均价格与总销量对比（双轴）
        ax2.set_xlabel('platform')  # x轴标签为平台名称

        color_price = '#FF6B6B'
        color_sales = '#556270'

        ax2_1 = ax2
        ax2_2 = ax2_1.twinx()

        ax2_1.plot(platforms, avg_prices, color=color_price, marker='o', label='avgp_rice')  # 绘制 平均价格
        ax2_1.set_ylabel('avgp_rice', color=color_price)  # y轴标签为 平均价格
        ax2_1.tick_params(axis='y', labelcolor=color_price)

        ax2_2.plot(platforms, total_sales, color=color_sales, marker='s', label='total_sales')  # 绘制 总销量
        ax2_2.set_ylabel('total_sales', color=color_sales)  # y轴标签为 总销量
        ax2_2.tick_params(axis='y', labelcolor=color_sales)

        # 设置主标题
        fig.suptitle('Comparison chart of price and sales analysis by platform', fontsize=16)  # 设置主标题为各平台与销量分析对比图
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        plt.savefig('ecommerce_analysis_updated.png', dpi=300)
        plt.show()

    #  保存数据到数据库
    def create_database_table(self):
        """创建数据库和表"""
        try:
            # 创建数据库连接（无数据库名）
            conn = pymysql.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            cursor = conn.cursor()

            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
            print(f"数据库 {self.db_config['database']} 已创建或已存在")

            # 切换到目标数据库
            cursor.execute(f"USE {self.db_config['database']}")

            # 创建表
            create_table_query = """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                platform VARCHAR(20) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                sales INT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            print("数据表 products 已创建或已存在")

        except pymysql.Error as e:
            print(f"数据库操作出错: {e}")
        finally:
            if conn:
                conn.close()

    #  保存数据到MySQL
    def save_to_mysql(self, data_list):
        """保存数据到MySQL"""
        if not data_list:
            print("没有数据需要保存")
            return

        try:
            self.create_database_table()  # 创建数据库和表

            conn = pymysql.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            cursor = conn.cursor()

            # 插入数据
            insert_query = """
            INSERT INTO products (platform, price, sales)
            VALUES (%s, %s, %s)
            """

            records = [(item['platform'], item['price'], item['sales']) for item in data_list]  # 将数据列表转换为元组列表
            cursor.executemany(insert_query, records)  # 执行批量插入
            conn.commit()

            print(f"成功保存 {len(records)} 条数据到MySQL数据库")

        except pymysql.Error as e:
            print(f"保存数据到数据库时出错: {e}")
        finally:
            if conn:
                conn.close()

    #  主函数
    def run(self, keyword='huaweipurax', max_items_per_platform=10):
        """执行完整流程"""
        # 获取数据
        all_data = self.get_all_data(keyword, max_items_per_platform)  # max_items_per_platform为可选参数，默认为10

        if not all_data:
            print("未获取到任何数据，程序终止")
            return

        # 转换为DataFrame
        df = pd.DataFrame(all_data)
        print("\n获取的数据:")
        print(df)

        # 可视化分析
        print("\n进行可视化分析...")
        self.visualize_data(df)

        # 保存到数据库
        print("\n保存数据到数据库...")
        self.save_to_mysql(all_data)

        print("\n程序执行完毕!")


#  主函数
if __name__ == "__main__":
    # 用户输入数据库配置
    host = input("请输入数据库主机地址（默认 localhost）: ") or 'localhost'
    user = input("请输入数据库用户名（默认 root）: ") or 'root'
    password = input("请输入数据库密码（默认 123456）: ") or '123456'
    database = input("请输入数据库名（默认 product_data）: ") or 'product_data'

    db_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }

    # 用户输入商品关键词
    keyword = input("请输入要爬取的商品关键词（默认 huaweipurax）: ") or 'huaweipurax'

    # 启动爬虫
    scraper = ECommerceScraper(db_config)
    scraper.run(keyword=keyword, max_items_per_platform=10)  # 运行程序