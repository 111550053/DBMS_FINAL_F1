# DBMS_FINAL_F1

## About this project
這是資料庫系統概論的期末專題，我們想製作一個網頁讓使用者查詢過去F1比賽的賽事結果與分析資訊。

主要以下三個功能為主：
1. 單場比賽分析：基本資料、排位賽與正賽成績排名、單場最速單圈、各圈排名、各圈各車手 pace、pit stop strategy 等
2. 車手車隊分析：排名、單場表現、單季表現、前半後半季表現等
3. 賽道分析：基本資料、歷年最快圈速、逐年分析 podium 與獲勝車隊等

使用者能夠選定其中一種功能，查詢不同年份、不同場次或不同車手車隊的資料，讓整理後的資料容易分析解讀。

4. CRUD  
訪客：僅查詢資料  
使用者：訪客功能、新增自己的車手、車隊，創建比賽等，只有使用者自己才看得到  
管理員：使用者功能、原始資料管理(新增新的比賽結果)、使用者管理

因為資料是真實世界比賽的結果，這裡 CRUD 只能著重在使用者創建自己的車手與車隊、設計一場比賽，而管理員則擁有最高權限，能夠管理原始資料與 Database，還有使用者的手動新增與移除。

## Dataset we use
[Formula 1 World Championship (1950 - 2023)](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020)

## How to use this repo
This project is based on MySQL and flask.  
1. Install python and MySQL.  
2. Clone this repo.
3. Run sql file **create_table.sql** in folder **dataset** (Might need the help from HW0) to create the database.
4. Install python libraries:  
    ```
    pip install flask pymysql
    ```
5. Run the main python file:
    ```
    python3 app.py
    ```
    Open the browser, enter the link showed on the terminal and enjoy the program.