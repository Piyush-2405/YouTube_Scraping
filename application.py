from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import pymongo

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/scrape',methods=['POST','GET']) # route to show the urls in a web UI
@cross_origin()

# @app.route('/favicon.ico')
# def favicon():
#     return ''


def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            browser  = webdriver.Chrome(ChromeDriverManager().install(), options=options)

            
            browser.get(searchString)
            browser.execute_script("window.scrollTo(0,400)", "")

            youtubePage = browser.page_source
            soup = bs(youtubePage, "html.parser")

            link = []
            thumbnail = []
            title = []
            views = []
            time = []

            soupData = soup.find("div", {"id": "contents"})

            try:
                videoSoup = (soupData.find_all(
                    "a", {"class": "yt-simple-endpoint inline-block style-scope ytd-thumbnail"}))[0:5]
                for i in videoSoup:
                    link.append("https://www.youtube.com"+str(i.get("href")))
            except:
                print("Error in Link")

            # Thumbnail
            try:
                soupvideoThumb = soup.find_all(
                    "img", {"class": "yt-core-image--fill-parent-height"})[:5]
                for i in soupvideoThumb:
                    thumbnail.append(str(i['src']))
            except:
                print("Error in Thumbnail Link")

            # Title
            try:
                soupTitle = (soupData.find_all("a", {
                    "class": "yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media"}))[0:5]
                for i in soupTitle:
                    title.append(str(i.get("title")))
            except:
                print("Error in Title")

            # No of views
            try:
                soupViews = (soupData.find_all("div", {"id": "metadata"}))[0:5]
                for i in soupViews:
                    views.append(str(i.find_all("span")[1].text))
            except:
                print("Error in no of views")

            # Time of Posting
            try:
                soupTime = (soupData.find_all("div", {"id": "metadata"}))[0:5]
                for i in soupTime:
                    time.append(str(i.find_all("span")[2].text))
            except:
                print("Error in Time of Posting")


            sc_data = []
            for i in range(5):

                dict = {
                    "link": link[i],
                    "thumbnail": thumbnail[i],
                    "title": title[i],
                    "views": views[i],
                    "time": time[i]
                }

                sc_data.append(dict)
            #inserting into mongodb
            youtube_coll.insert_many(sc_data)
                
            with open("youtube_scrap.csv", "w") as f:
                for i in sc_data:
                    f.write(str(i)+"\n")

            
            client = pymongo.MongoClient("mongodb+srv://compellingfuture24:pwskills@cluster0.z6gzk19.mongodb.net/?retryWrites=true&w=majority")
            db = client['YTvideo_scrap']
            youtube_col = db['YTvideo_scrap_data']
            youtube_col.insert_many(reviews)
            return render_template('results.html', reviews=sc_data)  
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
	#app.run(debug=True)
