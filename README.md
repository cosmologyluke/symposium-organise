# Symposium running order scripting

## About the code
This code was written by [Luke Hart](https://cosmologyluke.github.io) whilst he was at JBCA as a means to determine and create the running order for slides in the symposium. Since this will be a running trend over years, this code is hopefully generalised enough that you can just clone in and run it with the data included. The code will generate a set of PDFs with all the symposium slides you want and breaker slides to be included for each of the groups as they come up. Each group of slides is formed into a *batch* which is represented by 1 PDF file. Note that this will only work with the current JBCA symposium *minute per slide* format.

## Dependencies
The script `symposium.py` requires that `PyPDF2` is installed to generate the slides PDF files. You can install this using conda by
```
conda install -c conda-forge pypdf2
```
or by using pip,
```
pip install PyPDF2
```

Once this package is installed, the rest simply relies on an up-to-date Python 3 distribution. (Python 3.5 is being deprecated by Pip at some point so make sure that is considered when installing.)

## Running the script
 
 ### Preparing the information
 Before you run `symposium.py`, there are a couple of steps to follow:
1. Create a `./data/` and `./slides` directory to load up the names and file names for the members of the department you want presenting at your symposium
2. Generate a CSV file in the following format
```
First, Last, FileName.pdf, 1/0
```
where `First` and `Last` are the respective person's names, `FileName.pdf` is the slide carried in the `./slides/` directory, and the final 1/0 flag is an additional measure. Make sure this file is called `symposium_data.csv`. 
    In the last symposium, several members of the department could not participate within a certain time frame, so the 1 denoted their presentation had to be at the lunch hour and the 0 denotes that they can do any time at all. Play around with the *lunchtime* criterion in `symposium.py` otherwise just keep all these 0 if you do not require this function.

3. Run `symposium.py` from the home directory

## Notes about the script
- During the last symposium, we needed *breakout rooms* for the virtual setting of the symposium. This meant that an  `include_breakout` flag was included, set to 1 if there was a *breakout room* staple slide included in that particular batch. `include_breakout=1` adds a breakout slide **before** the member slides and `include_breakout=-1` adds the breakout slide **after**. 
- The `add_TY` flag adds a simple `beamer` slide that says Thank you to the group, which was reserved for the final group given in the last situation. 
- `SlideSessions` is the main construction function and takes the number of slides, the `Cohort()` base class which has all the data of the members, then the index of the session  for the distinct PDF file and finally the optional arguments. The definition looks like
```
slideSes = SlideSessions(num_slides, cohort, index, lunchtimeSession = False, include_breakout = 0, add_TY = False)
```
 - Note if you were doing this for multiple groups, you could actually give `Cohort()` an argument called  `dataFile` and that would target a different csv file. 

## Queries
Drop an issue in the repo if there are any problems.

I hope that this proves useful! :) 
Luke
