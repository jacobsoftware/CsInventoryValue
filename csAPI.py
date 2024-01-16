import json
import requests
import numpy as np
import sqlite3
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
from datetime import datetime
from pprint import pprint
import sys
import pandas as pd


requestCounter=0
commaSign = ","
errorCounter = 0
arrayOfErrors = np.array([])
currentTable = ""
currentRowInSheet = 3
timeAddedOnGS = False
responseFromServer =  ""
wait = 0
sumarryRow = 3


# google sheets variables
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'
SAMPLE_SPREADSHEET_ID = ''#here u need put spreadsheet id
creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets() 


# reading steam API from endpoints that we have in our database
def readFromAPI(url):

# There is not supposed to be try and expect cuz we need it in outer function xd
        
    try:
        
        global requestCounter
        global responseFromServer

        requestCounter = requestCounter + 1
        print(requestCounter)

        response = requests.get(url)
        responseFromServer = str(response)
        print(url," ",response)

        jsonObject = response.json()
        stringObject = json.dumps(jsonObject, ensure_ascii=False)
        string = json.loads(stringObject)

        return string
    
    except requests.ConnectionError as error:
        print(error)


# Currently not used
def addIndexesArray(array):
    for x in range(len(array)):
        array[x,0]=x+1

# Read table from database that contains: links, names of items we got, price when we bought them and quantity
def readTable(nameTable):
    global currentTable
    currentTable = nameTable
    sqlQueryReadTable= "SELECT * FROM "+nameTable

    connection = sqlite3.connect("csgoData.db")
    cursor = connection.cursor()
    cursor.execute(sqlQueryReadTable)
    results = cursor.fetchall()
    connection.close()
    return results

# Adding data from steam API to list
def addDataFromAPI(myList):
    myArray = np.array(myList,dtype="object")
    
# Here is supposed to be while loop cuz in for loop u can't affect on iteration number ( it's when we can't get response from server - 503 server reponse)
    for row in range(len(myArray)):
        try:
            apiDict1 = readFromAPI(myArray[row][1])
            
            varPrice = apiDict1["lowest_price"].replace(",",".")
            varPrice = varPrice.replace("zł","")
            myArray[row][6]=varPrice

            
            if "volume" in apiDict1:
                print("Wartosc: ",apiDict1["lowest_price"]," Ilość sprzedanych: ",apiDict1["volume"])
                
                if commaSign in apiDict1["volume"]:

                    varVolume = apiDict1["volume"].replace(",","")
                    myArray[row][7]=varVolume

                else:

                    myArray[row][7]=apiDict1["volume"]
            else:

                myArray[row][7]=0
                


            time.sleep(3)
            
        except Exception as e: 

            logging.error('Valve why?: '+ str(e))

            global errorCounter
            global arrayOfErrors
            global responseFromServer
            global wait
            
            if("429" in responseFromServer):
                print("Server banned us, program shutdown")
                sys.exit()
            elif("503" in responseFromServer):
                #ask again                       
                if wait<=9:
                    wait = wait +3
                    print("Row before: ", row)
                    row=row-1
                    print("Row after: ", row)

                else:
                    wait=0

                time.sleep(wait)



            arrayOfErrors = np.append(arrayOfErrors,[requestCounter,myArray[row][3]])            
            errorCounter = errorCounter +1

            time.sleep(3)
    #Global summary: cases, papers, glitter etc.
    makeSummary(myArray)
    if "2020 RMR" in myArray[0][3] or "Stockholm 2021" in myArray[0][3] or "Antwerp 2022" in    myArray[0][3] or "Rio 2022" in myArray[0][3]:
        # summary of every event
        putOnSheet(sumValues(myArray),"sumarry")

    return myArray.tolist()
#global summary
def makeSummary(array):
    
    totalCost, totalValue = 0, 0
    for x in range(len(array)):
        
        totalCost = totalCost + (float(array[x][5])*float(array[x][4]))
        if(array[x][6] is not None):
            totalValue = totalValue + (float(array[x][6])*float(array[x][4]))
        else:
            totalValue = totalValue + (float(array[x][5])*float(array[x][4]))

    totalCost = round(totalCost,2)
    totalValue = round(totalValue,2)
    profit = totalValue - totalCost
    roi = round(profit/totalCost,2)

    currentList = [(totalCost,totalValue,profit,roi)]
    putOnSheet(currentList,"sumarryV2")
    global sumarryRow
    sumarryRow=sumarryRow+1


# Summing all values of specific item type (paper, glitter holos etc.), we are doing this to have overview (summary in google sheets)

# The whole function is not necessary, better option might be put everything in sql database and sum everything by event name

def sumValues(myArray):
    # name, quantity, volume market, cost, current total value, ROI 

    global currentTable
    currentTable = currentTable.replace("Table","")

    Rmr2020 = "2020 RMR "+ currentTable
    Stockholm2021 = "Stockholm 2021 "+currentTable
    Antwerp2022 = "Antwerp 2022 " + currentTable
    Rio2022 = "Rio 2022 "+currentTable
    Paris2023 = "Paris 2023 "+ currentTable
# U can't use in numpy arrays multiple data types (arrays built in python can have different data types) soo better option for this might be dataframe from pandas
    arraySum = np.array([[Rmr2020,0,0,0.,0.,0.,0.],[Stockholm2021,0,0,0.,0.,0.,0.],
                         [Antwerp2022,0,0,0.,0.,0.,0.],[Rio2022,0,0,0.,0.,0.,0.],
                         [Paris2023,0,0,0.,0.,0.,0.]],dtype=object)

    for row in range(len(myArray)):
        if myArray[row][7] is not None:
            quantity = float(myArray[row][4])
            volumeMarket = float(myArray[row][7])
            purchasePrice = float(myArray[row][5])
            currentPrice = float(myArray[row][6])


            if "2020 RMR" in myArray[row][3]:
                #quantity
                arraySum[0][1]= arraySum[0][1]+quantity
                #market volume
                arraySum[0][2]= arraySum[0][2]+volumeMarket
                #cost
                arraySum[0][3]= arraySum[0][3]+purchasePrice*quantity
                #current value
                arraySum[0][4]= arraySum[0][4]+currentPrice*quantity
                

            elif "Stockholm 2021" in myArray[row][3]:
                #quantity
                arraySum[1][1]= arraySum[1][1]+quantity
                #market volume
                arraySum[1][2]= arraySum[1][2]+volumeMarket
                #cost
                arraySum[1][3]= arraySum[1][3]+purchasePrice*quantity
                #current value
                arraySum[1][4]= arraySum[1][4]+currentPrice*quantity

            elif "Antwerp 2022" in myArray[row][3]:
                #quantity
                arraySum[2][1]= arraySum[2][1]+quantity
                #market volume
                arraySum[2][2]= arraySum[2][2]+volumeMarket
                #cost
                arraySum[2][3]= arraySum[2][3]+purchasePrice*quantity
                #current value
                arraySum[2][4]= arraySum[2][4]+currentPrice*quantity

            elif "Rio 2022" in myArray[row][3]:
                #quantity
                arraySum[3][1]= arraySum[3][1]+quantity
                #market volume
                arraySum[3][2]= arraySum[3][2]+volumeMarket
                #cost
                arraySum[3][3]= arraySum[3][3]+purchasePrice*quantity
                #current value
                arraySum[3][4]= arraySum[3][4]+currentPrice*quantity

            elif "Paris 2023" in myArray[row][3]:
                #quantity
                arraySum[4][1]= arraySum[4][1]+quantity
                #market volume
                arraySum[4][2]= arraySum[4][2]+volumeMarket
                #cost
                arraySum[4][3]= arraySum[4][3]+purchasePrice*quantity
                #current value
                arraySum[4][4]= arraySum[4][4]+currentPrice*quantity
    # calculations
    if arraySum[0][4]!=0:
        #profit
        arraySum[0][5] = arraySum[0][4]-arraySum[0][3]
        #ROI
        arraySum[0][6] = arraySum[0][5]/arraySum[0][3]
        
    if arraySum[1][4]!=0:        
        #profit
        arraySum[1][5] = arraySum[1][4]-arraySum[1][3]
        #ROI
        arraySum[1][6]= arraySum[1][5]/arraySum[1][3]
        
    if arraySum[2][4]!=0:       
        #profit
        arraySum[2][5] = arraySum[2][4]-arraySum[2][3]
        #ROI
        arraySum[2][6]= arraySum[2][5]/arraySum[2][3]
        
    if arraySum[3][4]!=0:  
        #profit
        arraySum[3][5] = arraySum[3][4]-arraySum[3][3]
        #ROI
        arraySum[3][6]= arraySum[3][5]/arraySum[3][3]
    if arraySum[4][4]!=0:  
        #profit
        arraySum[4][5] = arraySum[4][4]-arraySum[4][3]
        #ROI
        arraySum[4][6]= arraySum[4][5]/arraySum[4][3]
        
    
    
    return arraySum.tolist()

#we are sending acquired values from API to google sheet
def putOnSheet(myList,nameSheet):
    
    global timeAddedOnGS
    #we are adding time on spreadsheet when program started work
    if(timeAddedOnGS == False):
        now = datetime.now()
        dateString = now.strftime("%H:%M %d/%m/%Y")
        columnNames = [(dateString,"Total cost","Total value","Profit","ROI")]

        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,range="sumarry!A2",
                                        valueInputOption="USER_ENTERED",body={"values":columnNames}).execute()
        timeAddedOnGS = True

    #list of
    if(nameSheet !="sumarry" and nameSheet != "sumarryV2"):

        nameSheet= nameSheet+"!A3"
        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,range=nameSheet,
                                        valueInputOption="USER_ENTERED",body={"values":myList}).execute()
    #global summary    
    if(nameSheet=="sumarryV2"):

        #global sumarryRow
        sheetLocation = "sumarry!B"+str(sumarryRow)
        
        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,range=sheetLocation,
                                        valueInputOption="USER_ENTERED",body={"values":myList}).execute()
    #event summary    
    if(nameSheet=="sumarry"):
        
        global currentRowInSheet     

        for x in range(len(myList)):
            eventName = nameSheet +"!G"+ str(currentRowInSheet) 
            # we don't want to have empty rows in our spread
            if(myList[x][1]!=0):

                listToSend = [(myList[x][0],myList[x][1],myList[x][2],myList[x][3],myList[x][4],myList[x][5],myList[x][6])]
                request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=eventName,valueInputOption="USER_ENTERED",body={"values":listToSend}).execute()  
                currentRowInSheet= currentRowInSheet + 1
        currentRowInSheet= currentRowInSheet + 1

#saving current inventory check to history sheet
def addToHistory(rowsInSumarry,idDestination,action):  

    

    if(action=="history"):
        workOnDB(condition="read")   
        print("First row of current history: ",valueInt)
        request_body = {
            'requests': [
                {
                    'copyPaste':{
                        'source':{

                            'sheetId': 0,
                            'startRowIndex': 1,
                            'endRowIndex': 1+rowsInSumarry,
                            'startColumnIndex': 0,
                            'endColumnIndex': 13
                                                },
                        'destination':{

                            'sheetId': idDestination,
                            'startRowIndex': valueInt,
                            'endRowIndex': valueInt+rowsInSumarry, # 36 cuz i have 36 rows in my summary
                            'startColumnIndex': 0,
                            'endColumnIndex': 13

                        },
                        'pasteType': 'PASTE_NORMAL'
                    }
                }
            ]
        }
        response = sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID,body=request_body).execute()
        workOnDB(condition="update")
    if(action=="compare"):
        request_body = {
            'requests': [
                {
                    'copyPaste':{
                        'source':{

                            'sheetId': 0,
                            'startRowIndex': 1,
                            'endRowIndex': 1+rowsInSumarry,
                            'startColumnIndex': 0,
                            'endColumnIndex': 13
                                                },
                        'destination':{

                            'sheetId': idDestination,
                            'startRowIndex': 1,
                            'endRowIndex': 1+rowsInSumarry, # 36 cuz i have 36 rows in my summary
                            'startColumnIndex': 15,
                            'endColumnIndex': 28

                        },
                        'pasteType': 'PASTE_NORMAL'
                    }
                }
            ]
        }
    response = sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID,body=request_body).execute()


def workOnDB(condition,rowsInSumarry=37):

    connection = sqlite3.connect("infoData.db")
    cursor = connection.cursor()
    
    sqlQueryCreateTable = "CREATE TABLE IF NOT EXISTS Information ( rID INTEGER PRIMARY KEY,name TEXT UNIQUE, value INTEGER)"
    cursor.execute(sqlQueryCreateTable)

    #cursor.execute("INSERT OR IGNORE INTO Information VALUES(1,'rowInHistorySheet',2")
    if(condition=="read"):
        cursor.execute("SELECT * FROM Information WHERE rID=1")
        value = cursor.fetchall()
        global valueInt 
        valueInt = value[0][2]
        connection.close()  
    if(condition == "update"):
        
        valueInt=valueInt+rowsInSumarry
        cursor.execute("UPDATE Information SET value="+str(valueInt)+" WHERE rID=1")
        connection.commit()
        connection.close()     
                
def colorDifferences(firstRow,lastRow):
    
    

    response1 =  service.spreadsheets().values().get(
        spreadsheetId = SAMPLE_SPREADSHEET_ID,
        range = 'sumarry!L'+str(firstRow)+":L"+str(lastRow+1)
    ).execute()

    response2 =  service.spreadsheets().values().get(
        spreadsheetId = SAMPLE_SPREADSHEET_ID,
        range = 'sumarry!AA'+str(firstRow)+':AA'+str(lastRow+1)
    ).execute()
    
    value1Array = np.zeros(len(response1["values"]))
    value2Array = np.zeros(len(response1["values"]))

    value1Tuple = response1['values']
    value2Tuple = response2['values']

    

    for x in range(len(response1["values"])):

        if len(value1Tuple[x]) != 0:
            
            value1 = value1Tuple[x][0]          
            value2 = value2Tuple[x][0]

            
            if "," in value1:
                value1 = value1.replace(",","")
            if "," in value2:
                value2 = value2.replace(",","")
            value1Float = float(value1.replace(" zł",""))
            value2Float = float(value2.replace(" zł",""))
            
            value1Array[x] = value1Float
            value2Array[x] = value2Float


    valuesCalculation = np.zeros(len(value1Array))
    cellColors = pd.DataFrame(columns=['Red','Green','Blue'])
    request = []

    for x in range(len(value1Array)):
        if value1Array[x] != 0 and value2Array[x] != 0:
            valuesCalculation[x] = value1Array[x] - value2Array[x]
            
            if value1Array[x] > value2Array[x] and valuesCalculation[x]>0 and value1Array[x]<0:
                valuesCalculation[x] = (valuesCalculation[x]/value1Array[x])*(-1)
            elif value1Array[x] > value2Array[x]:
                valuesCalculation[x] = (valuesCalculation[x]/value1Array[x])
            elif value1Array[x] < value2Array[x] and valuesCalculation[x]<0 and value2Array[x]<0:
                valuesCalculation[x] = (valuesCalculation[x]/value2Array[x])*(-1)
            elif value1Array[x] < value2Array[x]:
                valuesCalculation[x] = (valuesCalculation[x]/value2Array[x])

            

        if valuesCalculation[x]== 0:
            cellColors.loc[len(cellColors.index)] = [1,1,1]
        elif valuesCalculation[x] > 0 and valuesCalculation[x] <= 0.05:
            cellColors.loc[len(cellColors.index)] = [0.8,1,0.8]
        elif valuesCalculation[x] > 0.05 and valuesCalculation[x] <= 0.10:
            cellColors.loc[len(cellColors.index)] = [0.4,1,0.4]
        elif valuesCalculation[x] > 0.10 and valuesCalculation[x] <= 0.15:
            cellColors.loc[len(cellColors.index)] = [0,1,0]
        elif valuesCalculation[x] > 0.15:
            cellColors.loc[len(cellColors.index)] = [0,0.6,0]
        elif valuesCalculation[x] >=-0.05 and valuesCalculation[x] < 0:
            cellColors.loc[len(cellColors.index)] = [1,0.8,0.8]
        elif valuesCalculation[x] >=-0.10 and valuesCalculation[x] < -0.05:
            cellColors.loc[len(cellColors.index)] = [1,0.4,0.4]
        elif valuesCalculation[x] >=-0.15 and valuesCalculation[x] < -0.10:
            cellColors.loc[len(cellColors.index)] = [1,0.2,0.2]
        elif valuesCalculation[x] < -0.15:
            cellColors.loc[len(cellColors.index)] = [1,0,0]
        #print("Row:",x+3)
        #print(valuesCalculation[x]," and color ", cellColors.loc[len(cellColors.index)-1])
        request.append(
            
            {
            "updateCells": {
            "rows": [
                {
                    "values": [{
                                   "userEnteredFormat": {
                                       "backgroundColor": {
                                           "red": cellColors['Red'][x],
                                           "green": cellColors['Green'][x],
                                           "blue": cellColors['Blue'][x]
                                           #"alpha": 0.8
                                       }}}
                    ]
                }
            ],
            "fields": 'userEnteredFormat.backgroundColor',
            "range": {
                "sheetId": 0,
                "startRowIndex": 2+x,
                "endRowIndex": 3+x,
                "startColumnIndex": 11,
                "endColumnIndex": 12
            }}})

        body = {
            'requests': request
        }
        
    response = sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID,body=body).execute()
       

# DB: ID, linkPrice, linkDailySell, name, quantity, purchasePrice, 
# currentPrice, volumeMarket, dailySell


addToHistory(36,0,"compare")
putOnSheet(addDataFromAPI(readTable("caseTable")),"caseSpreed")
print("END case")
putOnSheet(addDataFromAPI(readTable("souvenirTable")),"souvenirSpreed")
print("END souvenir")
putOnSheet(addDataFromAPI(readTable("patchTable")),"patchSpreed")
print("END patch")
putOnSheet(addDataFromAPI(readTable("capsuleTable")),"capsuleSpreed")
print("END capsule")
putOnSheet(addDataFromAPI(readTable("goldStickerTable")),"goldStickerSpreed")
print("END gold")
putOnSheet(addDataFromAPI(readTable("foilStickerTable")),"foilStickerSpreed")
print("END foil")
putOnSheet(addDataFromAPI(readTable("holoStickerTable")),"holoStickerSpreed")
print("END holo")
putOnSheet(addDataFromAPI(readTable("glitterStickerTable")),"glitterStickerSpreed")
print("END glitter")
putOnSheet(addDataFromAPI(readTable("paperStickerTable")),"paperStickerSpreed")
print("END paper")

print("Number of errors: ",errorCounter)
if (errorCounter != 0):
    arrayOfErrors = arrayOfErrors.reshape(errorCounter,2)
    for x in range(len(arrayOfErrors)):
        print("The following error, number:  ",arrayOfErrors[x][0]," name: ",arrayOfErrors[x][1]) 

colorDifferences(3,37)
addToHistory(36,192195635,"history")






