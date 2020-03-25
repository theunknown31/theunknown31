#importing the Library
import tkinter as tk
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()
from googletrans import Translator
translator = Translator()
import csv 
import tweepy
import datetime
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM 
import time
import re
from pandas import concat
import numpy as np

#root
root= tk.Tk() 

#preprocessing Data
consumer_key = 'dgHUjdWUifw57wUEdAnLn5f4f'
consumer_secret = 'a2iX4kbbiloMxAHrKn26FCu3vqu9e3wQsTQX5C8fEiWTxyYYsD'
access_token = '1232317487506583555-tnOHPbOtP7G9NtXFidsSRtzattC3x9'
access_token_secret = 'fCYOEzjU0GtVrYbQDXar8mKX0WEPXCq2wry02hX3U8U03'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
values1=[0,0,0] 
pos=0
neg=0
neu=0

figure1 = plt.Figure(figsize=(6,5), dpi=100)
ax1 = figure1.add_subplot(111)
bar1 = FigureCanvasTkAgg(figure1, root)
bar1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
ax1.set_title('Corona Scare')

with open("pranjal111.csv", 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "date:","pos","neg","neu"
                    ])    
with open("pranjal111.csv", 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.datetime.now(),0,0,1
                    ])

#defining Data 
data1 = {'Country': ['US','CA','GER','UK','FR'],
         'GDP_Per_Capita': [45000,42000,52000,49000,47000]
        }
df1 = DataFrame(data1,columns=['Country','GDP_Per_Capita'])
 




#Text
tk.Label(root, text='Search') 
e1 = tk.Entry(root) 
e1.pack()


#functions    
def sentiment_analyzer_scores(text, engl=True):
    if engl:
        trans = text
    else:
        trans = translator.translate(text).text
    score = analyser.polarity_scores(trans)
    lb = score['compound']
    if lb >= 0.05:
        return 1
    elif (lb > -0.05) and (lb < 0.05):
        return 0
    else:
        return -1

def anl_tweets(lst, title='Tweets Sentiment', engl=True ):
    global pos,neg,neu
    for tw in lst:
        try:
            st = sentiment_analyzer_scores(tw, engl)
            if(st==1):
                pos=pos+1
            if(st==0):
                neg=neg+1
            if(st==-1):
                neu=neu+1
                
        except:
            print("Error")       
    pos1=pos/(pos+neg+neu)
    neg1=neg/(pos+neg+neu)
    neu1=neu/(pos+neg+neu)
    rmse=[abs(pos1-values1[0])/pos1*100,abs(neg1-values1[1])/neg1*100,abs(neu1-values1[2])/neu1*100]
    print(rmse)
    v1.set("Percent{}".format(rmse)) 
    root.update()
    with open("pranjal111.csv", 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.datetime.now(),pos1,neg1,neu1
                    ])
    series = read_csv('pranjal111.csv', header=0, index_col=0, parse_dates=True, squeeze=True) 
    ax1.plot(series.iloc[:,0],color="green")
    ax1.plot(series.iloc[:,1],color="red")
    ax1.plot(series.iloc[:,2],color="yellow")
    ax1.legend(["pos","neg","neu"])
    bar1.draw()
    #pyplot.plot(series)
    #pyplot.show()

def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)        
    return input_txt

def clean_tweets(lst):
    lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
    lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
    lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
    lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
    return lst
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
	n_vars = 1 if type(data) is list else data.shape[1]
	df = DataFrame(data)
	cols, names = list(), list()
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	agg = concat(cols, axis=1)
	agg.columns = names
	if dropnan:
		agg.dropna(inplace=True)
	return agg

#streamer
tweets=[]
mylist=[]
def twitter_stream_listener(
                            filter_track,
                            follow=None,
                            locations=None,
                            languages=None,
                            time_limit=20):
    global mylist
    global index1
    location=[float(OptionList1[i][index1]) for i in range(1,1,5)]
    class CustomStreamListener(tweepy.StreamListener):
        def __init__(self, time_limit):
            self.start_time = time.time()
            self.limit = time_limit
            super(CustomStreamListener, self).__init__()
        def on_status(self, status):
            if (time.time() - self.start_time) < self.limit:
              tweets.append(str(status.text))
            else:
                return False
        def on_error(self, status_code):
            if status_code == 420:
                print('Encountered error code 420. Disconnecting the stream')
                return False
            else:
                print('Encountered error with status code: {}'.format(
                    status_code))
                return True  # Don't kill the stream
        def on_timeout(self):
            print('Timeout...')
            return True  # Don't kill the stream
    # Writing csv titles
    streamingAPI = tweepy.streaming.Stream(
        auth, CustomStreamListener(time_limit=time_limit))
    streamingAPI.filter(
        track=filter_track,
        follow=follow,
        locations=location,
        languages=languages,
    )
    f.close()

filter=[]



def sentiment_predict():
    series = read_csv('pranjal111.csv', header=0, index_col=0, parse_dates=True, squeeze=True)
    series=series.values
    values=series_to_supervised(series,3)
    if(len(values.index)>1):
        train_X, train_y = values.iloc[:, :9].values, values.iloc[:,-3:].values
        train_X = train_X.reshape((train_X.shape[0], 3, 3))
        model = Sequential()
        model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
        model.add(Dense(3))
        model.compile(loss='mae', optimizer='adam')
        model.fit(train_X, train_y, epochs=50, batch_size=12, verbose=0, shuffle=False)
        train_y=train_y[-1,:]
        train_X=train_X[-1,1:]    
        train_X=np.append(train_X,train_y)
        train_X=train_X.reshape((1,3,3))
        yhat = model.predict(train_X)
        sums=sum(yhat[0])
        yhat[0][0]=yhat[0][0]/sums
        yhat[0][1]=yhat[0][1]/sums
        yhat[0][2]=yhat[0][2]/sums
        v2.set("{}".format(yhat[0]))
        root.update()
        return yhat[0]
    else:
        return [0,0,0]
   


#slider
i=0
OptionList=[]
data=[]
datafile = open('a.csv', 'r')
datareader = csv.reader(datafile, delimiter=',')
for row in datareader:
    data.append(row)
OptionList1=[list(i) for i in zip(*data)]
OptionList=OptionList1[0]
index1=0   
def callback(*args):
    global index1
    global mylist
    mylist=[]
    mylist.append(variable.get())
    index1=OptionList.index(variable.get())
    
    labelTest.configure(text="{}".format(mylist),width=20)    
variable = tk.StringVar(root)
variable.trace("w", callback)
variable.set(OptionList[0])
opt = tk.OptionMenu(root, variable, *OptionList)
opt.config(width=20, font=('Helvetica', 12))
opt.pack()
labelTest = tk.Label(text="", font=('Helvetica', 12), fg='red')
labelTest.pack(side="top")
v1=tk.StringVar(root)
v2=tk.StringVar(root)
v1.set("")
v2.set("")
w1=tk.Label(root,textvariable=v1)
w2=tk.Label(root,textvariable=v2)
stop=1
def show_entry_fields():
    global filter,tweets,values1,stop
    filter.append(e1.get())
    w=tk.Label(root, text="Seraching for {}".format(e1.get()))
    w.pack()
    while(stop==1):
        twitter_stream_listener(filter,time_limit=10)
        clean=clean_tweets(tweets)
        anl_tweets(clean,False)
        tweets=[]
        values1=sentiment_predict()
def show():
    global stop
    stop=0
       
button = tk.Button(root, text='Start', width=25, command=show_entry_fields) 
button.pack()  
w2.pack()
w1.pack()
button2 = tk.Button(root, text='Stop', width=25, command=show) 
button2.pack()
#start
root.mainloop()