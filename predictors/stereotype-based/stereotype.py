#!/usr/bin/env python

import pandas as pd
import datetime

class Stereo():
    def __init__(self):
        self.gendermap = {"M":1,"F":2}
        return

    def trainModel(self):
        # train model
        users = self.loadUser()
        cates = self.loadCategory()
        sHis = self.loadShopHis()
        traindata = self.geneTrainData(users,cates,sHis)
        return


    def geneTrainData(self, users, categories, shopHis):
        # generate train data from source dataset
        # train data structure: [
        # [Age, Gender, cate1_shopping_amount,cate2_shopping_amount,...],
        # ]
        x = []
        userid = []
        usernum = len(users)
        for userid in users['id']:
            userid.append(i)
            X
        print(x)

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
