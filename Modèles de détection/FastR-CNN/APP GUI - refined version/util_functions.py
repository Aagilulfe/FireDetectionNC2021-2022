import os
from tkinter import Canvas, Button, StringVar, OptionMenu, HORIZONTAL
from tkinter import ttk

"""
utilitary functions for GUI_FasterRCNN
"""

def initCompareTab(root, tab, Run, GenerateZipFile, OpenLogs, UploadAction, OpenAnomaliesDir, rootHeight, rootWidth, barLength, left_mod, right_mod, model_path="models/"):
    """
    Initiate a tab for comparison
    Returns a dict with all the variables of the tab:
        - oldModelPath
        - newModelPath
        - datasetPath
        - uploadLabel
        - butUpload
        - butRun
        - butZip
        - butLogs
        - butAnomalies
        - butQuit
    """
    tab_vars = {}
    
    model_list = os.listdir("models/"+left_mod)

    oldModelPath = StringVar(tab)
    oldModelPath.set(model_list[0])
    opt = OptionMenu(tab, oldModelPath, *model_list)
    opt.grid(column=1, columnspan=2, row=1,padx=3,pady=3)
    tab_vars["oldModelPath"] = oldModelPath

    
    dataset_list = os.listdir("test_images/")

    datasetPath = StringVar(tab)
    datasetPath.set(dataset_list[-1])
    opt = OptionMenu(tab, datasetPath, *dataset_list)
    opt.grid(column=3, row=1)
    tab_vars["datasetPath"] = datasetPath

    uploadLabel = StringVar(tab)
    uploadLabel.set("Upload challenger model")
    butUpload = Button(tab, textvariable=uploadLabel, command=UploadAction)
    butUpload.grid(column=4, columnspan=2, row=1,padx=3,pady=3)
    tab_vars["uploadLabel"] = uploadLabel
    tab_vars["butUpload"] = butUpload
    tab_vars["newModelPath"] = None
    
    butRun = Button(tab, text="Run", command=Run)
    butRun.grid(column=3,row=2,padx=3,pady=3)
    tab_vars["butRun"] = butRun

    butLogs = Button(tab, text="Open logs", command=OpenLogs)
    butLogs.grid(column=1,row=3,padx=3,pady=3)
    butLogs["state"] = "disabled"
    tab_vars["butLogs"] = butLogs

    butAnomalies = Button(tab, text="Open images dir", command=OpenAnomaliesDir)
    butAnomalies.grid(column=2,row=3,padx=3,pady=3)
    butAnomalies["state"] = "disabled"
    tab_vars["butAnomalies"] = butAnomalies

    butZip = Button(tab, text="Generate zip file", command=GenerateZipFile)
    butZip.grid(column=4, columnspan=1, row=3, padx=3, pady=3)
    butZip["state"] = "disabled"
    tab_vars["butZip"] = butZip

    butQuit = Button(tab, text="Quit", command=root.quit)
    butQuit.grid(column=5, columnspan=1, row=3,padx=3,pady=3)
    tab_vars["butQuit"] = butQuit

    # left canva
    oldModelCanva = Canvas(tab, height=rootHeight - 105, width=(rootWidth-barLength - 6)//2 - 6, background="ivory")
    oldModelCanva.grid(column=1, columnspan=2, row=2,padx=3,pady=3)
    tab_vars["oldModelCanva"] = oldModelCanva

    # right canva
    newModelCanva = Canvas(tab, height=rootHeight - 105, width=(rootWidth-barLength - 6)//2 - 6, background="ivory")
    newModelCanva.grid(column=4, columnspan=2, row=2,padx=3,pady=3)
    tab_vars["newModelCanva"] = newModelCanva

    
    loadingBar = ttk.Progressbar(tab, orient=HORIZONTAL, length=100 - 6, mode='determinate')
    loadingBar.grid(column=3, row=3,padx=3,pady=3)
    tab_vars["loadingBar"] = loadingBar

    return tab_vars