#!/usr/bin/env python3

import pandas as pd
import os
from tkinter import filedialog, Tk
from re import search

class TerminationStringNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)
    def __str__(self):
        return f"{self.message}"



def get_header(file):
    full_file=open(file, 'r', errors='ignore')
    file_line1=full_file.readline()
    match=search(" END ", file_line1)
    if match:
        return file_line1[:(match.span()[1])]
    else:
        raise TerminationStringNotFound("The propper termination string was not found in the file header")


def header_cull(header_str):
    #Takes the full header and returns an array for each elemet in the header with descriptors and whitespace removed
    return([(" ".join(header_str[i:i+80].split())).split("/")[0] for i in range(0, len(header_str), 80)])
def string_cleaning(str):
    #Use to clean up values that are surrounded by ' ' in the fits header
    return str.split('=')[-1].split("'")[1].strip()
def string_cleaning_numbers(str):
    #Use to clean values that are presented "as is" in the fits header
    return str.split('=')[-1].strip()
def object_find(name, index):
    match = search(name, index)
    if match:
        return(index)

def get_data(header,file_name,comment):
    _Ra,_Dec,_date,_time,_lst,_amass,_scope,_inst,_f,_exp,_name,_comm=[None,None,None,None,None,None,None,None,None,None,None,None]
    for i in header:
        ra_match = search("OBJCTRA", i)
        if ra_match:
            _Ra = string_cleaning(i)
            _Ra_split = _Ra.split() #used to calculate LST later

        dec_match = search("OBJCTDEC", i)
        if dec_match:
            _Dec = string_cleaning(i)
        
        date_match = search("DATE-OBS", i)
        if date_match:
            _date,_time=string_cleaning(i).split("T")

        lst_match = search("OBJCTHA", i)
        if lst_match:
            _hr, _hr_remainder=string_cleaning(i).split('.')
            _min, _min_remainder=str(float('0.'+_hr_remainder)*60).split('.')
            _sec=float('0.'+_min_remainder)*60
            _hr,_min,_sec = [int(_Ra_split[0]) + int(_hr), int(_Ra_split[1]) + int(_min), float(_Ra_split[2]) + _sec ] # This will fail if RA  
            if _sec > 60:                                                                                              # is not found first
                _min=_min+1                                                                                            # and should be taken 
                _sec=_sec-60                                                                                           # outside of the for loop
            if _min > 60:                                                                                              # -----------------------
                _hr=_hr+1                                                                                              # -----------------------
                _min=_min-1                                                                                            # -----------------------
            _lst = ("%i:%i:%0.3f" % (_hr, _min, _sec))                                                                 # -----------------------

        amass_match = search("AIRMASS", i)
        if amass_match:
            _amass = (float(string_cleaning_numbers(i)))

        tscope_match = search("TELESCOP", i)
        if tscope_match:
            _scope = (string_cleaning(i))

        inst_match = search("INSTRUME", i)
        if inst_match:
            _inst = (string_cleaning(i))

        filter_match = search("FILTER", i)
        if filter_match:
            _f = (string_cleaning_numbers(i)[1:-3])
        
        exp_match = search("EXPOSURE", i) #or search("EXPTIME", i)
        if exp_match:
            _exp = (float(string_cleaning_numbers(i)))

    _name = file_name.split("/")[-1]
    _comm = comment

    return [_Ra,_Dec,_date,_time,_lst,_amass,_scope,_inst,_f,_exp,_name,_comm]



# Start of the Main Program===============================================
os.system('cls' if os.name=='nt' else 'clear')
print("FITs File header reader ver. 0.0.5")
comment=input("Default comment for all observations: ")
Tk().withdraw() # prevents an empty tkinter window from appearing

file_list = filedialog.askopenfilenames()

data=[]
for j in range(len(file_list)):
    header = get_header(file_list[j])
    header_split=header_cull(header)
    data.append(get_data(header=header_split,file_name=file_list[j],comment=comment))

ObsLog = pd.DataFrame(data=data,columns=['Ra','Dec','UT_date','UT_time','LST','AirMass','Telescope','Instrument','Filter','Exp_time','File_name','Comment'])
print(ObsLog)
save_loc = filedialog.asksaveasfilename(filetypes=[('CSV','*.csv')],defaultextension='.csv')
if save_loc == '':
    breakpoint
else:
    ObsLog.to_csv(save_loc)
