#### website:  https://mtacommuter.herokuapp.com/

# Purpose of the project


This project is created for the purpose of The Data Incubator (TDI) capstone project. The challenge asks to "Propose a project to do while at The Data Incubator... Propose a project that uses a large, publicly accessible dataset. Explain your motivation for tackling this problem, discuss the data source(s) you are using, and explain the analysis you are performing. At a minimum, you will need to do enough exploratory data analysis to convince someone that the project is viable and generate two interesting non-trivial plots or other assets supporting this. Explain the plots and give url links to them."


# Motivation of the project


The goal is to develop an application called *Fantastic Commuters and Where to Find Them* (obviously, I’m a Harry Potter fan). The potential users of this app are the grocery delivery business. People’s lives have been dramatically changed since the global pandemic. One of the hot coro-nomics is that people now love to cook at home and get their groceries delivered. As we see the demands of grocery delivery surge, a lot of problems are showing up bothering everyone. Especially in New York City, we are seeing clogged streets full of delivery vehicles, parking violation tickets, fast riding e-bicycles, overwhelmed delivery staff and delays, and more.


As the economy opens, people gradually return to their social lives, and we can see crowded NYC subway again. The business idea here is to set up quick grocery pick-up or sales at the subway station on people’s way home or maybe other destinations. Delivery guys would be happy because they don’t need to buzz every building and bring grocery to the 5th floor. And customers would also be happy because they would be given discounts from the grocers, and it is usually not a long way to carry something from subway stations to homes.


Now the job is to tell the local business, where, when, and how many potential commuters you can find. This will help the local business make decisions.


This application can also be used by other pop-up business like food trucks, police for safety issues, or mobile network providers for signal boosts.


# Data source


The Metropolitan Transportation Authority (MTA) runs huge public transportation networks. According to MTA's website, the networks connect 12 counties in southeastern New York, along with two counties in southwestern Connecticut, carrying over 11 million passengers on an average weekday system-wide, and over 800,000 vehicles on its seven toll bridges and two tunnels per weekday. There are millions of millions of data generated over the years reflecting the commuters' behaviors.


This project focuses on analysizing the turnstile usage data generated from MTA New York City Transit (aka New York City Subway). The turnstile usage data are essentially the geographic and time distribution of the commuter behavior (enter or exit). 

The yearly data can be downloaded here:

- https://data.ny.gov/Transportation/Turnstile-Usage-Data-2021/uu7b-3kff 

The weekly data can be downloaded here: 

- http://web.mta.info/developers/developer-data-terms.html#data


## Data source structure


The row data has columns:

`C/A`      = Control Area (A002)
`Unit`     = Remote Unit for a station (R051)
`SCP`      = Subunit Channel Position represents an specific address for a device (02-00-00)
`Station`  = Represents the station name the device is located at
`Line Name` = Represents all train lines that can be boarded at this station
           Normally lines are represented by one character.  LINENAME 456NQR repersents train server for 4, 5, 6, N, Q, and R trains.
`Division` = Represents the Line originally the station belonged to BMT, IRT, or IND   
`Date`     = Represents the date (MM-DD-YY)
`Time`     = Represents the time (hh:mm:ss) for a scheduled audit event
`Description`     = Represent the "REGULAR" scheduled audit event (Normally occurs every 4 hours)
           1. Audits may occur more that 4 hours due to planning, or troubleshooting activities. 
           2. Additionally, there may be a "RECOVR AUD" entry: This refers to a missed audit that was recovered. 
`Entries`  = The comulative entry register value for a device
`Exits`    = The cumulative exit register value for a device

(http://web.mta.info/developers/resources/nyct/turnstile/ts_Field_Description.txt)


# Data processing and machine learning


## Determine unique turnstile

`Turnstile` is to identify a unique turnstile. The data is accumulated, so we need to find a specific turnstile to calculate the entries/exits. A unique `Turnstile` is defined by combining `C/A` + `Unit` + `SCP` + `Station`.


## Calculate increment at each station at each time period


Note that the `Entries` and `Exits` data are comulative. Calculate the data change for a specific turnstile in a time period. Add up all the turnstile data (at each data reporting time) in the same station. Since not all the turnstile upload data at the same time, but the majority of them update every 4 hours. So, cut the data into 6 periods for the convenience of data processing: 12 AM - 4 AM, 4 AM - 8 AM, 8 AM - 12 AM, 12 PM - 4 PM, 4 PM - 8 PM, 8 PM - 12 AM. Combine the data during the same time period at the same station.


There are of course missing data and obvious wrong/strange data. Remove the missing data. Remove negative data change (the turnstile data at one moment is smaller than that at the previous moment). Remove outlier data defined as > Q3 + 1.5 * IQR (upper quartile + 1.5 * interquartile range)(some data can be as large as 2 billion passenger at a single station at a 4-hour period). These wrong data may be due to the turnstile reset or simply some glitch.


Now we have passenger flow data (`Entries` and `Exits`) at each station at each 4-hour period of a day.


## Machine learning architecture


The project uses a simple but robust architecture. It assumes the passenger flow depends on the station , the day of a week, and the time of a day. Using one hot encoder to indicate the categorical parameters and a randomforest regressor, the accuracy of predicting exiting passenger flow is about 80%.


# Files explain


`df_geo.dill` includes the historical passenger flow data.


`est_onehot_ridge.dill` includes the trained model.


`dsl_geo.dill` includes the stations' geological data.


`station_name.dill` includes the stations' name.


`app.py` is the application mainly written in streamlit.


