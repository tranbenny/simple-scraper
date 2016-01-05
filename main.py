'''
create a CSV file with rating information about restaurants in Manhattan
'''

import requests
from bs4 import BeautifulSoup
import json
from urlObject import urlObject


def putScore(location, score, information):
    isResident = ", NY" in location
    if isResident:
        scores = information['new_york_ratings'].keys()
        if score in scores:
            information['new_york_ratings'][score] += 1
        else:
            information['new_york_ratings'][score] = 1
    else: # not a resident
        scores = information['other_ratings'].keys()
        if (score in scores):
            information['other_ratings'][score] += 1
        else:
            information['other_ratings'][score] = 1

file = open('manhattanRestaurants.json', 'w')
grabber = urlObject()
url = grabber.getURLs()['manhattanRestaurants.json']

r = requests.get(url)
soup = BeautifulSoup(r.content, "html.parser")
restaurants = []

# search through links to find all search results of a query
# need to find up to x number of restaurants

allRestaurants = soup.find('ul', {'class' : 'pagination-links'})
restaurantPageLinks = allRestaurants.find_all('li')


for link in restaurantPageLinks:
    # all the results one the first page
    if link.find('span') is not None:
        urlLink = url
    else:
        urlLink = grabber.base + link.find('a')["href"]
    r = requests.get(urlLink)
    soup = BeautifulSoup(r.content, "html.parser")
    resultsList = soup.find_all('li', {'class' : 'regular-search-result'})
    # for every restaurant result
    for result in resultsList:
        information = {
            'name' : "",
            'avg_rating' : "",
            'new_york_ratings' : {},
            'other_ratings' : {},
            'address' : ''
        }
        # attributes:

        # get name
        title = result.find('a', {'class' : 'biz-name'})
        name = title.find('span').text
        information["name"] = name
        link = title['href']

        # get avg_rating
        rating = result.find("i", {"class" : "star-img"})['title']
        rating = float(rating[:3])
        information['avg_rating'] = rating

        # get address
        address = result.find('address')
        information['address'] = address.text.strip()

        # access reviews: 1 page of results, need to do for all pages of results
        # need to find how many pages there are <---
        singleUrl = grabber.base + link # first page
        singleRequest = requests.get(singleUrl)
        newSoup = BeautifulSoup(singleRequest.content, "html.parser")

        allReviewsLinks = newSoup.find('ul', {'class' : 'pagination-links'})
        try:
            links = allReviewsLinks.find_all('li') # all links in one page
        except AttributeError:
            print('AttributeError: found no links')
            continue
        for i in range(1, len(links)):
            url = links[i].find('a')['href']
            newRequest = requests.get(url)
            smallSoup = BeautifulSoup(newRequest.content, "html.parser")
            # on a given review page, this finds all the reviews
            reviewInfo = smallSoup.find_all('div', {'class' : 'review'})
            for i in range(1, len(reviewInfo)):
                # find user location
                location = reviewInfo[i].find('li', {'class' : 'user-location'})
                city = location.find('b').text
                # find rating
                score = reviewInfo[i].find('meta', {'itemprop' : 'ratingValue'})
                stars = float(score['content'])
                putScore(city, stars, information)

        print(information)
        restaurants.append(information)
        file.write(json.dumps(information) + "\n")



print('FINISHED WRITING FILE')



