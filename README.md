# cov
基于疫情数据爬取
spider.py 进行数据库连接与前端的传输
utils.py 进行数据的保存到库只是百度热词部分
数据更新.py 进行数据的更新和存储
app.py     进行数据的展示利用了flask环境
static     静态文件
templates  html
数据库利用的是mysql


运行步骤：
1.pip install -r requirements.txt
2.先把 数据库.txt 创建好数据  数据库是cov 数据库密码为123456 数据库用户root
3.进行数据爬取存库 运行spider.py 数据更新.py utils.py 
4.进行app.py运行
