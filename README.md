
# Read the Wiki page for this project and repository first. 
The [Wiki](https://github.com/DataKind-BLR/QuestAlliance/wiki) can be found here

# Quest Alliance


create Virtual Env

```bash
cd QuestAlliance

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```  

Before you create a pull request

1) Run isort to alphabetically sort your imports
```bash
isort /PATH/TO/FILE.py
``` 

2) Run autopep8 to make sure the code follows the pep8 style
pep8 style guide :  https://www.python.org/dev/peps/pep-0008/  

```bash
autopep8 --in-place /PATH/TO/FILE.py
``` 

3) Add tests under QuestAlliance/test


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