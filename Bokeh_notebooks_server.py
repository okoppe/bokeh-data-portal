#!/usr/bin/env python
# coding: utf-8


import subprocess
import os
import bokeh
import threading
import git
import signal

class jupterNotebook:
    def __init__(self, fileName, filePath, port):
        self.fileName = fileName
        self.filePath = filePath
        self.port = port
        
    def serveBokehApp(self): 
        def startServer(self):
            BOKEH_ALLOW_WS_ORIGIN='ns1007523.ip-51-81-155.us:'+str(self.port)
            subprocess.call(['python3', '-m', 'bokeh', 'serve',  self.filePath, '--port', str(self.port), 
                 '--allow-websocket-origin=ns1007523.ip-51-81-155.us:'+str(self.port)])
            
        thread1 = threading.Thread(target=startServer, args=(self,))
        thread1.start()
    
    def shutdown(self):
        subprocess.call(['npx', 'kill-port', str(self.port)])
    
    def getPortLink(self):
        return ('ns1007523.ip-51-81-155.us:'+str(self.port)+'/'+self.fileName.replace(".ipynb",""))
    
    def getPort(self):
        return self.port
               
#j1 = jupterNotebook("neon.ipynb", "/Users/owenkoppe/Desktop/neon.ipynb", 5006)
#j1.serveBokehApp()


class handlePorts:
    def __init__(self, firstPortNumber):
        self.firstPortNumber = firstPortNumber
        self.openPorts = []
        self.NextNewPort = firstPortNumber
        
    def assignNewPort(self):
        if (len(self.openPorts)>0):
            new_port = self.openPorts[0]
            self.openPorts.remove(new_port)
            subprocess.call(['sudo', 'ufw', 'allow', str(new_port)])
            return new_port
        else:
            self.NextNewPort = self.NextNewPort+1
            subprocess.call(['sudo', 'ufw', 'allow', str(self.NextNewPort-1)])
            return(self.NextNewPort-1)
        
    def addBackOldPort(self, oldPort):
        subprocess.call(['sudo', 'ufw', 'deny', str(oldPort)])
        self.openPorts.append(oldPort)


class jupterNoteBookList:
    def __init__(self, gitHubLink, localRepoPath):
        self.gitHubLink = gitHubLink
        self.localRepoPath = localRepoPath
        self.servedFiles = 0
        self.notebookDict = {}
        self.g = git.cmd.Git(localRepoPath)
        self.g.pull(self.gitHubLink)
        self.fileArray = []
        self.BokehLinkDict = {}
        self.ports = handlePorts(5000)
        
    def updateLocalFiles(self):
        self.g.pull(self.gitHubLink)
        thisPullFiles = []
        for root, dirs, files in os.walk(self.localRepoPath):
            if (".git" not in root):
                for f in files:
                    if(".ipynb" in f):
                        thisPullFiles.append(f)
            
        #delete files from the array that have been deleted
        for oldFile in self.fileArray:
            if(oldFile not in thisPullFiles):
                self.fileArray.remove(oldFile)
                self.ports.addBackOldPort(self.notebookDict[oldFile].getPort())
                self.notebookDict[oldFile].shutdown()
                self.notebookDict.pop(oldFile)
                self.BokehLinkDict.pop(oldFile)
                

        for newFile in thisPullFiles:
            if newFile not in self.fileArray:
                self.fileArray.append(newFile)
                port = self.ports.assignNewPort()
                jnb = jupterNotebook(newFile, "/home/owenkoppe/fullTest/"+newFile, port)
                jnb.serveBokehApp()
                self.notebookDict[newFile] = jnb
                self.BokehLinkDict[newFile] = jnb.getPortLink()
                
    def loopUpdate(self):
        def loopFunction():
            while(True):
                self.updateLocalFiles()
                
        threadUpdateFiles = threading.Thread(target=loopFunction, args=())
        threadUpdateFiles.start()
        
    def getFileArray(self):
        return self.fileArray
    
    def getBokehLinkDict(self):
        return self.BokehLinkDict
                


j1 = jupterNoteBookList('https://github.com/okoppe/Juypter-Notebook-Repo.git', "/home/owenkoppe/fullTest")


j1.loopUpdate()






