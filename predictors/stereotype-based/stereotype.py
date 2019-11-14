#!/usr/bin/env python

import pandas as pd
import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn import cluster

class Stereo():
    def __init__(self):
        self.gendermap = {"M":1,"F":2}
        return

    def trainModel(self):
        # train model
        users = self.loadUser()
        cates = self.loadCategory()
        sHis = self.loadShopHis()
        userids, traindata = self.geneTrainData(users,cates,sHis)
        traindata = self.preprocess(traindata)
        #print(traindata)
        #TODO: how to choose cluster number
        k_means = cluster.KMeans(n_clusters=3)
        k_means.fit(traindata)
        print(k_means.labels_)
        similiarUsers = {}
        for i,v in enumerate(k_means.labels_):
            if v not in similiarUsers:
                similiarUsers[v] = []
            similiarUsers[v].append(userids[i])
        print(similiarUsers)
        return


    def preprocess(self, x):
        scaler = MinMaxScaler()
        return scaler.fit_transform(x)

    def geneTrainData(self, users, categories, shopHis):
        # generate train data from source dataset
        # train data structure: [
        # [Age, Gender, cate1_shopping_amount,cate2_shopping_amount,...],
        # ]
        userids = users['id']
        x = users[['Sex','YOB']]
        # find all categories
        catemap = {}
        for idx,rec in categories.iterrows():
            catemap[rec['Product']] = rec['Category']
        # history map {userid:{cate1:count}}
        hismap = {}
        cates = list(set(catemap.values()))
        for userid in userids:
            hismap[userid] = {}
            for cate in cates:
                hismap[userid][cate] = 0
        for idx,rec in shopHis.iterrows():
            userid = rec['User']
            cate = catemap[rec['Product']]
            hismap[userid][cate] += 1
        shopCount = []
        for userid in userids:
            userCount = []
            for ct in cates:
                userCount.append(hismap[userid][ct])
            shopCount.append(userCount)
        shopFrame = pd.DataFrame(shopCount, columns = list(cates))
        x = x.join(shopFrame)
        #print(x)
        return userids, x





    def loadShopHis(self):
        # load users' shopping history
        # I think we can just load history of past 6 months in case
        # our data set become very large, and people's interest change overtime
        # I will load all data here for simplicity
        return pd.read_csv("data-gen/out/gen-data-shop.csv")


    def loadUser(self):
        # load user info
        genderLab = lambda x : (self.gendermap.get(x,3) )
        # age converter
        now = datetime.datetime.now()
        ageCal = lambda x : (now.year - int(x))
        return pd.read_csv("data-gen/out/gen-data-user.csv", converters={'Sex':genderLab,'YOB':ageCal})

    def loadCategory(self):
        # load category info
        return pd.read_csv("data-gen/out/gen-data-item-categories.csv")


if __name__ == "__main__":
    s = Stereo()
    s.trainModel()
