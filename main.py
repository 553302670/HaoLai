import asyncio
import tkinter as tk
from tkinter import ttk
import re
import aiohttp
import json

QUERY_URL = "https://zy.xywlapi.cc/lolname?name="
BASE_URL = "https://vn.vmp.cc/shop/shop/getAccount"
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203',
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/json; charset=utf-8',
}


async def query_account_info(session, account):
    async with session.post(QUERY_URL + account, headers=HEADERS) as response:
        if response.headers.get('content-type') == 'text/html; charset=utf-8':
            print('跳过text/html异常响应')
        else:
            if response.status == 200:
                try:
                    data = await response.json()
                    if data.get('message') == '查询成功':
                        return {
                            "qq": data.get("qq"),
                            "name": data.get("name")
                        }
                    else:
                        print('账号：'+account+'----'+data.get('message'))
                except (json.JSONDecodeError, KeyError):
                    print("解析JSON响应或提取数据失败")
            elif response.status == 429:
                print("请求过多，等待5s后继续重试...")
                await asyncio.sleep(5)
                return await query_account_info(session, account)
            else:
                print("请求失败，状态码为：", response.status)

    return None


async def fetch_page(session, page, region):
    region = {'⭐皮肤专区⭐保底400以上': '289317', '⭐比尔吉沃特(网通一区)⭐': '292042', '⭐德玛西亚(网通二区)⭐': '292041',
              '⭐弗雷尔卓德(网通三区)⭐': '292040', '⭐无畏先锋(网通四区)⭐': '292039', '⭐恕瑞玛(网通五区)⭐': '292038',
              '⭐扭曲丛林(网通六区)⭐': '292037', '⭐巨龙之巢(网通七区)⭐': '292036', '⭐男爵领域⭐全网通大区': '289318',
              '⭐艾欧尼亚(电信一区)⭐': '292061', '⭐祖安(电信二区)⭐': '292060', '⭐诺克萨斯(电信三区)⭐': '292059',
              '⭐班德尔城(电信四区)⭐': '292058', '⭐皮尔特沃夫(电信五区)⭐': '292057', '⭐战争学院(电信六区)⭐': '292056',
              '⭐巨神峰(电信七区)⭐': '292055', '⭐雷瑟守备(电信八区)⭐': '292054', '⭐裁决之地(电信九区)⭐': '292053',
              '⭐黑色玫瑰(电信十区)⭐': '292052', '⭐暗影岛(电信十一区)⭐': '292051', '⭐钢铁烈阳(电信十二区)⭐': '292050',
              '⭐水晶之痕(电信十三区)⭐': '292049', '⭐均衡教派(电信十四区)⭐': '292048', '⭐影流(电信十五区)⭐': '292047',
              '⭐守望之海(电信十六区)⭐': '292046', '⭐征服之海(电信十七区)⭐': '292045',
              '⭐卡拉曼达(电信十八区)⭐': '292044',
              '⭐皮城警备(电信十九区)⭐': '292043', }[combo.get()]
    payload = {
        'goodsid': region,
        'page': str(page),
        'userid': '1115',
        'type': 'new'
    }

    async with session.post(BASE_URL, headers=HEADER, data=payload) as response:
        data = await response.json()
        return [f"{item['number']['3']}----{item['number']['4']}" for item in data["data"]]


async def fetch_account_data(region, loop_times):
    async with aiohttp.ClientSession() as session:
        name_list = []
        account_list = []

        tasks = [fetch_page(session, page, region) for page in range(1, loop_times + 1)]
        results = await asyncio.gather(*tasks)

        for names in results:
            name_list.extend(names)

        tasks = [query_account_info(session, re.findall(r'^([^-\-]+)', item)[0]) for item in name_list]
        account_list = [info for info in await asyncio.gather(*tasks) if info]

        return name_list, account_list


def save_account_data(name_list, account_list):
    file_path = 'account.txt'
    account_data = [f"{info['qq']}----{name}" for name in name_list for info in account_list if
                    info['name'] == name.split("----")[0]]

    try:
        with open(file_path, "w") as file:
            file.write("\n".join(account_data))
            print("可用数据已保存到account.txt文件中，请尝试登陆吧！")
    except IOError as e:
        print(f"写入文件时出错：{str(e)}")


def get_data():
    region = combo.get()

    loop_times = int(entry.get())

    try:
        name_list, account_list = asyncio.run(fetch_account_data(region, loop_times))
        save_account_data(name_list, account_list)
    except Exception as e:
        print(f"发生错误：{str(e)}")
    else:
        print("数据获取完成。")


root = tk.Tk()
root.title("号来")
root.geometry("300x150")

# 屏幕局中
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
root.geometry(f'+{(screenwidth - root.winfo_reqwidth()) // 2}+{(screenheight - root.winfo_reqheight()) // 2}')

combo_frame = ttk.Frame(root)
combo_frame.pack(pady=20)
ttk.Label(combo_frame, text="借号大区:").pack(side=tk.LEFT, padx=5)
combo = ttk.Combobox(combo_frame, values=['⭐皮肤专区⭐保底400以上', '⭐比尔吉沃特(网通一区)⭐', '⭐德玛西亚(网通二区)⭐',
                                          '⭐弗雷尔卓德(网通三区)⭐', '⭐无畏先锋(网通四区)⭐', '⭐恕瑞玛(网通五区)⭐',
                                          '⭐扭曲丛林(网通六区)⭐', '⭐巨龙之巢(网通七区)⭐', '⭐男爵领域⭐全网通大区',
                                          '⭐艾欧尼亚(电信一区)⭐', '⭐祖安(电信二区)⭐', '⭐诺克萨斯(电信三区)⭐',
                                          '⭐班德尔城(电信四区)⭐',
                                          '⭐皮尔特沃夫(电信五区)⭐',
                                          '⭐战争学院(电信六区)⭐', '⭐巨神峰(电信七区)⭐', '⭐雷瑟守备(电信八区)⭐',
                                          '⭐裁决之地(电信九区)⭐',
                                          '⭐黑色玫瑰(电信十区)⭐',
                                          '⭐暗影岛(电信十一区)⭐', '⭐钢铁烈阳(电信十二区)⭐', '⭐水晶之痕(电信十三区)⭐',
                                          '⭐均衡教派(电信十四区)⭐',
                                          '⭐影流(电信十五区)⭐', '⭐守望之海(电信十六区)⭐', '⭐征服之海(电信十七区)⭐',
                                          '⭐卡拉曼达(电信十八区)⭐',
                                          '⭐皮城警备(电信十九区)⭐'], width=22)
combo.current(0)
combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

entry_frame = ttk.Frame(root)
entry_frame.pack(pady=10)
ttk.Label(entry_frame, text="页面数量:").pack(side=tk.LEFT, padx=5)
entry = tk.Entry(entry_frame, width=25)
entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

button = tk.Button(root, text="开始借号", command=get_data)
button.pack(pady=10)

root.mainloop()
