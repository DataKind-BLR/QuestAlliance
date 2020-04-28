
# Read the Wiki page for this project and repository first. 
The [Wiki](https://github.com/DataKind-BLR/QuestAlliance/wiki) can be found here


## Development
Requires Python3 SQLite
check requirements.txt

## Initialization

create Virtual Env

```bash
cd QuestAlliance

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```  


## Note on Patches/Pull Requests

1) Make your feature addition or bug fix.

2) Run isort to alphabetically sort your imports
```bash
isort /PATH/TO/FILE.py
``` 

3) Run autopep8 to make sure the code follows the pep8 style <br>
pep8 style guide :  https://www.python.org/dev/peps/pep-0008/  

```bash
autopep8 --in-place /PATH/TO/FILE.py
``` 

4) Add tests under QuestAlliance/test

5) Send a pull request. Bonus points for topic branches!

## How to run the scraper script for the NCS website.
1) Install the geckodriver executable for Firefox in the QuestAlliance folder
2) Run the scraper using the following command
```bash
python ncs_scraper.py -he
``` 

**Data Points**

- Salary        (amount range) / per month
- Experience    ("freshers can apply")
- Location      (location, city, area)

Additional details
- Job Type      (Full time / part time etc.)
- Working Days  (days)

Requirements
- Education
- Age
- Experience
