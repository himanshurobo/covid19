import requests
import lxml.html as lh
import pandas as pd


from fuzzywuzzy import fuzz 
from fuzzywuzzy import process

from sklearn import preprocessing




def checker(wrong_options,correct_options):
    response = []    
    for wrong_option in wrong_options:
        x=process.extractOne(wrong_option,correct_options)
        response.append((x[0],x[1],wrong_option))
    return response

def getIndiaData():
    # url='https://www.latlong.net/search.php?keyword=bihar'
    url='https://www.mohfw.gov.in/'
    #Create a handle, page, to handle the contents of the website
    page = requests.get(url)
    #Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    #Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')
    

    i=0
    p_elements = doc.xpath('//p')

    print(len(p_elements))
    last = int(len(p_elements)-1)
    #For each row, store each first element (header) and an empty list
    for t in p_elements:
        i+=1
        name=t.text_content()
        print ('%d:"%s"'%(i,name))
        # col.append((name,[]))

    dateTime = (p_elements[last]).text_content()
    
    dateTime = dateTime[37:-1]
    #print(tr_elements)

    #Check the length of the first 12 rows
    # [len(T) for T in tr_elements[:12]]



    tr_elements = doc.xpath('//tr')
    #Create empty list
    col=[]
    i=0
    #For each row, store each first element (header) and an empty list
    for t in tr_elements:
        i+=1
        name=t.text_content()
        # #print ('%d:"%s"'%(i,name))
        col.append((name,[]))


    #Since out first row is the header, data is stored on the second row onwards
    for j in range(1,len(tr_elements)):
        #T is our j'th row
        T=tr_elements[j]
        
        #If row is not of size 10, the //tr data is not from our table 
        if len(T)!=10:
            break
        
        #i is the index of our column
        i=0
        
        #Iterate through each element of the row
        for t in T.iterchildren():
            data=t.text_content() 
            #Check if row is empty
            if i>0:
            #Convert any numerical value to integers
                try:
                    data=int(data)
                except:
                    pass
            #Append the data to the empty list of the i'th column
            col[i][1].append(data)
            #Increment i for the next column
            i+=1


    [len(C) for (title,C) in col]




    data = []

    for (title,C) in col[:-1]:
        #print("--->>>",title.split("\n"))
        hello = [x.strip() for x in title.split("\n") if x.strip() != '']
        # data.append(title.split("\n"))
        # #print(hello)
        data.append(hello)



    df = pd.DataFrame(data)
    # #print(df.head())    
        
    # df.set_index('S. No.', inplace=True)
    # Dict={title:column for (title,column) in col}
    # df=pd.DataFrame(Dict)
    # #print(Dict)


    index = df.loc[(df[0] == 'S. No.')].index[0]


    df = df.iloc[index:]

    df.reset_index(drop=True,inplace=True)

    df.columns = df.iloc[0]
    df.drop(df.index[0],inplace=True)
    # using dictionary to convert specific columns 
    convert_dict = {'Total Confirmed cases (Indian National)': float, 
                    'Total Confirmed cases ( Foreign National )': float,
                    'Cured/Discharged/Migrated' : float,
                    'Death' : float
                }
    df['Total Confirmed cases (Indian National)'] = df['Total Confirmed cases (Indian National)'].str.extract(r'(\d+)').astype('float')
    df['Total Confirmed cases ( Foreign National )'] = df['Total Confirmed cases ( Foreign National )'].str.extract(r'(\d+)').astype('float')
    df['Cured/Discharged/Migrated'] = df['Cured/Discharged/Migrated'].str.extract(r'(\d+)').astype('float')
    df['Death'] = df['Death'].str.extract(r'(\d+)').astype('float')

    # df = df.astype(convert_dict)
    # print(df.info())
    df['Active Cases'] = df['Total Confirmed cases (Indian National)'] + df['Total Confirmed cases ( Foreign National )'] \
        - df['Cured/Discharged/Migrated'] - df['Death']



    #print(df.tail())
    indiaStateLatLong = pd.read_csv('./indiaStateLatLong.csv',index_col=0)

    # # creating and passsing series to new column 

    # #print(indiaStateLatLong.head())

    str2Match = df['Name of State / UT'].fillna('######').tolist()
    strOptions =indiaStateLatLong.index.fillna('######').tolist()



    # #print(str2Match)

    name_match=checker(str2Match,strOptions)

    # #print(name_match)

    match_df = pd.DataFrame(list(name_match), columns=['States','score','Name of State / UT'])
    # #print(match_df)

    merged_df = match_df.merge(df, how = 'inner', on = ['Name of State / UT'])
    merged_df = merged_df.merge(indiaStateLatLong, how = 'inner', on = ['States'])

    #print(merged_df.head())

    print("Get Indian Data")

    convertList = list(convert_dict.keys())
    convertList.append('Active Cases')
    merged_df.drop(columns=['States','score'],inplace=True)
    # #print(indiaStateLatLong.loc[name_match[0]])
    merged_df.set_index('S. No.',inplace=True)
    merged_df.loc['Total'] = merged_df[convertList].sum(axis=0,numeric_only=True)
    merged_df.to_csv('./text.csv',index=False)
    return merged_df,dateTime




def getCountryWiseData():
    print("Get Country Wise Data")
    dataUrl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv'

    df = pd.read_csv(dataUrl)
    
    df['Active'] = df['Confirmed'] + df['Deaths'] \
        - df['Recovered']

    # Create x, where x the 'scores' column's values as floats
    x = df[['Active']].values.astype(float)

    # Create a minimum and maximum processor object
    min_max_scaler = preprocessing.MinMaxScaler()

    # Create an object to transform the data to fit minmax processor
    x_scaled = min_max_scaler.fit_transform(x)

    # Run the normalizer on the dataframe
    df['mean_active'] = x_scaled

    df.loc[df['mean_active'] == 0.0,'mean_active'] = 0.005
    # mean_active = df.Active.dropna().mean()
    # max_active = df.Active.dropna().max()
    # min_active = df.Active.dropna().min()

    # df['mean_active'] = df['Active'].apply(lambda x: (x - mean_active ) / (max_active -min_active ))

    df.rename(columns={"Lat": "Latitude", "Long_": "Longitude", "Active" : "Active Cases"},inplace=True)

    #print(df.head())

    # df = df[:5]
    df1 = df.copy()
    df['StartDate'] = pd.to_datetime(df['Last_Update'])
    recent_date = df['StartDate'].max()


    df.to_csv('./text1.csv',index=False)
    return df,str(recent_date)


