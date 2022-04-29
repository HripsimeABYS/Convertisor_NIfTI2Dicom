from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
# from functions import  convert_nifti_to_dicom
from glob import glob
import dicom2nifti
import os
import numpy as np
import pydicom
from PIL import Image
import os
import SimpleITK as sitk
from tqdm import tqdm
import time


    

def writeSlices(series_tag_values, new_img, i, out_dir):
    image_slice = new_img[:,:,i]
    writer = sitk.ImageFileWriter()
    writer.KeepOriginalImageUIDOn()

    # Tags shared by the series.
    list(map(lambda tag_value: image_slice.SetMetaData(tag_value[0], tag_value[1]), series_tag_values))

    # Slice specific tags.
    image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d")) # Instance Creation Date
    image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S")) # Instance Creation Time

    # Setting the type to CT preserves the slice location.
    image_slice.SetMetaData("0008|0060", "CT")  # set the type to CT so the thickness is carried over

    # (0020, 0032) image position patient determines the 3D spacing between slices.
    image_slice.SetMetaData("0020|0032", '\\'.join(map(str,new_img.TransformIndexToPhysicalPoint((0,0,i))))) # Image Position (Patient)
    image_slice.SetMetaData("0020,0013", str(i)) # Instance Number

    # Write to the output directory and add the extension dcm, to force writing in DICOM format.
    writer.SetFileName(os.path.join(out_dir,'slice' + str(i).zfill(4) + '.dcm'))
    writer.Execute(image_slice)


def convert_nifti_to_dicom(in_dir, out_dir):
    new_img = sitk.ReadImage(in_dir) 
    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")

    direction = new_img.GetDirection()
    series_tag_values = [("0008|0031",modification_time), # Series Time
                    ("0008|0021",modification_date), # Series Date
                    ("0008|0008","DERIVED\\SECONDARY"), # Image Type
                    ("0020|000e", "1.2.826.0.1.3680043.2.1125."+modification_date+".1"+modification_time), # Series Instance UID
                    ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6],# Image Orientation (Patient)
                                                        direction[1],direction[4],direction[7])))),
                    ("0008|103e", "Created-SimpleITK")] # Series Description

    # Write slices to output directory
    list(map(lambda i: writeSlices(series_tag_values, new_img, i, out_dir), range(new_img.GetDepth())))



def progress_bar(master):
    progress_bar = Progressbar(master, mode='determinate', orient='horizontal', length=500)
    progress_bar.pack(pady=(20,0))

    return progress_bar

def call_home_page():
    root.geometry('700x500')
    home_page = Frame(root, bg=bg)
    home_page.grid(row=0, column=0, sticky='nsew')

    title = Label(home_page, text='NIfTI vers Dicom', bg=bg, fg='black', font='Arial 35 bold')
    title.pack(pady=(20,0))

    buttons_frame = Frame(home_page, bg=bg)
    buttons_frame.pack(pady=(50,0))


    nifti_to_dicom_button = Button(buttons_frame, text='Sélectionner\nun\nfichier', font='none 20 bold', width=10, fg='#053047', command=nifti_to_dicom_page)
    nifti_to_dicom_button.grid(row=1, column=1, padx=(50,0), pady=(50,0))



def nifti_to_dicom_page():
    global text_message_n_d
    root.geometry('600x450')
    nifti_to_dicom = Frame(root, bg=bg)
    nifti_to_dicom.grid(row=0, column=0, sticky='nsew')

    title = Label(nifti_to_dicom, text='Nifti to Dicom', bg=bg, fg='#ffffff', font='Arial 35 bold')
    title.pack()

    open_buttons = Frame(nifti_to_dicom, bg=bg)
    open_buttons.pack(pady=(30,0))

    open_file = Button(open_buttons, text='Open File', font='none 20 bold', width=10, fg='#053047', command=call_open_file_nifti_dicom)
    open_file.grid(row=0, column=0, padx=(0,20))

    open_dir = Button(open_buttons, text='Open Dir', font='none 20 bold', width=10, fg='#053047', command=call_open_dir_nifti_to_dicom)
    open_dir.grid(row=0, column=1, padx=(20,0))

    convert_save = Button(nifti_to_dicom, text='Convert & Save', font='none 20 bold', fg='#053047', command=call_convert_save_nifti_to_dicom)
    convert_save.pack(pady=(40,0))

    text_message_n_d = Label(nifti_to_dicom,text='Choose file or dir', font='none 9', bg=bg, fg='#FFFFFF')
    text_message_n_d.pack(pady=(20,0))

    home_button = Button(nifti_to_dicom, text='Home', command=call_home_page, font='none 13 bold', width=10, fg='#053047')
    home_button.pack(pady=(40,20))

def call_open_file_nifti_dicom():
    global flag_nifti_dicom
    global in_path_nifti_dicom
    global text_message_n_d
    
    
    in_path_nifti_dicom = filedialog.askopenfilename()
    if in_path_nifti_dicom: 
        flag_nifti_dicom = 1
        text_message_n_d.config(text='You opened: \n' + in_path_nifti_dicom)

def call_open_dir_nifti_to_dicom():
    global flag_nifti_dicom
    global in_path_nifti_dicom
    global text_message_n_d

    in_path_nifti_dicom = filedialog.askdirectory()

    if in_path_nifti_dicom:
        flag_nifti_dicom = 2
        text_message_n_d.config(text='You opened: \n' + in_path_nifti_dicom, fg="#FF8000")

def call_convert_save_nifti_to_dicom():
    global text_message_n_d
    text_message_n_d.config(text='Converting...', fg="#FF8000")

    if flag_nifti_dicom == 1 and in_path_nifti_dicom:
        out_path = filedialog.askdirectory()
        if out_path:
            convert_nifti_to_dicom(in_path_nifti_dicom, out_path)
            text_message_n_d.config(text='Votre fichier est enregistré dans\n' + out_path + '.nii.gz')

    if flag_nifti_dicom == 2 and in_path_nifti_dicom:
        images = glob(in_path_nifti_dicom + '/*')
        out_path = filedialog.askdirectory()
        if out_path:
            for i, image in enumerate(images):
                text_message_n_d.config(text='Converting...', fg="#FF8000")
                o_path = out_path + '/' + os.path.basename(image)[:-7]
                if not os.path.exists(o_path): os.makedirs(o_path)

                convert_nifti_to_dicom(image, o_path)
                text_message_n_d.config(text='Vos dossiers sont enregistrés dans \n' + out_path)


##############################################################################
########################## This is the main function #########################
##############################################################################

if __name__ == '__main__':

    global in_path_nifti_dicom


    global flag_nifti_dicom 

    flag_nifti_dicom = 0


    bg = 'white'
    root = Tk()
    root.geometry('700x500')
    root.title('Convertiseur')
    root.iconbitmap('utils/logo.ico')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    call_home_page()

    root.mainloop()
    
