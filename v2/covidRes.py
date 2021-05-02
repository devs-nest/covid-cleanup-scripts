import csv
import requests
from city_to_state import city_to_state
import re
from resources import sub_types_to_type
import string
import os
from requests.auth import HTTPBasicAuth
import json

# When testing and you dont want to send requests to api set slef.TEST = True
# When you want logs of erros set self.DEBUG = True

class CovidRes:
  def __init__(self):
    self.TEST = False
    self.DEBUG = True
    self.API_KEY = os.environ['API_KEY']
    self.FD_ENDPOINT = os.environ['FD_ENDPOINT']
    self.URL =  "https://" + self.FD_ENDPOINT + ".freshdesk.com/api/v2/tickets"
    print('Using API_KEY:', self.API_KEY)
    print('Using FD_ENDPOINT:', self.FD_ENDPOINT)
    print('Using URL', self.URL)

  def testCsv(self, filename):
    with open(filename) as file:
      print('reading....')
      read = csv.reader(file, delimiter=',')
      for row in read:
        print('row[0] ', row[0])

  def readCsv(self, filename):
    with open(filename) as file:
      print('reading....')
      read = csv.reader(file, delimiter=',')
      # need to delete the row of every first row in csv as the first row has only the name of columns
      countRows = 0
      errorRows = []
      for row in read:
        try:
          # do not interchange next 2 lines, as other line depends on the first one
          error,city = self.parseCity(row[1], countRows)
          state = self.parseState(city, error, countRows)

          # do not interchange next 3 lines, as last 2 lines input depends on each other
          s = self.getListOfWords(row[2])
          resource_sub_type = self.parseResourceSubType(s)
          resource_type = self.parseResourceType(resource_sub_type, s, countRows)
          

          contact_name = self.parseContactName(row[5])
          contact_number = self.parseContactNumber(row[6], countRows)

          subject = str(resource_type) + ' in ' + str(state) + ', ' + str(city)
          description = 'Contact Name: ' + str(contact_name) + '<br>Contact Number: ' + str(contact_number) + '<br>Location: ' + row[4] + '<br>Source: ' + row[10]
          if len(description) > 199:
            description = (description[:197] + '..')

          self.makeRequest({
            'custom_fields': {
              'cf_resource_type': resource_type,
              'cf_sub_resource_type' : resource_sub_type,
              'cf_city' : city,
              'cf_state': state,
              'cf_supplierdonor_name' : contact_name,
              'cf_supplierdonor_contact_number': contact_number,
            },
            'status': 3,
            'priority': 1,
            'email': 'covidresourcesdotin@gmail.com',
            'description': description,
            'subject': subject,
          }, countRows)
        except Exception as e:
          if self.DEBUG: print(e)
          print('Error in row ', countRows)
          errorRows.append(row)
        finally:
          countRows += 1
      print('Error in', len(errorRows), 'out of', countRows)
      if len(errorRows) > 0:
        print('Generating error rows file')
        self.writeCsv(errorRows)
        print('Error rows file generated')
      else:
        print('No errors, no error file generated')

  def writeCsv(self, rows):
    with open('error_rows.csv', 'w') as f:
        write = csv.writer(f)
        write.writerow(rows[0])
        write.writerows(rows)

  def getListOfWords(self, stri):
    s = [string.capwords(x) for x in re.split('[^a-zA-Z]', stri) if x != '']
    return s

  def parseCity(self, city, rowNo):
    error = False
    if string.capwords(city) not in city_to_state:
      raise Exception('Error no city named ' + city + ' exists at row no. ' + str(rowNo))
    return error,city

  def parseState(self, city, error, rowNo):
    if not error:
      return city_to_state[city]

    if string.capwords(city) not in city_to_state.values():
      raise Exception('Error no state named '+ city +' exists at row no. '+ str(rowNo))
    
    return city
  
  # def desperatelyParseResourceType(self, col, rowNo):
  #   string_split = col.split('[^a-zA-Z]')
  #   for item in string_split:
  #     if sub_types_to_type.get(item):
  #       return sub_types_to_type.get(item)

  #   raise Exception('Error no resource type found at row no. '+ str(rowNo))
  #   return None

  # do not change the function again
  def parseResourceType(self, stri, s, rowNo):
    if stri:
      return sub_types_to_type[stri]

    if len(s) == 0:
      return None
    # print(s)
    x = s[0]
    # print(x)
    for i in range(1, len(s)):
      #l.append(s[i])
      count = 1
      # print('Here')
      for j in range(i, len(s)):
        # print('here')
        if count >= 4:
          break
        x = x + ' ' + s[j]
        # print(x)
        if x in sub_types_to_type.values():
          # print('Found resource type as ', x)
          if x == 'Medicines Injections':
            return 'Medicines/Injections'
          if x == 'Food Tiffin':
            return 'Food / Tiffin'
          return x

        #l.append(x)
        count += 1
        # print(x)
    #print(l)

    for i in range(len(s)):
      if x == 'Medicines' or x == 'Injections' or x == 'Medicine' or x == 'Injection':
        return 'Medicines/Injections'
      if x == 'Food' or x == 'Tiffin':
        return 'Food / Tiffin'
      if s[i] in sub_types_to_type.values():
        # print('Found resource type as ', s[i])
        return s[i]

    return None

  def parseResourceSubType(self, s):
    if len(s)==0:
      return None
    #s = [x for x in re.split('[^a-zA-Z]', string) if x != '']
    #l = [s[len(s)-1]]
    # print(s)
    x = s[0]
    for i in range(1, len(s)):
      #l.append(s[i])
      count = 1
      for j in range(i, len(s)):
        if count >= 4:
          break
        x = x + ' ' + s[j]
        # print(x, ' x')
        if x in sub_types_to_type:
          # print('Found resource sub type as ', x)
          return x

        #l.append(x)
        count += 1
        # print(x)
    #print(l)

    for i in range(len(s)):
      if s[i] == 'Remedesvier':
        return 'Remdesivir'
      if s[i] in sub_types_to_type:
        # print('Found resource sub type as ', s[i])
        return s[i]

    # print('Sub type not found')
    return None

  def parseContactName(self, name):
    return name

  def parseContactNumber(self, number, rowNo):
    if not number:
      raise Exception('Error no contact number at row no. '+ str(rowNo))
    return str(number)

  def makeRequest(self, data, index):
    # make network request to API
    if self.TEST:
      print('Data to send: ', data)
    else:
      print('Sending data', json.dumps(data))
      response = requests.post(
        self.URL,
        json=data,
        auth=HTTPBasicAuth(self.API_KEY, 'X')
      )
      if response.status_code == 201:
        print(index, 'row inserted successfully')
      else:
        if self.DEBUG:
          print('Request failed with code:', response.status_code)
          print('Response text:', response.text)
        else:
          print(index, 'row failed to inserted')
