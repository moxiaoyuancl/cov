#导入模块
import pymysql
import time
import json
import requests
import traceback
import sys


# 历史数据爬取
def get_history_data():
    url = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_other"
    headers = {
        'url-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    r = requests.get(url, headers)
    c = r.text

    c = json.loads(r.text)
    data_all = json.loads(c['data'])
    history = {}  # 历史数据
    for i in data_all['chinaDayList']:
        ds = "2020." + i["date"]  # 获取日期
        tup = time.strptime(ds, "%Y.%m.%d")
        ds = time.strftime("%Y-%m-%d", tup)  # 改变时间格式，不然插入数据库会报错，数据库是datetime类型
        confirm = i["confirm"]
        suspect = i["suspect"]
        heal = i["heal"]
        dead = i["dead"]
        history[ds] = {"confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead}
    for i in data_all["chinaDayAddList"]:
        ds = "2020." + i["date"]  # 获取日期
        tup = time.strptime(ds, "%Y.%m.%d")
        ds = time.strftime("%Y-%m-%d", tup)  # 改变时间格式，不然插入数据库会报错，数据库是datetime类型
        confirm = i["confirm"]
        suspect = i["suspect"]
        heal = i["heal"]
        dead = i["dead"]
        history[ds].update({"confirm_add": confirm, "suspect_add": suspect, "heal_add": heal, "dead_add": dead})
        # 上面是获取增加的数据整合
    return (history)


# 列表数据爬取
def get_details_data():
    url = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5"
    headers = {
        'url-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    r = requests.get(url, headers)
    c = r.text

    c = json.loads(r.text)
    data_all = json.loads(c['data'])
    details = []  # 当日详细数据
    update_time = data_all["lastUpdateTime"]
    data_country = data_all['areaTree']  # 25个国家
    data_province = data_country[0]["children"]  # 中国各省
    for pro_infos in data_province:
        province = pro_infos["name"]
        for city_infos in pro_infos["children"]:
            city = city_infos["name"]
            confirm = city_infos["total"]["confirm"]
            confirm_add = city_infos["today"]["confirm"]
            heal = city_infos["total"]["heal"]
            dead = city_infos["total"]["dead"]
            details.append([update_time, province, city, confirm, confirm_add, heal, dead])
    return details



#pymysql的简单的使用
#建立连接
def get_conn():
    conn = pymysql.connect('localhost','root','123456','cov')
#创建游标，默认是元组型
    cursor=conn.cursor()
    return conn,cursor
#conn.commit()#提交事务
def close_conn(conn,cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# 更新数据库里的数据
def update_details():
    """
    更新 details 表
    :return:
    """
    cursor = None
    conn = None
    try:
        li = get_details_data()  #  0 是历史数据字典,1 最新详细数据列表
        conn, cursor = get_conn()
        sql = "insert into details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
        sql_query = 'select %s=(select update_time from details order by id desc limit 1)' #对比当前最大时间戳
        cursor.execute(sql_query,li[0][0])
        if not cursor.fetchone()[0]:
            print(f"{time.asctime()}开始更新最新数据")
            for item in li:
                cursor.execute(sql, item)
            conn.commit()  # 提交事务 update delete insert操作
            print(f"{time.asctime()}更新最新数据完毕")
        else:
            print(f"{time.asctime()}已是最新数据！")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


#插入历史数据

def insert_history():
    cursor=None
    conn=None
    try:
        dic=get_history_data()#是历史数据字典 1最新详细数据列表
        print(f"{time.asctime()}开始插入历史数据 ")
        conn,cursor =get_conn()
        sql="insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for k,v in dic.items():
            cursor.execute(sql,[k,v.get("confirm"),v.get("confirm_add"),v.get("suspect"),v.get("suspect_add"),
                               v.get("heal"),v.get("heal_add"),v.get("dead"),v.get("dead_add")])
        conn.commit()
        print(f"{time.asctime()}插入历史数据完华 ")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn,cursor)

        # 更新历史数据


# 更新历史数据
def update_history():
    cursor = None
    conn = None
    try:
        dic = get_history_data()  # 是历史数据字典 1最新详细数据列表
        print(f"{time.asctime()}开始更新历史数据 ")
        conn, cursor = get_conn()

        sql = "insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        sql_query = "select confirm from history where ds=%s"
        for k, v in dic.items():
            if not cursor.execute(sql_query, k):
                cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"), v.get("suspect"), v.get("suspect_add"),
                                     v.get("heal"), v.get("heal_add"), v.get("dead"), v.get("dead_add")])

        print(f"{time.asctime()}插入历史数据完华 ")
        conn.commit()

    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)

get_details_data()
get_history_data()
update_details()
update_history()
insert_history
