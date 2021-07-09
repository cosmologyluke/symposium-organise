import PyPDF2
import numpy
import random
import subprocess
import os
import csv
from copy import deepcopy

def create_list_pdfs(dir):
    slideSet = os.listdir(dir)
    f=open('data/symposium_data.csv','w+')
    [f.write(slideName) for slideName in slideSet]
    f.close()
    return

class Member :
    def __init__(self,
                 first_name,
                 last_name,
                 filename,
                 lunchtime_talk):
        self.first=first_name
        self.last=last_name
        self.filename=filename
        self.talk_lunch=int(lunchtime_talk)
        self.page = self.makePageObj()
    def getFirstName(self):
        return self.first
    def getLastName(self):
        return self.last
    def getName(self):
        return self.first+" "+self.last
    def makePageObj(self):
        file=open(self.filename,'rb')
        pdfRead = PyPDF2.PdfFileReader(file,strict=False)
        pageObj= pdfRead.getPage(0)
        return pageObj

    def areTheyTalkingAtLunch(self):
        return self.talk_lunch
    def switchToLunch(self):
        if self.talk_lunch == 1:
            self.talk_lunch = 0
        else:
            self.talk_lunch = 1

class Cohort:
    def __init__(self,dataFile="symposium_data.csv"):
        self.slideno=0
        f=open(dataFile)
        sympDataReader=csv.reader(f)
        self.listOfMembers =[]
        for x in sympDataReader:
            member = Member(x[0],x[1],x[2],x[3])
            self.listOfMembers.append(member)
        for x in self.listOfMembers:
            if not isinstance(x,Member):
                print("Error. Wrong data type.")
        self.numberOfLunchSlides = len([x for x in self.listOfMembers if x.areTheyTalkingAtLunch() == 1])

    def chooseRandomMember(self, is_lunch=False):
        print(len(self.listOfMembers))
        if is_lunch and self.getNumberOfLunchSlides() > 0:
            chosenMember = random.choice([x for x in self.listOfMembers if x.areTheyTalkingAtLunch() == 1])
            self.numberOfLunchSlides-=1
        else:
            chosenMember = random.choice([x for x in self.listOfMembers if x.areTheyTalkingAtLunch() == 0])
        self.listOfMembers.remove(chosenMember)
        self.slideno+=1
        return chosenMember

    def getNumberOfLunchSlides(self):
        return self.numberOfLunchSlides


class IntroSlide:
    def __init__(self, index, currentNames, nextNames):
        self.currentNames = currentNames
        self.nextNames = nextNames
        self.index = index
        self.content = self.slideLatex()
    def slideLatex(self,ty=False):
        prefix =r'''\documentclass{beamer}
                    \begin{document}
                    \begin{frame}[plain,t,noframenumbering]
                    \vspace{10mm}
                    \begin{itemize}'''
        reducedMiddle =r'''\end{itemize}'''
        middle =r'''\end{itemize}
                    \vspace{10mm}
                    \addtolength{\leftmargini}{7cm}
                    \begin{itemize}'''
        suffix =r'''\end{itemize}
                    \end{frame}
                    \end{document}'''

        content=prefix
        for x in self.currentNames: content += self.lineOfName(x)
        if self.nextNames is not None:
            content += middle
            for x in self.nextNames: content += self.lineOfNextName(x)
        else:
            content += reducedMiddle
        content += suffix
        return content
    def lineOfName(self,name):
        return r"\item "+name+"\n"
    def lineOfNextName(self,name):
        return r"\item \textcolor{gray}{"+name+"}\n"
    def makeSlide(self):
        self.fname='intro'+str(self.index)
        with open(self.fname+'.tex','w') as f:
            f.write(self.content)
        process = subprocess.Popen(['pdflatex','-interaction','batchmode',self.fname+'.tex'])
        process.communicate()
        os.unlink(self.fname+'.tex')
        os.unlink(self.fname+'.log')
        pdfFile = open(self.fname+".pdf",'rb')
        pdfRead = PyPDF2.PdfFileReader(pdfFile,strict=False)
        pObj = pdfRead.getPage(0)
        return pObj

#  BO, slides, slides, BO, slides

class SlideSessions:
    def __init__(self, num_slides, cohort, index, lunchtimeSession = False, include_breakout=0,add_TY=False):
        self.numberOfSlides = num_slides
        self.cohort = cohort
        self.isLunchtimeSession = lunchtimeSession
        self.fileWriter = PyPDF2.PdfFileWriter()
        self.sessionsIndex = index
        groupCount = 0
        numRemainingSlides = self.numberOfSlides
        group0 = [self.cohort.chooseRandomMember(is_lunch=lunchtimeSession) for j in range(5)]
        if include_breakout==1:
            self.addBreakoutSlide()
        slide_i=0
        isItFinished=False
        while numRemainingSlides>0:

            if slide_i==0: thisGroup = [x for x in group0]
            nextGroupSize=5
            if numRemainingSlides<=10:
                nextGroupSize = numRemainingSlides-5
            if numRemainingSlides<=5:
                isItFinished=True
            numRemainingSlides-=5

            # Lunchtime flag switched off internally
            if isItFinished:
                groupSlide = IntroSlide(groupCount, currentNames=[x.getName() for x in thisGroup],nextNames=None)
            if not isItFinished:
                nextGroup = [self.cohort.chooseRandomMember(is_lunch=lunchtimeSession) for j in range(nextGroupSize)]
                groupSlide = IntroSlide(groupCount, currentNames=[x.getName() for x in thisGroup],nextNames=[x.getName() for x in nextGroup])
            self.fileWriter.addPage(groupSlide.makeSlide())
            [self.fileWriter.addPage(x.makePageObj()) for x in thisGroup]

            if not isItFinished:
                slide_i+=5
                thisGroup=nextGroup
                groupCount+=1
        if include_breakout == -1:
            self.addBreakoutSlide()
        if add_TY:
            self.addTYSlide()
        self.makeFile()
        return

    def makeFile(self):
        sessionsFile=open('session_'+str(self.sessionsIndex)+'.pdf','wb')
        self.fileWriter.write(sessionsFile)
        sessionsFile.close()
        return

    def addBreakoutSlide(self):
        boFile = open('breakout.pdf','rb')
        boRead = PyPDF2.PdfFileReader(boFile,strict=False)
        bObj = boRead.getPage(0)
        self.fileWriter.addPage(bObj)
        return

    def addTYSlide(self):
        tcontent=r'''\documentclass{beamer}
        \usepackage{tikzsymbols}

        \setbeamertemplate{frametitle}[default][center]
        \setbeamerfont{frametitle}{series=\bfseries}

        \begin{document}
        \begin{frame}
        \centering
        {\Large\bf Thank you very much \Laughey[1.4]}
        \end{frame}

        \end{document} '''
        self.fname='ty'
        with open(self.fname+'.tex','w') as f:
            f.write(tcontent)
        process = subprocess.Popen(['pdflatex','-interaction','batchmode',self.fname+'.tex'])
        process.communicate()
        os.unlink(self.fname+'.tex')
        os.unlink(self.fname+'.log')
        pdfFile = open(self.fname+".pdf",'rb')
        pdfRead = PyPDF2.PdfFileReader(pdfFile,strict=False)
        pObj = pdfRead.getPage(0)
        self.fileWriter.addPage(pObj)
        return

    def gutAuxillaryFiles(self):
        subprocess.call(['rm','intro*'])
        subprocess.call(['rm','ty*'])
        return

# First you will need to generate a list of speakers by uploading all the slides
# You can either add lines to the script which take names in as extra fields or you can add them into the symposium_data csv file by hand
create_list_pdfs("./")

# Generate a Cohort class which stores all the names of members of the department + the upload data for their slides
dept = Cohort()

# Use the cohort data to randomly assign sessions and include a cursory 'breakout slide' if your sessions will be bordered by a breakout
session1 = SlideSessions(25, dept, 1, include_breakout=1)
session2 = SlideSessions(25, dept, 2, include_breakout=-1,lunchtimeSession=True)
session3 = SlideSessions(15, dept, 3, include_breakout=0)
session4 = SlideSessions(14, dept, 4, include_breakout=1,add_TY=True)

# Removes messy files from wd
session4.gutAuxillaryFiles()
