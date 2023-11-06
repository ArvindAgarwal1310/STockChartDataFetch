import cv2
import pytesseract
from pytesseract import Output
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import tkinter.font as font
from tkinter import ttk

# Create the main application window
app = tk.Tk()
app.title("Chart Screen")

# Create a label to display the loaded image
img_label = tk.Label(app, bg='#F0F0F0')

columns = ("Parameter", "Price", "Time")
table = ttk.Treeview(app, columns=columns, show="headings")

table.column("Parameter", width=250, anchor="center")
table.column("Price", width=250, anchor="center")
table.column("Time", width=250, anchor="center")
table.heading("Parameter", text="Parameter" , anchor="center")
table.heading("Price", text="Price", anchor="center")
table.heading("Time", text="Time", anchor="center")
style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 18,"bold"))

style.configure("Treeview.Cell", font=("Times New Roman", 20,"bold)"))



def display_image(fp,img_label): #Image is displayed on the Label
    if img_label.image:
        img_label.image = None
    image = Image.open(fp)
    max_width = app.winfo_screenwidth() * 0.75
    max_height = app.winfo_screenheight() * 0.75
    image.thumbnail((max_width, max_height))
    photo = ImageTk.PhotoImage(image)
    img_label.config(image=photo)
    img_label.image = photo




# Function to open a file dialog and load an image, send it to value_extraction to preprocess and extract data.
def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.ppm *.pgm")])
    if file_path:
        clear_table()
        value_extraction(file_path)
        image = Image.open(file_path)
        max_width = app.winfo_screenwidth() * 0.75
        max_height = app.winfo_screenheight() * 0.75
        image.thumbnail((max_width, max_height))
        photo = ImageTk.PhotoImage(image)
        img_label.config(image=photo)
        img_label.image = photo
        display_image("predicted_values_image.jpg",img_label)

#clears the pre existing data in the table.
def clear_table():
    for item in table.get_children():
        table.delete(item)


def add_values(ans_list):
    # Check if both price and parameter are provided
    if ans_list[0] and ans_list[1]:
        if (len(ans_list)==2):
            ans_list.append("unknown")
        table.insert("", "end", values=(ans_list[0], ans_list[1],ans_list[2]))

def createApp():

    # Maximize the application window
    app.state('zoomed')

    # Set a background color
    app.configure(bg='#F0F0F0')

    # Create a custom font
    custom_font = font.Font(size=12)

    # Create a button to open an image file with custom styling
    open_button = tk.Button(app, text="Select Image", command=open_image, font=custom_font, bg='#007ACC', fg='white')
    open_button.pack(pady=5)
    img_label.pack(pady=10)
    table.pack()
    app.mainloop()

#function to check if extracted string is a floating number
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

#important function to preprocess and extract data from image
def value_extraction(filepath):
    image = cv2.imread(filepath)
    BWimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    h,w,_=image.shape

    #Page segmentation mode and Engine mode
    myconfig=r"--psm 11 --oem 3" 
    '''
    #this section return individual characters, instead of string.
    boxes=pytesseract.image_to_boxes(image,config=myconfig)
    
    for box in boxes.splitlines():
        box=box.split(" ")
        print(box)
        image=cv2.rectangle(image,(int(box[1]),h-int(box[2])),(int(box[3]),h-int(box[4])),(0,255,0),2)
            '''

    data=pytesseract.image_to_data(BWimage,config=myconfig, output_type=Output.DICT)


    amount_boxes=len(data['text'])
    for i in range(amount_boxes):
        if float(data['conf'][i])> 45:
            (x,y,width,height)=(data['left'][i],data['top'][i],data['width'][i],data['height'][i])
            answers=[]
            if (("P" in data['text'][i]) or ("L" in data['text'][i])) and len(data['text'][i])<4:
                #print(data['text'][i])
                answers.append(data["text"][i])
                #print(x,y,width,height)
                x_axis, y_axis = 0,0
                for j in range(amount_boxes):
                    if(x_axis==1 and y_axis==1):
                        break
                    for k in range(20,100,10): #checking for the closest value in the price axis
                        if(y_axis==1):
                            break
                        if (x+40<data["left"][j])and (y>=data["top"][j]-k and y<=data["top"][j]+(k/5)) :
                            if(isfloat(data["text"][j]) and (float)(data["text"][j])>0.05):
                                #print(data['text'][j])
                                answers.append((data['text'][j]))
                                y_axis=1
                                break
                    for k in range(20,100,10): #checking for the closest value in the time axis
                        if(x_axis==1):
                            break
                        if (y<data["top"][j])and (x>=data["left"][j]-k and x<=data["left"][j]+k) :
                            if(isfloat(data["text"][j])):
                                #print(data['text'][j])
                                answers.append(data['text'][j])
                                x_axis=1
                                break
                if(len(answers)>=2):
                    add_values(answers)
            image=cv2.rectangle(image,(x,y),(x+width,y+height),(0,255,0),1)  #boxes are created alongside detected text
            image=cv2.putText(image, data['text'][i], (x+width-35,y+height+20),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2,cv2.LINE_AA)

    cv2.imwrite("predicted_values_image.jpg",image)
    #image is saved on the system, for further use and cross-check.

if __name__ == "__main__":
    createApp()
    print("done")
