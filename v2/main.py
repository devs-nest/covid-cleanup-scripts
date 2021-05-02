from covidRes import CovidRes
# from errorList import li

# import csv
covid = CovidRes()
covid.readCsv('small.csv')
# with open('testfile.csv') as file:
#       print('reading....')
#       read = csv.reader(file, delimiter=',')
#       countRows = 1
      
#       rowsN = []

#       for row in read:
#         s = covid.getListOfWords(row[2])
#         resource_sub_type = covid.parseResourceSubType(s)
#         resource_type = covid.parseResourceType(resource_sub_type, s, countRows)
#         # print(countRows, ' ', resource_sub_type, ' ', resource_type)
#         if not resource_sub_type and not resource_type:
#           rowsN.append(countRows)
#         countRows += 1

# print(rowsN)

# for x in li:
#   print(covid.parseResourceType('', x[1], 0))