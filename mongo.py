import pymongo
import matplotlib.pyplot as plt

def read_classes(classes_path):
    with open(classes_path) as f:
        class_names = f.readlines()
    class_names = [c.strip() for c in class_names]
    return class_names


def conDB():
    conn = pymongo.MongoClient("localhost",27017)
    return conn.get_database("Detection")
def createDatabase():
    db = conDB()
    Class =read_classes("./model_data/coco_classes.txt")
    try:
        db.Classes.drop()
    except: 1+1
    for i in Class:
        db.Classes.insert({"ObjectName":i,"no":0})

def increment(conn,key): #conn.get_database("Detection")
    db = conn
    return db.Classes.update_one({'ObjectName': key}, {'$inc': {'no': 1}})

def result(conn,lim=10):
    all = list(conn.Classes.find({}, {'_id': False}).sort([('no',pymongo.DESCENDING)]).limit(lim))
    print(list(all))
    indexes = list()
    val = list()
    outText = ""
    for i in  range(len(all)):
        if all[i].get("ObjectName")==None:continue
        try:

            indexes.append(all[i].get("ObjectName"))
            val.append(all[i].get("no"))

            outText = outText + "{0} : {1}\n".format(all[i].get("ObjectName"), all[i].get("no"))
        except:
            continue

    plt.title(s="Result")
    plt.xlabel("Classes")
    plt.ylabel("Counts")
    print (outText)
    plt.bar(indexes,val, color='g')
    plt.text(x=.99,y=.5,s=outText, wrap=True)
    return plt
if __name__ == '__main__':
   # createDatabase()
    createDatabase()
    collect =conDB()

