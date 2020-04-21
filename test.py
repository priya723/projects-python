import json
import requests
import pandas as pd
from flask import Flask,request
from bs4 import BeautifulSoup 
from flask_restful import Resource,Api
from prettytable import PrettyTable
import matplotlib.pyplot as plt

app = Flask(__name__)
api= Api(app)
class covid(Resource):
    def get(self):
        # POST to API
        url = 'https://www.mygov.in/corona-data/covid19-statewise-status'
        # make a GET request to fetch the raw HTML content
        web_content = requests.get(url).content
        # parse the html content
        soup = BeautifulSoup(web_content, "html.parser")    
        # remove any newlines and extra spaces from left and right
        extract_contents = lambda row: [x.text.replace('\n', '') for x in row]

        stats = [] # initialize stats
        all_rows = soup.find_all('tr') # find all table rows 
        

        for row in all_rows: 
            stat = extract_contents(row.find_all('td')) # find all data cells  
            # notice that the data that we require is now a list of length 4
            if len(stat) == 5: 
                stats.append(stat)
        # now convert the data into a pandas dataframe for further processing
        new_cols = ["S.No","States/UT","Confirmed","Recovered","Deceased"]
        state_data = pd.DataFrame(data = stats, columns = new_cols)
        print(state_data)
        
        # converting the 'string' data to 'int'
        state_data['Confirmed'] = state_data['Confirmed'].map(int)
        state_data['Recovered'] = state_data['Recovered'].map(int)
        state_data['Deceased']  = state_data['Deceased'].map(int)

        # pretty table representation
        table = PrettyTable()
        table.field_names = (new_cols)
        for i in stats:
            table.add_row(i)
        table.add_row(["","Total", 
                    sum(state_data['Confirmed']), 
                    sum(state_data['Recovered']), 
                    sum(state_data['Deceased'])])
        print(table)
        #return "u have got your table"

        
        

       
api.add_resource(covid,"/covid")

if __name__ == '__main__':
    app.run(debug=True)
    
