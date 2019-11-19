#!/usr/bin/env python

import pandas as pd
import datetime
import operator
import json
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn import cluster

class ItemsHis():
    def __init__(self, itemid, times):
        self.id = itemid
        self.times = times

class Stereo():
    def __init__(self):
        self.gendermap = {"M":1,"F":2}
        self.modelmap = None
        self.modelf = "stereotype.model"
        return

    def trainModel(self):
        # train model
        users = self.loadUser()
        cates = self.loadCategory()
        sHis = self.loadShopHis()
        userids, traindata = self.geneTrainData(users,cates,sHis)
        traindata = self.preprocess(traindata)
        #TODO: how to choose cluster number
        numberOfUser = len(users)
        print(numberOfUser)
        good_n_cluster = 0
        good_n_cluster_score = 0
        start = int(numberOfUser / 50)
        if start < 2:
            start = 2
        end = int(numberOfUser / 5)
        for n_clusters in range(start,end):
            k_means = cluster.KMeans(n_clusters=n_clusters)
            cluster_labels = k_means.fit_predict(traindata)
            silhouette_avg = silhouette_score(traindata, cluster_labels)
            if silhouette_avg > good_n_cluster_score:
                good_n_cluster = n_clusters
                good_n_cluster_score = silhouette_avg
            print("For n_clusters =", n_clusters,
                "The average silhouette_score is :", silhouette_avg)

        print("ideal number of cluster is", good_n_cluster)
        k_means = cluster.KMeans(n_clusters=good_n_cluster)
        cluster_labels = k_means.fit_predict(traindata)
        print(k_means.labels_)
        similiarUsers = {}
        for i,v in enumerate(k_means.labels_):
            if v not in similiarUsers:
                similiarUsers[int(v)] = []
            similiarUsers[int(v)].append(int(userids[i]))
        with open(self.modelf,"w") as f:
            f.write(json.dumps(similiarUsers))
        self.modelmap = similiarUsers
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

    def loadModel(self):
        with open(self.modelf, "r") as f:
            self.modelmap = json.loads(f.read())
        print(self.modelmap)

    def getItemMap(self):
        return

    def predict(self, userid):
        groupids = None
        for k in self.modelmap:
            if userid in self.modelmap[k]:
                groupids = self.modelmap[k]
                break
        print(groupids)
        if groupids == None:
            return []
        histories = self.loadShopHis()
        needhis = histories[["User","Product"]]
        recommend = {}
        for uid in groupids:
            cns = needhis[needhis.User == uid]["Product"].value_counts()
            for idx,im in cns.items():
                if idx not in recommend:
                    recommend[int(idx)] = 0
                recommend[int(idx)] += int(im)
        sortedrec = sorted(recommend.items(), key=operator.itemgetter(1),reverse=True)
        bought = needhis[needhis.User == userid]["Product"].unique().tolist()
        predictRes = []
        for (pid, time) in sortedrec:
            if pid not in bought:
                predictRes.append(pid)
                if len(predictRes) > 10:
                    return predictRes
        return predictRes

    
        

if __name__ == "__main__":
    s = Stereo()
    s.trainModel()
    #s.loadModel()
    #print(s.predict(10014))
