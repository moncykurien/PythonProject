# importing necessary libraries
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from datetime import date, timedelta
import time

#initializing the flask app with the name app template/home.html
app = Flask(__name__)


def get_soup(url):
    req_data = requests.get(url)
    return bs(req_data.content, 'html.parser')

def get_product_link(url, actual_product):
    urll = url.split('/')
    return urll[0] + '//' + urll[2] + actual_product

def get_data_from_soup(data_soup, tag, atrb, atrb_name):
    return data_soup.findAll(tag, {atrb: atrb_name})
'''
    all_products = all_data[-2].findAll('div', {'class': '_1-WJZn'})
    del all_data

    actual_product = all_products[0].a['href']
    del all_products

    url = get_product_link(url, actual_product)

    data_soup = get_soup(url)
    '''


def load_database(review, web_site, scraped_date, element_dict, searchString, product_searched = None):
    try:
        review_header = review.find(element_dict['review_header'][0], {'class': element_dict['review_header'][1]}).get_text()
    except:
        review_header = 'No Header'
    try:
        review_summary = review.find(element_dict['review_summary'][0], {'class': element_dict['review_summary'][1]}).div.div.get_text()
    except:
        review_summary = 'No Summary'
    try:
        reviewer_name = review.find(element_dict['reviewer_name'][0], {'class': element_dict['reviewer_name'][1]}).get_text()
    except:
        reviewer_name = "No Name"
    try:
        review_likes_dislikes = review.find(element_dict['review_likes_dislikes'][0], {'class': element_dict['review_likes_dislikes'][1]}).get_text()
    except:
        review_likes_dislikes = 0
    try:
        review_rating = review.find(element_dict['review_rating'][0], {'class': element_dict['review_rating'][1]}).get_text()
    except:
        try:
            review_rating = review.find(element_dict['review_rating'][0], {'class': element_dict['review_rating'][2]}).get_text()
        except:
            review_rating = 'No Rating'

    review_dict = {'Product': searchString ,'review_rating': review_rating, 'reviewer_name': reviewer_name, 'review_header': review_header,
                   'review_summary': review_summary, 'review_likes_dislikes': review_likes_dislikes,
                   'scraped_date': scraped_date, 'scraped_source': web_site}
    return review_dict


@app.route('/', methods = ['GET']) #route to display the home page
def homePage():
    return render_template("home.html")

# This route accepts POST and GET methods
@app.route("/review", methods = ['POST','GET'])
def layout():

    if request.method == "POST":
        try:
            product = request.form['content']
            searchString = product.replace(' ','')# This obtains the search text from the form
                #Web scrapping

            flipkart_url = 'https://www.flipkart.com/search?q=' + searchString  # preping the url
            #amazon_url = 'https://www.amazon.in/search?q=' + searchString  # preping the url

            start_time_1 = time.time()
            urls = [flipkart_url]

            for url in urls:
                start_time_2 = time.time()
                data_soup = get_soup(url)
                if ('flipkart' in url):

                    all_data = data_soup.findAll('div', {'class': 'bhgxx2 col-12-12'})

                    try:
                        all_products = all_data[-2].findAll('div', {'class': '_1-WJZn'})
                        del all_data
                    except:
                        return render_template('home.html',message = "The item is not available. Please search something else")
                    #product_searched = all_products[0].a.div.text()
                    actual_product = all_products[0].a['href']
                    del all_products

                    product_url = get_product_link(url, actual_product)
                    data_soup = get_soup(product_url)
                    try:
                        all_reviews_link = data_soup.find('div', {'class': 'swINJg _3nrCtb'}).find_parent()['href']
                    except:
                        return render_template('home.html',message = "The item is not available. Please search something else")


                    all_reviews_url = get_product_link(url, all_reviews_link)
                    data_soup = get_soup(all_reviews_url)

                    all_reviews_data = data_soup.findAll('div', {'class': '_3gijNv col-12-12'})
                    all_review_pages = all_reviews_data[-1].findAll('a')

                    reviews_list = []
                    element_dict = {'review_header': ['p', '_2xg6Ul'], 'review_summary': ['div', 'qwjRop'], \
                                    'reviewer_name': ['p', '_3LYOAd _3sxSiS'], 'review_likes_dislikes': ['span', '_1_BQL8'], \
                                    'review_rating': ['div', 'hGSR34 E_uFuv', 'hGSR34 _1nLEql E_uFuv']}
                    end_time_2 = time.time()
                    print("Time taken to get all review pages: ", end_time_2 - start_time_2)
                    start_time_3 = time.time()
                    for tag in all_review_pages:

                        soup = get_soup("https://www.flipkart.com" + tag.get('href'))
                        review_soup = soup.findAll('div', {'class': 'col _390CkK _1gY8H-'})

                        for review in review_soup:
                            #,product_searched
                            rev_dict = load_database(review, 'Flipkart', str(date.today()), element_dict, product)
                            reviews_list.append(rev_dict)
                    end_time_3 = time.time()
                    print("Time taken to get all actual reviews: ", end_time_3 - start_time_3)
                    return render_template('results.html', reviews_list = reviews_list)

        except Exception as e:
            print('The exception is: ',e)
            return render_template('home.html',message = "The item is not available. Please search something else")
        finally:
            end_time_1 = time.time()
            print("Total time taken: ", end_time_1 - start_time_1)
    else:
        return render_template('home.html')

if __name__ == '__main__':
    app.run(debug = True)