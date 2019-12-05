# General Assembly DSI 9 - Jorge Ramos
# Capstone: New App Evaluator
## Problem Statement
Determine whether a new app would be successful or not based on its title and description. To reach this result the model will relate the title and description of existing apps to their respective ratings and create a recommender that will act as an evaluator for future apps. This application will require a person to input the title and description of their app in order to be evaluated.

## Executive Summary
The users will access the web page and input their app's title and description. There will be a submit button that, when pressed, will activate the the evaluator and output a result. This result will contain the predicted rating that comes from the average of the most related apps. If the app is rated with a 4 or more, it will be considered successful, but below a 4 will suggest the person to rethink the title and description of the app.

Additionally the result will include some recommendations like:
- Age Rating:
  - Based on the existing most related apps.
- Genre:
  - Based on the existing most related apps.
  - This might be more than one genre if there is a chance that the app may be related to some other one.
- Categories:
  - Based on the existing most related apps.
  - This will include all the different categories in which the related apps have been classified in.
- Free or Paid:
  - Based on the existing most related apps.
  - A percentage of how many of the apps are free regarding the top ten most similar.
  - Will give the average price of the related apps.
  - And will show the maximum price of the related apps.

At the end, there will be a list of the most related apps with their respective ratings and links to the App Store.

## Data Collection & Cleaning
The data used for this project was obtained from a Kaggle dataset: 17K Mobile Strategy Games \
https://www.kaggle.com/tristan581/17k-apple-app-store-strategy-games \
I used the version 3 of this dataset, which was updated around sept-2019.

I also used the iTunes API to update some of the values that were considered NaNs. \
https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/

The dataset has information of 17,007 different apps from the Apple App Store and contains:
- URL: The URL
- ID: The assigned ID
- Name: The name
- Subtitle: The secondary text under the name
- Icon URL: 512px x 512px jpg
- Average User Rating: Rounded to nearest .5, requires at least 5 ratings
- User Rating Count: Number of ratings internationally, null means it is below 5
- Price: Price in USD
- In-app Purchases: Prices of available in-app purchases
- Description: App description
- Developer: App developer
- Age Rating: Either 4+, 9+, 12+ or 17+
- Languages: ISO2A language codes
- Size: Size of the app in bytes
- Primary Genre: Main genre
- Genres: Genres of the app
- Original Release Date: When it was released
- Current Version Release Date: When it was last updated

### Managing Null Values
Initially the Null Value count was:
- subtitle: 11746
- average_user_rating: 9446
- user_rating_count: 9446
- price: 24
- in-app_purchases: 9324
- languages: 60
- size: 1

#### Replacing all NaN values of "Average User Ratings"  and "User Rating Count" for 0
According to the discussion thread in Kaggle, these values are equivalent to NaNs because the apps have 4 or less ratings. As well as apple is probably assuming that these are non-representative for an assumption of good or bad overall rating, I will assume they all have 0 ratings. \
With this assumption in consideration, I will also give all this apps a rating of 0.

#### Replacing all NaN values of "subtitle" for " "
The NaN values in the subtitle column indicate that there is no subtitle, so this values will be changed for empty strings (a space) to make sure that we get the correct information while merging title, subtitle and description into one string.

#### Managing prices and correcting ratings
Since there are only 24 apps that have NaN values for prices I will input the actual values manually and correct rating information for these apps, if it is available in the website. I will also drop the rows containing apps that do not exist any more.

#### Managing languages
Since there are only 60 apps without a language I will input data manually in 3 steps.
1. Drop rows with apps that don't exist anymore
2. Change NaN languages for apps different than just "English"
3. Replace all remaining NaN values with "EN" for English

#### Managing In-app Purchases
For this part I went through the following steps:
1. Find the apps that have a strange value for this feature but the sum of all of them are equal to 0 and turn them into "0.00" or their respective values to match the rest.
2. Delete apps that don't exist any more.
3. Fill the rest of NaNs with "0.00".

## Feature Engineering
- Combo text: Combination of title, subtitle and description
- Is it free: 1 if the app is free and 0 if it has a cost
- In-app purchases sum: The sum of all available in-app purchases for each app
- Has in-app purchases: 1 if the app has in-app purchases and 0 if it does not have.
- Successful app: 1 if the app has a rating equals to 4 or more and 0 if it has less than 4
- Keyword Creation: Extract keywords of combo text.
- Category List: Enlist the categories that are set for every app as genre.

## Modeling and Building Application
The model uses the rake function to extract all keywords from the combo text for later use in the evaluation of the new app. After this, the words go into word2vec to make a larger list of similar keywords.

The function evaluator() receives 3 inputs:
- A dataframe containing all the existing apps.
- A title of the new app to be evaluated.
- A description of the new app to be evaluated.

This function will use the 2nd and 3rd input to combine, get keywords and broaden the list with word2vec to search within each of the existing apps keywords. The evaluator will start at a 90% coincidence and will reduce the threshold until it gets some results to evaluate the app. The function will output a list of app ids that will be later used to generate recommendations and show the similar apps.

The application is built using Flask in Python, HTML and CSS.
The application includes:
- Home page:
  - Where the user will input the title and description of their new app.
- Evaluation page:
  - Where the user will see the results
  - The title and an extract of the description written
  - The predicted rating and a message that tells the user whether or not the app is successful.
  - The recommendation area:
    - Age Rating
    - Genre
    - Categories
    - Free or Paid
  - Similar apps section
  - A link to go back to the home page

## Key Takeaways
- This application is a great tool for the user to check the potential of their app before releasing.
- It gives the developer a list of similar apps from which to learn and make some improvements for a better reception to clients.

## Next Steps
- Build a model that predicts if paid apps are more successful than free apps or the other way around. As a follow up to this figure out if the is strategic amount for the price to be just right for the public.
- Same idea with the in-app purchases. See if the most successful apps have in-app purchases and whether or not high or low prices influence people to purchase or not. This would require access to the app purchases to analyze what people are buying.
- Since there are some very well known developers, it would be interesting to know whether having one of this developers build the app makes its popularity rise faster than other apps with unknown developers.
- How important is it for the apps to be available in more than 1 language. Which are the most common languages for the top apps. How many ratings vs how many languages.
- Build a ranking of the apps including the predictions of the new app that is being consulted.
- Sentiment analysis to what people are saying about apps in social media.
