# Import arcpy module
import arcpy
import os
import sys
import csv
from arcpy import env
import operator
from Tkinter import Tk
from tkFileDialog import askopenfilename
from tkFileDialog import askdirectory
from progress.bar import Bar

def checkdictionary(dicti):
    print ("checking the dictionary")
    print (dict)
    a = max(dicti.iteritems(), key=operator.itemgetter(1))[0]
    print ("printing the highest area value")
    print (a)
    if (a == "AGR"):
        var["AGR"]= var["AGR"]+1
        print (var)
        dicti.clear()
    elif (a == "COM"):
        var["COM"]= var["COM"]+1
        print (var)
        dicti.clear()
    elif (a == "CULARCH"):
        var["CULARCH"]= var["CULARCH"]+1
        print (var)
        dicti.clear()
    elif (a == "FOR"):
        var["FOR"]= var["FOR"]+1
        print (var)
        dicti.clear()
    elif (a == "HYD"):
        var["HYD"]= var["HYD"]+1
        print (var)
        dicti.clear()
    elif (a == "OTH"):
        var["OTH"]= var["OTH"]+1
        print (var)
        dicti.clear()
    elif (a == "PUB"):
        var["PUB"]= var["PUB"]+1
        print (var)
        dicti.clear()
    elif (a == "RES"):
        var["RES"]= var["RES"]+1
        print (var)
        dicti.clear()
    else:
        return


#defining the workspace
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
a = askdirectory(title = "Select the workspace")
env.workspace = a
#env.workspace = "C:\Users\poshan\Desktop\spatial_join"

# Local variables:
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
present_landuse = askopenfilename( filetypes = (("Shapefiles","*.shp"),("ALl Files","*.*")), title = "Choose the Present Landuse or Landuse Zoning") # show an "Open" dialog box and return the path to the selected file

#present_landuse = "Bhumlu_Present_Landuse.shp"

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
parcel = askopenfilename( filetypes = (("Shapefiles","*.shp"),("ALl Files","*.*")), title = "Choose the Parcel") # show an "Open" dialog box and return the path to the selected file

intersect = "present_landuse_intersect_parcel1.shp"
dissolved = "dissolved1.shp"

bar = Bar('Processing', max=20)
bar.next()
# Process: Intersect
print("Performing the intersection of present landuse and parcel")
arcpy.Intersect_analysis([present_landuse,parcel], intersect, "ALL", "", "INPUT")


# Process: Dissolve
print("Performing the dissolve of the intersection based on present land use and parcel key")
dissolved_shp = arcpy.Dissolve_management(intersect, dissolved, "LEVEL1;PARCELKEY", "", "MULTI_PART", "DISSOLVE_LINES")

#add a field area in the table
# Set local variables
inFeatures = dissolved_shp
fieldName = "area"
fieldPrecision = 9
fieldLength = 10

# Execute AddField
print("Adding field area")
arcpy.AddField_management(dissolved_shp, fieldName, "double", fieldPrecision)

#calculate area
print("calculating the area in SQ. m")
expression1 = "{0}".format("!SHAPE.area@SQUAREMETERS!")
arcpy.CalculateField_management(dissolved_shp, fieldName, expression1, "PYTHON", )

var = {"AGR":0,"COM":0,"CULARCH":0,"FOR":0,"HYD":0,"IND":0,"OTH":0,"PUB":0,"RES":0}

dissolved_sorted = "dissolved_sorted.shp"
sort_fields = [["PARCELKEY", "DESCENDING"]]
sort_method = "PEANO"

print("sorting the dissolved data based on parcelkey")
arcpy.Sort_management(dissolved_shp, dissolved_sorted, sort_fields, sort_method)

#go through all the rows in parcel keys now to
print("traversing through the rows")
cursor = arcpy.SearchCursor(dissolved_sorted, sort_fields = "PARCELKEY; area")
row = cursor.next()
dicti = {}
lyr = arcpy.MakeFeatureLayer_management(dissolved_sorted, "lyr")
while row:
    dicti.clear()
    counter = 0
    parcel_key = row.getValue("PARCELKEY")
    #select by attribute the value of parcel key
    query = """ "PARCELKEY" = '%s'"""%parcel_key
    print (arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", query))
    cursor1 = arcpy.SearchCursor(arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", query))
    row1 = cursor1.next()
    while row1:
        parcel_key1 = row1.getValue("PARCELKEY")
        print (parcel_key1)
        area = row1.getValue("area")
        print (area)
        level = row1.getValue("LEVEL1")
        print (level)
        print("------------------------------------------------------------")
        dicti[level] = area
        row1 = cursor1.next()
        counter = counter + 1
        #check the end of the row and call  the function checkdictionary (dicti)
    checkdictionary(dicti)
    del row1
    i = 0
    while i < counter:
        row = cursor.next()
        i = i + 1
del row

arcpy.Delete_management(intersect)
arcpy.Delete_management(dissolved)
arcpy.Delete_management(dissolved_shp)
arcpy.Delete_management(dissolved_sorted)

#write csv file
with open('stat.csv', 'w') as csvfile:
    fieldnames = ['LandUse', 'No of Parcel']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for k in var:
        writer.writerow({'LandUse':k, 'No of Parcel':var[k]})
        bar.next()
bar.finish()    
    




    
