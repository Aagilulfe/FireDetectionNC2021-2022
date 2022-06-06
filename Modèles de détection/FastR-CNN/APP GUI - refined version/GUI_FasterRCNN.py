from tkinter import Tk, filedialog, Label, Frame
from tkinter import ttk
import os
from PIL import Image as Im, ImageDraw as ImDr
import xml.etree.ElementTree as ET
from torchvision import transforms
import torch
import time
from datetime import datetime as dt
import shutil
# import yolov5.detect as yolo5Detect
from zipfile import ZipFile

# import of util_functions. homemade util function for initialization of tabs in GUI.
import util_functions


class GUI_FasterRCNN:
    # CONSTRUCTOR
    def __init__(self):
        """
        GUI dimensions
        """
        self.rootHeight = 700
        self.rootWidth = 900
        self.barLength = 100

        root = Tk()
        root.title("Model Tester")
        ws = root.winfo_screenwidth() # width of the screen
        hs = root.winfo_screenheight() # height of the screen   
        x = (ws//2) - (self.rootWidth//2)
        y = (hs//2) - (self.rootHeight//2)
        root.geometry('%dx%d+%d+%d' % (self.rootWidth, self.rootHeight, x, y))
        self.root = root

        # Creation of tabs
        self.tabControl = ttk.Notebook(root)
        self.tabConfusion = ttk.Frame(self.tabControl)
        self.tabStat = ttk.Frame(self.tabControl)
        # self.tabVisualize = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tabConfusion, text="Confusion matrix")
        self.tabControl.add(self.tabStat, text="Stats")
        # self.tabControl.add(self.tabVisualize, text="Visualize")
        self.tabControl.pack(expand=1, fill="both")

        # Confusion matrix tab
        confusion_vars = util_functions.initCompareTab(self.root, self.tabConfusion, self.Run, self.GenerateZipFile, self.OpenLogs, self.UploadAction, self.OpenAnomaliesDir, self.rootHeight, self.rootWidth, self.barLength, left_mod="rcnn", right_mod="rcnn")

        #Initialization of different parameters
        self.oldModelPath = confusion_vars["oldModelPath"]
        self.uploadLabel = confusion_vars["uploadLabel"]
        self.butUpload = confusion_vars["butUpload"]
        self.newModelPath = confusion_vars["newModelPath"]
        self.butRun = confusion_vars["butRun"]
        self.butLogs = confusion_vars["butLogs"]
        self.butAnomalies = confusion_vars["butAnomalies"]
        self.butQuit = confusion_vars["butQuit"]
        self.currentModelCanva = confusion_vars["oldModelCanva"]
        self.newModelCanva = confusion_vars["newModelCanva"]
        self.loadingBar = confusion_vars["loadingBar"]
        self.datasetPath = confusion_vars["datasetPath"]
        self.butZip = confusion_vars["butZip"]
        
        # root launch
        root.mainloop()
        self.root.destroy()

    # On click method for upload button.
    def UploadAction(self):
        self.filename = filedialog.askopenfilename(initialdir="models/rcnn/")
        print('Selected:', self.filename.split(sep="/")[-1])
        if self.filename != "":
            self.newModelPath = self.filename
            name = self.filename.split(sep="/")[-1]
            self.uploadLabel.set(name)
            self.root.bind_all('<Return>', lambda event: self.Run())

    # Util method for IoU evaluation. Calculate the intersection over union areas.
    def IoU(self, bbox1, bbox2):    # Xmin, Ymin, Xmax, Ymax
        inter_width = min(bbox1[2], bbox2[2]) - max(bbox1[0], bbox2[0])
        inter_length = min(bbox1[3], bbox2[3]) - max(bbox1[1], bbox2[1])
        if inter_width <= 0 or inter_length <= 0:
            return 0
        inter_area = inter_width * inter_length
        union_area = (bbox1[3]-bbox1[1])*(bbox1[2]-bbox1[0]) + (bbox2[3]-bbox2[1])*(bbox2[2]-bbox2[0]) - inter_area
        ratio = inter_area / union_area
        return ratio

    # Util method for Yolo testing (DEPRECATED)
    def yoloDetect(self, img_name, real_bbox):
        result_dir = os.listdir("yolov5/runs/detect/")[-1]
        yolo_path = "yolov5/runs/detect/"+result_dir
        img = Im.open(yolo_path+"/"+img_name)
        img_width, img_height = img.size
        labels = os.listdir(yolo_path+"/labels")
        for label in labels:
            if img_name.split(sep=".")[0] in label:
                with open(yolo_path+"/labels/"+label, "r") as file:
                    lines = file.readlines()
                smoke_pred = []
                for line in lines:
                    if line != "":
                        relative_coord = [float(i) for i in line.split()[1:]]
                        center_x = relative_coord[0] * img_width
                        center_y = relative_coord[1] * img_height
                        half_width = relative_coord[2] / 2 * img_width
                        half_height = relative_coord[3] / 2 * img_height
                        coord = [center_x-half_width, center_y-half_height, center_x+half_width, center_y+half_height]
                        smoke_pred.append(coord)
                IoU_bbox = self.IoU(smoke_pred[0], real_bbox)
                if IoU_bbox >= 0.5:
                    self.NewRepartition["TP"] += 1
                else:
                    self.NewRepartition["FP"] += 1
                    shutil.copy(yolo_path+"/"+img_name, "anomalies/yolo/FP_"+img_name)
                return
        self.NewRepartition["FN"] += 1
        shutil.copy(yolo_path+"/"+img_name, "anomalies/yolo/FN_"+img_name)

    # Util method for RCNN testing (OK)
    def rcnnDetect(self, model, img_name, img, real_bbox, repartition, mode):
        img_bbox = ImDr.Draw(img)
        tensor_img = transforms.ToTensor()(img)
        
        t0 = time.time()
        prediction = model([tensor_img.to(self.device)])[0]
        if mode == "old":
            self.CurrentDuration += time.time() - t0
        else:
            self.NewDuration += time.time() - t0

        data_zip=list(zip(*[v for k,v in prediction.items()]))
        all_smoke_pred = [value for value in data_zip if value[1]==1]

        if real_bbox != None:
            img_bbox.rectangle(xy=real_bbox, outline='blue', width=3)

        if all_smoke_pred: # verification de la bbox de plus grande confidence

            seuil = 0.4   # seuil de prise en compte de la bbox

            smoke_pred = all_smoke_pred[0]
            proba = smoke_pred[-1].detach().cpu().numpy()
            smoke_pred = smoke_pred[0].detach().cpu().numpy()
            
            img_bbox.rectangle(xy=[smoke_pred[0], smoke_pred[1], smoke_pred[2], smoke_pred[3]], outline='green', width=3)

            if real_bbox == None:
                repartition["FP"] += 1
                img.save("temp/"+mode+"/FP_"+img_name)
                return repartition
            IoU_bbox = self.IoU(smoke_pred, real_bbox)

            # LOGS
            self.WriteLogLine("old IoU: " + str(int(IoU_bbox*100)/100))

            if IoU_bbox >= 0.5:
                repartition["TP"] += 1
                img.save("temp/"+mode+"/TP"+img_name)
            else:
                repartition["FP"] += 1
                img.save("temp/"+mode+"/FP_"+img_name)
        elif real_bbox == None:
            repartition["TN"] += 1
            img.save("temp/"+mode+"/TN_"+img_name)
        else:
            repartition["FN"] += 1
            img.save("temp/"+mode+"/FN_"+img_name)

        return repartition

    # On click method of Run button. Initiate all parameters and vars for the tests, then calls Step method.
    def Run(self):
        if self.newModelPath != None:
            self.butRun["state"] = "disabled"       # disable run button

            self.currentModelCanva.delete('all')
            self.newModelCanva.delete('all')
            for img in os.listdir("temp/old"):
                os.remove("temp/old/"+img)
            for img in os.listdir("temp/new"):
                os.remove("temp/new/"+img)

            with open("logs.txt", 'w') as file:
                file.write("LOGS - "+str(dt.now()))
                file.write("\nCURRENT MODEL: " + self.oldModelPath.get())
                file.write("\nNEW MODEL: " + self.newModelPath)

            """
            Banque de test avec calcul de IoU
            """

            self.image_path= 'test_images/'+self.datasetPath.get()+'/image/'
            self.xml_path= 'test_images/'+self.datasetPath.get()+'/xml/'
            self.express_list= os.listdir(self.image_path)
            self.device = torch.device('cuda')
            print(self.device)


            print("Processing {0} images...".format(len(self.express_list)))

            # Old model
            path = "models/rcnn/"+self.oldModelPath.get()

            print("CURRENT : ", path.split(sep="/")[-1])
            self.CurrentModel = torch.load(path, map_location=torch.device('cuda'))
            self.CurrentModel.eval()

            # New model
            path = self.newModelPath

            print("NEW : ", path.split(sep="/")[-1])
            self.NewModel = torch.load(path, map_location=torch.device('cuda'))
            self.NewModel.eval()

            self.CurrentModel.cuda()
            self.NewModel.cuda()

            self.CurrentRepartition = {"TP": 0, "FN": 0, "FP": 0, "TN": 0} # Repartition of the old model (left side) for the confusion matrix
            self.NewRepartition = {"TP": 0, "FN": 0, "FP": 0, "TN": 0}  # Repartition of the new model (right side) for the confusion matrix

            self.CurrentDuration = 0
            self.NewDuration = 0

            self.count = 0  # the image count

            # prediction yolo :
            # t0 = time.time()
            # yolo5Detect.run(weights=self.newModelPath,imgsz=(500,500),conf_thres=0.2,source="test_images/image",save_txt=True)
            # self.NewDuration = time.time() - t0

            self.Step()

    # Does a test step. Called by Run method
    def Step(self):
        
        self.count += 1
        if self.count > len(self.express_list):
            print(self.CurrentRepartition)
            print(self.NewRepartition)
            self.Display()
            return
        percent = self.count*100 // len(self.express_list)
        self.loadingBar['value'] = percent

        img_name = self.express_list[self.count-1]
        self.WriteLogLine("\n==>" + img_name)
        img = Im.open(self.image_path+img_name).convert('RGB')

        # Extracting Xml bbox
        parts = img_name.split(sep=".")[:-1]
        xml_name = ""
        for part in parts:
            xml_name += part+"."
        xml_name += "xml"
        try:
            xml_tree = ET.parse(self.xml_path+xml_name)
            root = xml_tree.getroot()

            for neighbor in root.iter('bndbox'):
                xmin = float(neighbor.find('xmin').text)
                ymin = float(neighbor.find('ymin').text)
                xmax = float(neighbor.find('xmax').text)
                ymax = float(neighbor.find('ymax').text)
                real_bbox = [xmin, ymin, xmax, ymax]
        except FileNotFoundError:
            real_bbox = None

        # Detection
        self.CurrentRepartition = self.rcnnDetect(self.CurrentModel, img_name, img.copy(), real_bbox, self.CurrentRepartition, "old")
        self.NewRepartition = self.rcnnDetect(self.NewModel, img_name, img.copy(), real_bbox, self.NewRepartition, "new")
        # self.yoloDetect(img_name, real_bbox)

        if self.count == 1:     # One turn amorcage in order to avoid the setup time of first iteration
            self.CurrentDuration = 0
            self.NewDuration = 0

        self.WriteLogLine(str(self.CurrentRepartition) + " - " + str(sum([self.CurrentRepartition[i] for i in self.CurrentRepartition])) + " - " + str(self.CurrentDuration) + "\n" + str(self.NewRepartition) + " - " + str(sum([self.NewRepartition[i] for i in self.NewRepartition])) + " - " + str(self.NewDuration))

        self.root.after(250, self.Step)

    # Called when tests are finished. Handle all the results displaying stuff
    def Display(self):
        self.butRun["state"] = "normal"     #switching ON the run button
        self.butLogs["state"] = "normal"    #switching ON the logs button
        self.butAnomalies["state"] = "normal"    #switching ON the anomalies dir button
        self.butZip["state"] = "normal"     #switching ON the zip generator button

        # Confusion Matrix TAB
        self.currentModelCanva.create_text((self.rootWidth-self.barLength - 6)//4 - 3, 20, font="Verdana 10", anchor="center", text=str(self.CurrentDuration)+" sec.")
        self.newModelCanva.create_text((self.rootWidth-self.barLength - 6)//4 - 3, 20, font="Verdana 10", anchor="center", text=str(self.NewDuration)+" sec.")
        self.ConfusionMatrix((self.rootWidth-self.barLength - 6)//2 - 6, (10, 80), self.CurrentRepartition, self.currentModelCanva)
        self.ConfusionMatrix((self.rootWidth-self.barLength - 6)//2 - 6, (10, 80), self.NewRepartition, self.newModelCanva)

        # Stats TAB
        # score heuristic : (TP + TN) / (TP + TN + FN + FP/5)  (we minimize FP compared to FN because they are less critical in our problem)
        self.currentScore = (self.CurrentRepartition["TP"] + self.CurrentRepartition["TN"]) / (self.CurrentRepartition["TP"] + self.CurrentRepartition["TN"] + self.CurrentRepartition["FN"] + self.CurrentRepartition["FP"] / 5) * 20
        self.newScore = (self.NewRepartition["TP"] + self.NewRepartition["TN"]) / (self.NewRepartition["TP"] + self.NewRepartition["TN"] + self.NewRepartition["FN"] + self.NewRepartition["FP"] / 5) * 20

        self.currentScore = int(self.currentScore * 1000) / 1000
        self.newScore = int(self.newScore * 1000) / 1000

        self.currentTPI = int(self.CurrentDuration/len(self.express_list) * 1000) / 1000
        self.newTPI = int(self.NewDuration/len(self.express_list) * 1000) / 1000

        self.statsMatrix = [[None, "OLD", "NEW"],
                            ["Total duration (sec.)", int(self.CurrentDuration * 1000) / 1000, int(self.NewDuration * 1000) / 1000],
                            ["Time per image (sec.)", self.currentTPI, self.newTPI],
                            ["Nb of errors", self.CurrentRepartition["FP"]+self.CurrentRepartition["FN"], self.NewRepartition["FP"]+self.NewRepartition["FN"]],
                            ["False negatives", self.CurrentRepartition["FN"], self.NewRepartition["FN"]],
                            ["False positives", self.CurrentRepartition["FP"], self.NewRepartition["FP"]],
                            ["SCORE ( /20)", self.currentScore, self.newScore]]

        for i in range(len(self.statsMatrix)):
            for j in range(len(self.statsMatrix[0])):
                entry = self.statsMatrix[i][j]
                if entry != None:
                    if i == 4 and j >= 1:
                        color = "red"
                    elif i == 5 and j >= 1:
                        color = "orange"
                    else:
                        color = "black"
                    entry_font = "Verdana 10"
                    
                    border = Frame(self.tabStat, background="black")
                    Label(border, width=20, foreground=color, font=entry_font, text=str(entry), bd=0).pack(padx=1, pady=1)
                    border.grid(column=j+1, row=i+1)

    # displaying method of the confusion matrix
    def ConfusionMatrix(self, l, coord, repartition, canva):
        x, y = coord
        matrix_width = l - 2*x
        case_width = matrix_width // 3
        for vertical in [(x+i*case_width, y, x+i*case_width, y+3*case_width) for i in range(1,3)]:
            self.currentModelCanva.create_line(vertical)
            self.newModelCanva.create_line(vertical)
        for horizontal in [(x, y+i*case_width, x+3*case_width, y+i*case_width) for i in range(1,3)]:
            self.currentModelCanva.create_line(horizontal)
            self.newModelCanva.create_line(horizontal)
        
        # displaying columns and rows labels
        canva.create_text(x+case_width//2+case_width, y+case_width//2, font="Verdana 12 bold", anchor="center", text="PREDICTED\nsmoke")
        canva.create_text(x+case_width//2+2*case_width, y+case_width//2, font="Verdana 12 bold", anchor="center", text="PREDICTED\nno smoke")
        canva.create_text(x+case_width//2, y+case_width//2+case_width, font="Verdana 12 bold", anchor="center", text="ACTUAL\nsmoke")
        canva.create_text(x+case_width//2, y+case_width//2+2*case_width, font="Verdana 12 bold", anchor="center", text="ACTUAL\nno smoke")

        # displaying repartition
        canva.create_text(x+case_width//2+case_width, y+case_width//2+case_width, fill="green", font="Verdana 12 bold", anchor="center", text=str(repartition["TP"]))
        canva.create_text(x+case_width//2+2*case_width, y+case_width//2+2*case_width, fill="green", font="Verdana 12 bold", anchor="center", text=str(repartition["TN"]))
        canva.create_text(x+case_width//2+2*case_width, y+case_width//2+case_width, fill="red", font="Verdana 12 bold", anchor="center", text=str(repartition["FN"]))
        canva.create_text(x+case_width//2+case_width, y+case_width//2+2*case_width, fill="orange", font="Verdana 12 bold", anchor="center", text=str(repartition["FP"]))

    # util for writing in logs file
    def WriteLogLine(self, line):
        with open("logs.txt", 'a') as file:
                file.write("\n"+line)
    
    # On click method - Logs Button
    def OpenLogs(self):
        os.system('Notepad logs.txt')

    # On click method - Analyzed pictures Button
    def OpenAnomaliesDir(self):
        os.system('explorer temp')

    # On click function of Zip generation button. Generate a zip file with tested images and logs
    def GenerateZipFile(self):
        from datetime import date
        from os.path import basename

        today = date.today()

        old_model = basename(self.oldModelPath.get())
        new_model = basename(self.newModelPath)

        theme = old_model +'_VS_'+ new_model

        day = today.strftime("%m-%d-%y")
        zip_name = 'results/'+day+'_'+self.datasetPath.get()+'__'+theme
        zip_count = len(list(filter(lambda s: zip_name in "results/"+s, os.listdir("results/"))))

        # copy of all the tested pictures
        with ZipFile(zip_name+"__"+str(zip_count)+".zip", 'w') as zipObj2:
            zipObj2.write('logs.txt')
            for file in os.listdir('temp/old'):
                    zipObj2.write('temp/old/'+file, old_model+'/'+file)
            for file in os.listdir('temp/new'):
                    zipObj2.write('temp/new/'+file, new_model+'/'+file)
        # when finished, opens the directory
        os.system('explorer results')

if __name__ == '__main__':
    gui = GUI_FasterRCNN()