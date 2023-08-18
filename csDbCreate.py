import sqlite3
import numpy as np
def createTable(list,tableName):

    connection = sqlite3.connect("csgoData.db")
    cursor = connection.cursor()
    
    sqlQueryCreateTable = "CREATE TABLE IF NOT EXISTS "+ tableName +"( itemID INTEGER PRIMARY KEY,linkPrice TEXT, linkDailySell TEXT, name TEXT, quantity INTEGER, purchasePrice REAL, currentPrice REAL, volumeMarket INTEGER, dailySell INTEGER)"
    cursor.execute(sqlQueryCreateTable)

    sqlQueryInsertInto = "INSERT INTO "+ tableName +" (linkPrice, linkDailySell, name, quantity, purchasePrice) VALUES (?,?,?,?,?)"
    cursor.executemany(sqlQueryInsertInto,list)
    connection.commit()
    
    # for row in cursor.execute("SELECT * FROM caseTable"):
    #      print(row)
    #      print(type(row))

    connection.close()


spaceButton = "%20"
iButton = "%26"
verticalBarButton = "%7C"
openBracketButton = "%28"
closeBracketButton = "%29"

def createLinks(myList):

    myArray = np.array(myList,dtype="object")

    for x in range(len(myArray)):

        myArray[x][0]= linkPrice+myArray[x][2]
        myArray[x][1]= linkDailySell+myArray[x][2]

        nameFiltr = myArray[x][2]
        if spaceButton in nameFiltr:
            nameFiltr = nameFiltr.replace(spaceButton," ")
        if iButton in nameFiltr:
            nameFiltr = nameFiltr.replace(iButton,"and")
        if verticalBarButton in nameFiltr:
            nameFiltr = nameFiltr.replace(verticalBarButton,"|")
        if openBracketButton in nameFiltr:
            nameFiltr = nameFiltr.replace(openBracketButton,"(")
        if closeBracketButton in nameFiltr:
            nameFiltr = nameFiltr.replace(closeBracketButton,")")  
        myArray[x][2]=nameFiltr


    return myArray.tolist()

    
#lista: ID, linkPrice, linkDailySell, name, quantity, purchasePrice, currentPrice, volumeMarket, dailySell
# %20
# current currency is zloty
linkPrice = "https://steamcommunity.com/market/priceoverview/?appid=730&currency=6&market_hash_name="
linkDailySell = "https://steamcommunity.com/market/pricehistory/?appid=730&market_hash_name="
# ("","","",,),
case_list= [

    ("","","Clutch%20Case",10,1.86),
    ("","","Danger%20Zone%20Case",1,0.03)

    ]
souvenir_list= [
    ("","","Stockholm%202021%20Dust%20II%20Souvenir%20Package",1,19.5),
    ("","","Paris%202023%20Vertigo%20Souvenir%20Package",5,11.6)

    ]
patch_list= [

    ("","","Patch%20%7C%20FURIA%20%28Gold%29%20%7C%20Stockholm%202021",1,28.92),
    ("","","Patch%20%7C%20Entropiq%20%28Gold%29%20%7C%20Stockholm%202021",1,27.50)

    ]
capsule_list= [

    ("","","Paris%202023%20Contenders%20Autograph%20Capsule",13,1.05),
    ("","","Paris%202023%20Legends%20Autograph%20Capsule",15,1.05)

    ]
goldSticker_list= [

    ("","","Sticker%20%7C%20Sprout%20Esports%20%28Gold%29%20%7C%20Rio%202022",1,37.98),
    ("","","Sticker%20%7C%20Fnatic%20%28Gold%29%20%7C%20Rio%202022",1,26.80) 

    ]
foilSticker_list= [

    ("","","Sticker%20%7C%20Team%20Liquid%20%28Foil%29%20%7C%20Stockholm%202021",1,10.25),
    ("","","Sticker%20%7C%20Gambit%20Gaming%20%28Foil%29%20%7C%20Stockholm%202021",2,7.97)

    ]
holoSticker_list= [

    ("","","Sticker%20%7C%20KRIMZ%20(Holo)%20%7C%20Paris%202023",2,3.74),
    ("","","Sticker%20%7C%20Lucaozy%20(Holo)%20%7C%20Paris%202023",3,9.75), 
    


    ]
glitterSticker_list= [

    ("","","Sticker%20%7C%20Eternal%20Fire%20%28Glitter%29%20%7C%20Antwerp%202022",2,4.21),
    ("","","Sticker%20%7C%20Bad%20News%20Eagles%20%28Glitter%29%20%7C%20Antwerp%202022",5,1.81),
    ("","","Sticker%20%7C%20Cloud9%20%28Glitter%29%20%7C%20Antwerp%202022",1,7.98)


    ]
paperSticker_list= [
     ("","","Sticker%20%7C%20TYLOO%20%7C%202020%20RMR",50,0.63),
     ("","","Sticker%20%7C%20TeSeS%20%7C%20Paris%202023",10,0.03),
     ("","","Sticker%20%7C%20WOOD7%20%7C%20Paris%202023",8,0.07),
     ("","","Sticker%20%7C%20INS%20%7C%20Paris%202023",35,0.03),
     ("","","Sticker%20%7C%20aliStair%20%7C%20Paris%202023",25,0.03)

     ]


#print(createLinks(case_list).tolist())
case_listDB = createLinks(case_list)
createTable(case_listDB,"caseTable")

souvenir_listDB = createLinks(souvenir_list)
createTable(souvenir_listDB,"souvenirTable")

patch_listDB = createLinks(patch_list)
createTable(patch_listDB,"patchTable")

capsule_listDB = createLinks(capsule_list)
createTable(capsule_listDB,"capsuleTable")

goldSticker_listDB = createLinks(goldSticker_list)
createTable(goldSticker_listDB,"goldStickerTable")

foilSticker_listDB = createLinks(foilSticker_list)
createTable(foilSticker_listDB,"foilStickerTable")

holoSticker_listDB = createLinks(holoSticker_list)
createTable(holoSticker_listDB,"holoStickerTable")

glitterSticker_listDB = createLinks(glitterSticker_list)
createTable(glitterSticker_listDB,"glitterStickerTable")

paperSticker_listDB = createLinks(paperSticker_list)
createTable(paperSticker_listDB,"paperStickerTable")
