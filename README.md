### E-commerce Platform Data Analytics Project Study Guide

#### Project Overview
This project is suitable as an introductory learning for data analysis, by crawling Huawei Pura X product data from Taobao, JD.com, and Pinduoduo, visualizing and analyzing it and storing it in a MySQL database.

#### Runtime environment preparation

##### Base environment
- **Python environment**: Python must be pre-installed (version 3.7 recommended)
- MySQL database: Install it on your local computer
- Default login username: 'root'
- Default Login Password: '123456'

##### Browsers and drivers
- **Chrome**: Requires the latest version
- **ChromeDriver Plug-in**: The version must match the Chrome browser

##### Python dependency libraries
The following Python modules need to be installed before running the script:
```bash
pip install pandas matplotlib pymysql beautifulsoup4 selenium numpy
```

#### Project Functional Module
- **Data Collection**: Obtain product data from the three major e-commerce platforms through Selenium simulated browser operation
- Data Processing: Use pandas for data cleansing and transformation
- Visual Analysis: Visualize data with matplotlib for bar and line charts
- Data Storage: Save the analysis results to a MySQL database

#### Learning Focus
1. Web crawler basics
2. Data processing and analysis processes
3. Data visualization methods
4. Get started with database operations

#### Project structure
- Main program file: Contains complete crawler and analysis logic
- Data file: Stores the crawled raw data
- Visualizations: The generated analytics charts will be saved locally

#### Precautions
- When running the program, you need to manually scan the QR code to log in to Taobao and JD.com and Pinduoduo
- Do not close the browser window that opens automatically during the crawling process
- The database configuration allows you to modify the connection parameters in the code as needed
- The first run automatically creates a database and data table

###  V1.1 What's New Description:

1. **Custom Product Name:**

* When the program runs, you will be prompted to enter a keyword (the default is 'huaweipurax').

2. Custom database connection parameters:

* Prompt for host, user name, password, and database name (all with default values) at startup.

Through this project, you will learn the complete process of data analysis, from data acquisition, cleaning, analysis to visualization and storage, which is a good entry-level practical project.
