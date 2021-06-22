# Casablanca-House-Prices
* Created a model that estimates property listing prices in the city of Casablanca, Morocco (MAPE ~ 17%) to help sellers estimate the current market price their property should be listed for
* Optimized Linear, Ridge, Lasso, Random Forest and Gradient Boosted Regressors using GridsearchCV to reach the best model.

## Code and Resources Used
**Python Version:** 3.8   
**Packages:** pandas, numpy, sklearn, matplotlib, seaborn, selenium, pickle

## Web Scraping
Built the webscraper from scratch using selenium to scrape 3000 property listings from mubawab.ma. For each listing we scraped the following :
*	Type of property
* Listing title
* Neighbourhood
* Latitude
* Longitude
* Tag list containing:
  * Area
  * Number of rooms
  * Number of bedrooms
  * Number of bathrooms
  * Floor
  * Current state
  * Age
* Price

## Data Cleaning
After scraping the data, I needed to clean it up for it to be usable by our model. The following changes were made :
* Parsed numeric data out of the scraped variables (price, area, rooms, bedrooms, bathrooms)
* Parsed neighbourhood string from full location string
* Converted tags variable consisting of lists into individual columns/variable 
* Set missing values to NaN
* Removed rows without price
* Added price by squared meter variable
* Filled the listings with missing type from the listing title
* Set the value of floor to 0 for non-appartment properties
* Dropped duplicated rows

## EDA
I explored the distribution of the data and the different variables as well as the relationship between variables.

The distribution of listings by type reveals an imbalance towards appartments with more than 1200 listings wivhi represents more than 75% of listings.
Maisons and Riads are very scare and hence were merged with Villas for the rest of the analysis.  
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Distribution_Listings_Type.png "Distribution of listings by type")

I noticed that there is a very large imbalance in the distribution of listings by neighbourhood. 50% of neighbourhoods are represented by 4 listings or less
while 80% of listings are associated with the 27 top neighbourhood by number of listings, this represents 25% of the total number of neighbourhoods.

![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Distribution_Listings_by_Neighbourhood.png "Distribution of listings by neighbourhood")

I continued the analysis with the 80% listings from the top 27 neighbourhoods.

Plotting the distribution of price per squared meter and by neighbourhood, we can spot that the data contains extreme outliers. Some listings have a 
price per m2 close to 0 and others are way too high.
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Distribution_Price_m2.png "Distribution of price per m2")
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Distribution_Price_m2_by_neighbourhood.png "Distribution of price per m2 by neighbourhood")

### Dealing with outliers
First I dropped every listing with a price by squared meter below 3000 MAD as a rational threshold based on data investigation and expertise.
Then I used a z-score on listings of the same neighbourhood to spot remaining outliers, and to deal with the fact that the z-score is already 
biased due to the presence of the outliers, I applied the sorting twice.

Applying the z-score once we spot the following outliers
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Distribution_Price_m2_by_neighbourhood_wt_outliers.png "Distribution of price per m2 by neighbourhood with outliers")

Applying the z-score sorting another time:
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Distribution_Price_m2_by_neighbourhood_wt_outliers2.png "Distribution of price per m2 by neighbourhood with remaining outliers")

After removing the outliers, here is the distribution of price per m2 and of price for appartments and for villas :
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Distribution_Price_m2_no_outliers.png "Distribution of price per m2 without outliers")
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Distribution_Price_no_outliers.png "Distribution of price without outliers")

### Explore the relationship between features and target
#### Price & Neighbourhood
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Average_Price_by_Neighbourhood.png "Average Price by Neighbourhood")
The price varies substantially depending on the property's neighbourhood. From this same plot we notice as expected that price also varies depending on property type.


#### Price and numerical features
![alt text](https://github.com/iliasoudghiri/Casablanca-House-Prices/blob/main/EDA_visuals/Correlation_matrix.png "Correlation matrix")

For Appartements we notice that the price is highly correlated to the area (0.88), number of rooms, bedrooms and bathrooms. However, number of rooms is a redundant feature considering it is in most of the cases very close to the sum of number of bedrooms and bathrooms. We hence naturally find a high correlation between rooms, bedrooms, and bathrooms which mean we should carefully select our features for modeling.

For Villas, price is highly correlated with area and moderatly correlated with Rooms, Bedrooms and Bathrooms. The correlation between the independant variables is less pronounced than for appartments.

## Model Building
First, I encoded Ordinal and Categorical variables and split the data into train and test set with a test set size of 30%

The performance metric I used to evalute models is the Mean Absolute Percentage Error (MAPE) and R^2. The reason I chose MAPE is that it is hard to interpret errore values when the property price range is so large, the MAPE made more sense. R^2 measured the variabillity of the data captured for the model and allowed me to spot models that were overfitting (large difference between the test and train R^2).

I performed hyperparameter tuning using Gridsearch with 5-fold cross-validation

The modells I tried :
* Multiple Linear Regression
* Ridge Regression — to introduce regularization 
* Polynomial regression (degree 2) — to test if interaction terms between variables explains the data better
* Random Forest — because I tought it would be a good fit with sparse data introduced by categorical variables
* Gradient Boosting Regression — again for the same reason as random forest 

## Model Performance
* Multiple Linear Regression
  * train MAPE : 0.2211
  * test MAPE : 0.2395
  * Training set score (R^2): 0.94
  * Test set score (R^2): 0.90 
* Ridge Regression {'alpha': 0.1}
  * train MAPE : 0.2208
  * test MAPE : 0.2394
  * Training set score (R^2): 0.94
  * Test set score (R^2): 0.90  
* Polynomial regression (degree 2) 
  * train MAPE : 0.2294
  * test MAPE : 0.2552
  * Training set score (R^2): 0.95
  * Test set score (R^2): 0.92  
* Random Forest {'max_depth': 10, 'max_features': 15, 'n_estimators': 200}
  * train MAPE : 0.1073
  * test MAPE : 0.1882
  * Training set score (R^2): 0.98
  * Test set score (R^2): 0.94  
* Gradient Boosting Regression {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 200}
  * train MAPE : 0.1125
  * test MAPE : 0.1713
  * Training set score (R^2): 0.99
  * Test set score (R^2): 0.94

## Limits of this project
The quality of the data collected could be enhanced as we rely on individual owners accuracy when listing their property on the website. Moreover, we should have collected a dataset of actual transactions to get a better idea of the actual property market value but unfortunately this was not available.
Our best regressor suffers from overfitting, we should try to increase the number of listings collected to deal with this.
