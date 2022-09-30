# Wikipedia Scraper
The project extracts information from locally provided API which has list of countries with their leaders' information which includes
names and wikipedia links. Then for each country it tries to read leaders wikipedia and collect the first paragraph and then constract
simplified information of the leaders which then be saved as a json file.

## Input
Input: API's base URl to retrieve requered cookies, list of countries and leaders 

## Output
json file containing simplified leaders information per country together with first paragraph from their wikipedia page.

## Rnunning the project

### Windows command line

```
> python3 -m wikipedia_scraper.py [path to save the files]  
```

### Linux terminal

```
$ python wikipedia_scraper.py [path to save the files]  
```
