import math
import pandas as pd
#读取数据
data = pd.read_csv('课程配套数据/meal_order_detail.csv', usecols=['dishes_name', 'order_id', 'emp_id'])
data1 = pd.read_csv('课程配套数据/meal_order_info.csv', usecols=['order_status', 'info_id'])
#删除\r\n字符
data = data.replace('\r', '', regex=True).replace('\n', '', regex=True)
###数据预处理
#去除'白饭/小碗'的数据
data2 = data.drop(data.loc[(data['dishes_name'] == '白饭/小碗')].index, axis=0)
#去除'白饭/大碗'的数据
data2.drop(data2.loc[(data2['dishes_name'] == '白饭/大碗')].index, inplace=True, axis=0)

#寻找订单状态不为1的索引
b = data1.loc[(data1['order_status'] != 1)].index
#寻找订单状态不为1的订单ID
b1 = data1['info_id'][b]
#删除订单状态不为1的数据
for i in b1:
    a = data2.drop(data2.loc[(data2['order_id'] == i)].index, axis=0)

##删除点餐数量小于3的用户
n1 = {}   #创建用户ID与点餐数量的字典
for i in a['emp_id']:
    if i not in n1:
        n1[i] = 1
    else:
        n1[i] += 1
n2 = []
for i in n1:
    if n1[i] < 3:
        n2.append(i)
for i in n2:
    a = a.drop(a.loc[(a['emp_id'] == i)].index, axis=0)
    del n1[i]

#删除订单ID在订单详情表有但订单信息表没有的数据
# a1 = []; a2 = []; a3 =[]
# for i in a['order_id']:
#     if i not in a1:
#         a1.append(i)
# for i in data1['info_id']:
#     if i not in a2:
#         a2.append(i)
# for i in a1:
#     if i not in a2:
#         a3.append(i)
#计算发现a3为空，即不存在订单ID在订单详情表有但订单信息表没有的数据

#删除 order_id的列
a = a.drop(labels='order_id', axis=1)#至此得到a为菜品名称和客户ID两列数据

###创建用户--菜品二元矩阵
n1 = []
for i in a['emp_id']:
    if i not in n1:
        n1.append(i)
n = len(n1)  #用户的总数量
k1 = math.ceil(0.8*n)
#根据客户人数来划分训练集和测试集，取80%作为训练数据(向上取整) %20作为测试数据
j = 1;train = [];test = [];b = a
for i in n1:
    if j <= k1:
        train.append(i)
    else:
        test.append(i)
    j += 1
for i in train:
    a = a.drop(a.loc[(a['emp_id'] == i)].index, axis=0)
for i in test:
    b = b.drop(b.loc[(b['emp_id'] == i)].index, axis=0)
Train = b; Test = a   #至此得到的训练数据和测试数据的Size分别为:(8365, 2) (1148, 2)

#将训练数据转成客户-菜品的二元矩阵
train1 = []
for i in Train['dishes_name']:
    if i not in train1:
        train1.append(i)
data3 = pd.DataFrame(data=0, columns=train1, index=train)

for i in Train['emp_id']:
    b1 = Train.loc[(Train['emp_id'] == i)].index
    j = Train['dishes_name'][b1]
    data3.loc[i][j] = 1
#得到的用户--菜品二元矩阵(data3)的Size为（375， 143）

#计算各个菜品之间的相似度
data2 = pd.DataFrame(data=0.0000, columns=data3.columns, index=data3.columns)
for i in data3.columns:
    for j in data3.columns:
        if i == j:
            data2[i][j] = 0
        else:
            n1 = data3[i].sum()+data3[j].sum()
            N1 = data3.loc[(data3[i] == 1)].index
            N2 = data3.loc[(data3[j] == 1)].index
            n3 = 0
            for k in N1:
                if k in N2:
                    n3 += 1
            nn = round(n3/(n1-n3), 4)
            data2[i][j] = nn
#得到菜品与菜品之间的相似度data2(143*143)

#将测试数据转成字典形式，用cs表示
cs = {}
ceshi = []
for i in Test['emp_id']:
    if i not in ceshi:
        ceshi.append(i)
for i in ceshi:
    b = Test.loc[(Test['emp_id'] == i)].index
    j = Test['dishes_name'][b]
    if i not in cs:
        cs[i] = j

#找到相似度最高的一道菜
data2 = data2.idxmax()

#对客户所点的每一道菜,推荐与其相似度最高的一道菜，用aa表示
aa = {}
for i in cs:
    aa[i] = []
    for j in cs[i]:
        aa[i].append(data2[j])

#计算准确率
j = 0
n = 0
for i in aa:
    for k in aa[i]:
        for j1 in cs[i]:
            if k == j1:
                n += 1
        j += 1
#输出结果
print('正确推荐的菜品数:', n, '所有推荐菜品数:', j, '准确率:', n/j)




