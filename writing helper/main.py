
import pandas as pd
import operator
from collections import Counter
import os
import sys, codecs

# These packages are for drawing the frame
import tkinter as tk
from tkinter import filedialog

# These packages are for NLP implementations
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import nltk
#nltk.download('punkt')


# These packages is for converting pdf to texts
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import getopt

# this package is to copy file from src to dest directory
import shutil



# Implementing the search functions

"""
This class is responsible for

1. Gather search result
2. Auto complete and auto search

"""
class Search():
    def __init__(self):
        self.a =1

    """
    Input: search keyword, tokenized sentence and words in a map
    Output: list of the synnym in dictionary, nynonym used in the dataset, antonym, and ranked sentencesfrom the dataser
    
    """
    def searchresult(self,woi,map_sentence_tokens):
        sarr = wordnet.synsets(woi)
        synonyml1=[]
        synonyml2=[]
        synonympaper=[]
        antonym=[]
        sentencepaper=""

        # COnstruct the synonym list and antonym list from the dictionary
        for syn in sarr:
            for lem in syn.lemmas():
                synonyml1.append(lem.name())
                
                for ant in lem.antonyms():
                    antonym.append(ant.name())

        # construct advanced and extended synonym list from the dictionary       
        for woi2 in synonyml1:
            sarr2=wordnet.synsets(woi2)
            for syn in sarr2:
                for lem in syn.lemmas():
                    synonyml2.append(lem.name())
                    
        
        synonyml1 = set(synonyml1)
        synonyml2 = set(synonyml2)
        antonym = set(antonym)


        # find the synonyms used in the dataset
        for sentence in map_sentence_tokens.keys():
            for word in map_sentence_tokens[sentence]:
                if word in synonyml1:           # in which array, we want to consider: primary l1, secondary l2
                    synonympaper.append(word)

        synonympaper = set(synonympaper)
        
        print("Found synonym in papers are: ",synonympaper)

        # find the relevent sentence
        map_sentence_foundwordcount={}
        for sentence in map_sentence_tokens.keys():
            count = len(list(set(synonyml1) & set(map_sentence_tokens[sentence]))) # rank the sentences from the dataset
            #count = len(list(woi) & map_sentence_tokens[sentence]) # in which array, we want to consider: primary woi, then l1, secondary l2
            map_sentence_foundwordcount[sentence]=count

        sorted_map_score= dict(sorted(map_sentence_foundwordcount.items(),key=operator.itemgetter(1),reverse=True)) # rank the sentences from the dataset
        j=1
        for sentence in sorted_map_score.keys():
            sentencepaper += str(j)+".   "+sentence+"\n\n"
            print(sentence, " Score: ", sorted_map_score[sentence]) 
            j+=1
            if j>10:
                break

        print("\n\n\nPriority sentences: ",sentencepaper)

        return synonyml1,synonyml2,synonympaper, antonym,sentencepaper,sorted_map_score  


"""
This driver function is responsible to:
1. Design the form
2. Upload the dataset pdfs
3. Convert pdf to text to create dataset
4. Gather search keywor, and search in the texts files
5. Report search result form the data papers and also from the dictionary
6. Clear the dataset papers
 
"""

class Driver():
    
    def __init__(self):
        self.map_sentence_tokens={} # Key: sentence Value: words as tokenized
        self.loadalldocs() # load in the datastructures at the begining of the run
        self.drawframe() # draw the frame

    """
    Input: None
    Output: load the map datastructure based on the  dataset available at the start
    
    """
    def loadalldocs(self):
        self.cwd = os.getcwd()
        textdir = txtDir = self.cwd+"/texts/"
        for filename in os.listdir(textdir):
            filepath = os.path.join(textdir, filename)
            self.loadsingledoc(filepath)
            print("File name: ",filepath,"  Total sentence: ", len(self.map_sentence_tokens.keys()))
            
            
    """
    Draw the frame here
    The button, text fields, labels are ll declared here
    
    """
    def drawframe(self):
        self.root = tk.Tk()
        self.root.title("WritingHelper")

        # Pdf upload frame
        self.labelgupload = tk.Label(self.root,text="Upload a PDF file: ")
        self.labelgupload.grid(row=1,column=0,sticky='W')
        self.buttonchoosefile = tk.Button(self.root,text="Choose File",width = 21, command=self.clickchoosefile) # button for change settings
        self.buttonchoosefile.grid(row = 1,column=1,sticky="W")

        # Searching codes starts here
        self.labelsearch = tk.Label(self.root,text="Type the keyword:")
        self.labelsearch.grid(row=3,column=0,sticky='W')
        self.entrysearch = tk.Entry(self.root,width=25)
        self.entrysearch.grid(row=3,column=1,sticky='W')
        self.buttonsearch = tk.Button(self.root,text="Go",width = 21, command=self.clicksearch) # button for search
        self.buttonsearch.grid(row = 4,column=1,sticky="W")

        # clear database part here
        self.labelclear = tk.Label(self.root,text="Clear Dataset Papers: ")
        self.labelclear.grid(row=1,column=2,sticky='W')
        self.buttonchoosefile = tk.Button(self.root,text="Clear Dataset",width = 21, command=self.clicksleardataset) # button for change settings
        self.buttonchoosefile.grid(row=2,column=2,sticky="W")    

        self.root.mainloop()

    # event handler for clearing the dataset
    def clicksleardataset(self):
        txtfilesdir= self.cwd+"/texts/"
        pdffilesdir = self.cwd+"/pdfs/"

        # remove the text files
        filelist = [ f for f in os.listdir(txtfilesdir) ]
        for f in filelist:
            os.remove(os.path.join(txtfilesdir, f))

        # remove the pdf files
        filelist = [ f for f in os.listdir(pdffilesdir) ]
        for f in filelist:
            os.remove(os.path.join(pdffilesdir, f))

        #Reset the datastructures
        self.map_sentence_tokens={}
        self.synonyml1=self.synonyml2=self.synonympaper= self.antonym=[]
        self.sentencepaper=""


    # event handler for searching    
    def clicksearch(self):
        woi= self.entrysearch.get()
        woi=woi.lower() # convert the search keyword to lower case
        print("Searching going on!! Keyword: ",woi)
        search = Search()
        # Main search result come from here
        self.synonyml1,self.synonyml2,self.synonympaper, self.antonym,self.sentencepaper,sorted_map_score = search.searchresult(woi, self.map_sentence_tokens)
        print("\n\n\nSearch complete ")


        # show the result
        self.labelsynpaper = tk.Label(self.root,text="Synonym from paper: ")
        self.labelsynpaper.grid(row=6,column=0,sticky='W')
        self.textsynpaper = tk.Text(self.root,width=50, height=7, wrap = tk.WORD, background="white")
        self.textsynpaper.grid(row=7,column=0,sticky='W')
        self.textsynpaper.delete(0.0,tk.END)
        self.textsynpaper.insert(tk.END,str(self.synonympaper).strip('[]')) # Show the synonyms from the paper
        
        self.labelsynl1 = tk.Label(self.root,text="Synonym from Dictionary: ")
        self.labelsynl1.grid(row=8,column=0,sticky='W')
        self.textsynl1 = tk.Text(self.root,width=50, height=7, wrap = tk.WORD, background="white")
        self.textsynl1.grid(row=9,column=0,sticky='W')
        self.textsynl1.delete(0.0,tk.END)
        self.textsynl1.insert(tk.END,str(self.synonyml1).strip('[]')) # Show the synonyms from the  dictionary

        self.labelsynl2 = tk.Label(self.root,text="Synonym Extended: ")
        self.labelsynl2.grid(row=10,column=0,sticky='W')
        self.textsynl2 = tk.Text(self.root,width=50, height=7, wrap = tk.WORD, background="white")
        self.textsynl2.grid(row=11,column=0,sticky='W')
        self.textsynl2.delete(0.0,tk.END)
        self.textsynl2.insert(tk.END,str(self.synonyml2).strip('[]')) # Show the extended synonyms from the dict

        self.labelant = tk.Label(self.root,text="Antonym from Dictionary: ")
        self.labelant.grid(row=12,column=0,sticky='W')
        self.textantl1 = tk.Text(self.root,width=50, height=7, wrap = tk.WORD, background="white")
        self.textantl1.grid(row=13,column=0,sticky='W')
        self.textantl1.delete(0.0,tk.END)
        self.textantl1.insert(tk.END,str(self.antonym).strip('[]')) # Show the antonyms from the dictionary

        self.labelsentence = tk.Label(self.root,text="Sentence suggested from paper: ")
        self.labelsentence.grid(row=6,column=1,sticky='W')
        self.textsentence = tk.Text(self.root,width=90, height=33, wrap = tk.WORD, background="white")
        self.textsentence.grid(row=7,column=2, rowspan=10,sticky='W')
        self.textsentence.delete(0.0,tk.END)
        self.textsentence.insert(tk.END,self.sentencepaper) # Show the ranked sentences from the paper

    # Event handler for uploading new data file
    def clickchoosefile(self):
        initialdirectory="D:\My Drive/2 Research/forum/papers/"   # Initial directory for the upload dialog box
        selectedfilename=filedialog.askopenfilename(initialdir=initialdirectory, title="Select a File", filetype=(("PDF file","*.pdf"),("All files","*.*")))
        onlyfilename= selectedfilename.split("/")[-1]
        print("Only file name: ",onlyfilename)
        
        print("Selected filename: ",selectedfilename ) # this is the file directory to be uploaded
        self.labelguploadsucess = tk.Label(self.root,text="You uploaded: "+onlyfilename)
        self.labelguploadsucess.grid(row=2,column=0,sticky='W')

        # Store the pdf file
        dest = self.cwd + "/pdfs/" # This iswhere we store the pdfs
        
        print("Dest=",dest)

        
        shutil.copy(selectedfilename,dest) # Copy the slected file to pdfs directory
        
        

        # Convert the pdf to text and store the converted text [ create a file txt , store in /texts/ directory]
        fileExtension = selectedfilename.split(".")[-1]
        textfiledirectory= self.cwd + "/texts/"+ selectedfilename.split("/")[-1]
        if fileExtension == "pdf":
            pdfFilename = selectedfilename
            text = self.convert(pdfFilename) #get string of text content of pdf
            textFilename = textfiledirectory + ".txt"
            textFile = codecs.open(textFilename, "w",encoding='utf-8') #make text file
            textFile.write(text.lower()) #write text to text file
        print("Uploaded file converted...")


        # load this uploaded doc to our map
        self.loadsingledoc(textFilename)
        print("Total length of the map: ",len(self.map_sentence_tokens.keys()))




    """
    Input: a filepath
    Description: read the file from, store in the map (sent, words)
    Output: construct the map
    """
    def loadsingledoc(self,filepath):
        with codecs.open(filepath, 'r',encoding='utf-8') as f: # open in readonly mode
            data = f.read().replace('\n', ' ')
            sentences = sent_tokenize(data)
            for sentence in sentences:
                words = word_tokenize(sentence)
                if sentence not in self.map_sentence_tokens.keys():
                    self.map_sentence_tokens[sentence]=words




    """
    Input: fileame
    Description: Use pdf miner to mine the pdf and convert to text, 
    Output: file with Converted text
    """
    def convert(self,fname, pages=None):
        if not pages:
            pagenums = set()
        else:
            pagenums = set(pages)

        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams()) # conversion pre step
        interpreter = PDFPageInterpreter(manager, converter)

        infile = open(fname, 'rb')
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page) # conversion takes place here
        infile.close()
        converter.close()
        text = output.getvalue()
        output.close
        return text            

# main function
def main():
    driver = Driver()



if __name__ == "__main__":
    main()
