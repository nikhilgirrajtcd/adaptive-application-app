import pandas as pd
import numpy as np
import scipy.sparse as sparse
from faker import Faker
from datetime import datetime
import random as rd
# import pydbgen
# from pydbgen import pydbgen
# myDB=pydbgen.pydb()

def genUsers(count=30):
    users = pd.DataFrame()
    fake = Faker()
    nameFuncs = [fake.name_female, fake.name_male, fake.name]
    sexes = ['F', 'M', 'O']
    currentYear = datetime.now().year
    users['id'] = [i for i in range(10000, 10000 + count)]
    users['Sex'] = [sexes[i%7%5%3] for i in range(0,count)]
    users['Name'] = [nameFuncs[i%7%5%3]() for i in range(0,count)]
    users['YOB'] = currentYear - np.random.randint(18, 65 + 1, count)
    users['Household'] = np.random.randint(1, 10 + 1, count)
    return users

def genProductsWithSizes():
    items = np.array([
                ['Milk', 'Dairy'], 
                ['Soap', 'Personal Care'], 
                ['Shampoo', 'Personal Care'], 
                ['Butter', 'Dairy'], 
                ['Bread', 'Dairy'], 
                ['Sauce', 'Food C'], 
                ['Chicken', 'Food A'], 
                ['Beef', 'Food A'], 
                ['Coffee', 'Beverages'], 
                ['Sugar', 'Food B'],
                ['Cooking Oil', 'Food C'],
                ['Rice', 'Food C'],
                ['Freshener', 'Cleaning'],
                ['Bleach', 'Cleaning'],
                ['Cookies', 'Snacks'],
                ['Chips', 'Snacks']                
    ])
    countProducts = len(items)
    
    itemSizes = ['S', 'M', 'L']
    dfItemCat = pd.DataFrame()
    dfItemCat['Item'] = items[:, 0]
    dfItemCat['Category'] = items[:, 1]
    dfItemCat['Product'] = np.arange(7000, 7000 + dfItemCat.shape[0])
    
    dfItemSizes = pd.DataFrame({
        'Product': list(dfItemCat.Product.values) * 3,
        'Size': [itemSizes[i] for i in np.sort(list(list(np.arange(0, len(itemSizes))) * countProducts))] ,
        'ItemSizeId': np.arange(5001, 5001 + countProducts * len(itemSizes), 1)
    })
    
    # all products available at every store with price difference (base) of random percentage, larger sizes are available at 130 to 180 percent price of the smaller sizes on average
    stores = ['Tesco', 'Lidl', 'Spar', 'Aldi', 'M&S']
    store_item_sizeMap = sparse.rand(len(stores), dfItemSizes.shape[0], density=0.8, format='csr', random_state=66, dtype=bool).A
    
    productbaseprice = [np.random.uniform(0.5, 4.5) for item in items[:, 0]]
    pricesPerSize = [(productbaseprice[i] + j * productbaseprice[i] * np.random.uniform(0.3, 0.8)) for i in range(len(productbaseprice)) for j in range(len(itemSizes))]
    dfStorePrices = pd.DataFrame(columns=['Store', 'Product', 'Size', 'Price'])
    # storeProd = np.array([[store, prod, itemSizes[isize], ] 
    for isize in range(len(itemSizes)):
        size = itemSizes[isize]
        for iprod in range(len(dfItemCat.Product.values)):
            prod = dfItemSizes['Product'].values[iprod]
            refProdPrice = productbaseprice[iprod] + isize * productbaseprice[iprod] * np.random.uniform(0.3, 0.8)
            for store in stores:
                prodPriceAtStore = np.random.uniform(0.7, 1.3) * refProdPrice
                dfStorePrices.loc[dfStorePrices.shape[0]] = [store, prod, size, prodPriceAtStore] 
                    
    # dfStorePrices['Store'] = storeProd[:, 0]
    # dfStorePrices['Product'] = storeProd[:, 1]
    #pd.DataFrame({ 'Store': list(stores) * dfItemSizes.shape[0], 'Product': list(dfItemSizes['Product']) * len(stores) })
    # dfStorePrices['Price'] = pricesPerSize
    dfStorePrices['IsAvailableEver'] = np.array(store_item_sizeMap).flatten()
    
    
    return dfItemCat, dfStorePrices, dfItemSizes

def getGeneralRevisitTendencyForUsers(users):
    return np.random.normal(7, 2.5, len(users)).astype(int)

def PurchaseDatesByProductForUser(user, householdSize, revisitTendency, items, stores):
    # assign a normally distributed re-purchase day distance to the user np.random.normal
    # assign a lazyness probability to the user np.random.random
    # assign a product affinity to the user np.random.dirichlet(np.ones(10),size=1)
    # assign a store affinity (probability) to the user  np.random.dirichlet(np.ones(10),size=1)
    # visit to a store is random based on numpy.random.choice
    # purchase of products on a visit is product affinity * household size
    days = 500
    ## this data will be created for 500 days (NOT 500 store visits)
    repurchase = list()
    lazyness = np.random.uniform(1, revisitTendency/2) 
    for i in range(0, 500, revisitTendency):
        realVisitDay = np.random.choice([i, i, i, i+lazyness, i+lazyness, i+2*lazyness, 0], 1)[0]
        if(realVisitDay == 0): 
            continue
        repurchase.append(int(realVisitDay))
        
    productAffinity = rd.sample(list(items), k=np.random.randint(5, len(items)))
    storeAffinity = np.random.dirichlet(np.ones(len(stores)), size=1)[0]
    visits=list()
    for r in repurchase:
        storeVisited = np.random.choice(a=stores, size=1, p=storeAffinity)[0]
        # buy big sizes if household is big, later
        purchasesThisVisit = GetItemStoreSize(productAffinity, householdSize*revisitTendency, storeVisited)
        for p in purchasesThisVisit:
            visits.append((user, r, storeVisited, p[0], p[1], p[2]))
        
    return visits



def GetItemStoreSize(products, householdxRevisitTendency, store):
    global dfStorePrices
    dfFiltered = dfStorePrices[(dfStorePrices.Product.isin(products)) & (dfStorePrices.Store == store) & (dfStorePrices.IsAvailableEver == True)]
    ret = list()
    for prod in products:
        prodFilter = dfFiltered.Product == prod
        chosensize = np.random.choice(dfFiltered[prodFilter].Size.values, 1)[0]
        row = dfFiltered[(prodFilter) & (dfFiltered.Size == chosensize)]
        ret.append((prod, chosensize, row.Price.values[0]))

    return ret



dfUsers = genUsers(50)
dfItemCat, dfStorePrices, dfItemSizes = genProductsWithSizes()

    
revisitTendencies = np.random.normal(7, 2.5, dfUsers.shape[0])    
all = list()
for i, user in dfUsers.iterrows():
    all.append(PurchaseDatesByProductForUser(user.id, revisitTendencies[i], 3, dfItemCat.Product.values, list(set(dfStorePrices.Store.values))))


dfFinal = pd.DataFrame(columns=['User', 'PurchaseDay', 'Store', 'Product', 'Size', 'Price'])
for item in all:
    for item2 in item:
        dfFinal.loc[dfFinal.shape[0]+1,:] = list(item2)


dfFinal.to_csv(r'out\gen-data-shop.csv', index=False)
dfUsers.to_csv(r'out\gen-data-user.csv', index=False)
dfItemCat.to_csv(r'out\gen-data-item-categories.csv', index=False)
dfStorePrices.to_csv(r'out\gen-data-store-prices-sizes.csv', index=False)
dfItemSizes.to_csv(r'out\gen-data-item-sizes.csv', index=False)