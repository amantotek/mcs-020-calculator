#!/usr/bin/python3
# -*- coding: utf-8 -*-
VEERSION = "20240306_1504"
#mcs020.py
#Based on https://mcscertified.com/wp-content/uploads/2021/10/MCS-020.pdf procedure p15+ for Air Source Heat Pump
#Colours https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Color_Names.py

#import PySimpleGUI20201011 as psg
import PySimpleGUI as psg
import math

bStep4ByTable = True #As original MCS020 Note 4 page 21/25

#Steps
#1 62dBA
#2 Two reflective surfaces so Q4
#3 5.4m

l1 = psg.Text('MCS-020', key='-OUT-', font=('Arial Bold', 20), justification='center')

#Input data
la1 = psg.Text("Max dB of Heat Pump")
in1 = psg.Input('62', enable_events=True, key='KDdB', font=('Arial Bold', 20), size=(200,100), justification='left')
la2 = psg.Text("Reflective surfaces 1-3 (Q2 Q4 Q8)") #Table uses Q values
in2 = psg.Input('2', enable_events=True, key='KDrefl', font=('Arial Bold', 20), expand_x=True, justification='left')
la3 = psg.Text("Distance Heat Pump to Assessment Point 1m-30m") #Can be non integer in range 1 to 30
in3 = psg.Input('5.4', enable_events=True, key='KDm', font=('Arial Bold', 20), expand_x=True, justification='left')
la4 = psg.Text("Barrier: None=0 Partial=5 Full=10 Enter number")
in4 = psg.Input('0', enable_events=True, key='KBa', font=('Arial Bold', 20), expand_x=True, justification='left')

#Result textbox
Reesult = psg.Text("",font=('Arial Bold', 20), size=(0, 1), key='OUUTPUT')
UtSteps = psg.Multiline("",font=('Arial Bold', 12), size=(50, 4), key='KEYSTEPS') #Allow 3 lines 90,3 ok

#Buttons
b1 = psg.Button('GO', key='-OK-', font=('Arial Bold', 20))
b2 = psg.Button('Exit', font=('Arial Bold', 20))

la9 = psg.Text("Toggle between Original MCS Tables and Equation Driven")
sTableLabl = 'Replace MCS020 Tables with Equations'
sEqatnLabl = 'Revert to Original MCS020 Tables'
bu9 = psg.Button(sTableLabl, key='UEQ', font=('Arial Bold', 12))

layout = [ [l1], [la1, in1], [la2, in2], [la3, in3], [la4, in4], [b1], [Reesult], [UtSteps], [b2],[la9, bu9] ]
window = psg.Window('Air Source Heat Pump Sound Calculations', layout, size=(750, 800)) #2nd is vertical

#hrr = [[1, 2, 3], [4, 5, 6]]
#print(hrr[0][2]) #gives 3

#NOTE 4: DB DISTANCE REDUCTION (14 column table)
hrr = [[1,1.5,2,3,4,5,6,8,10,12,15,20,25,30],
[-8,-11,-14,-17,-20,-21,-23,-26,-28,-29,-31,-34,-36,-37]]

#NOTE 7: DECIBEL CORRECTION (STEP 9)
ArrStp9 = [3.0,2.5,2.1,1.8,1.5,1.2,1.0,0.8,0.6,0.5,0.4,0.3,0.3,0.2,0.2,0.1]

#Test
iRws = [0,3,6]
for yy in iRws:
  #range(6) is values 0 to 5.
  for xx in range(14):
    iTablVal = hrr[1][xx] + yy
    if yy > 0 and xx == 5:
      iTablVal -= 1 #anomaly
    print(iTablVal, end='');
  print()
  
#Make file like x y1 y2 y3
#print("File A")
sFilnm = 'hpMCS020Note4P21.txt'
sTmp = ""
for xx in range(14):
  sTablVal = str(hrr[0][xx])
  for yy in iRws:
    iyVal = hrr[1][xx] + yy
    if yy > 0 and xx == 5:
      iyVal -= 1 #anomaly
    sTablVal += " " + str(iyVal) # * -1) #So all +ve values
  print(sTablVal, end='')
  sTmp += sTablVal + "\n"
print()
with open(sFilnm, 'w+') as fz:
  fz.write(sTmp)
print("MCS020 p21 Note 4 Table is in {}".format(sFilnm))
  
def mToCol(fDist):  
  #Convert distance to column in table  
  for xx in range(14):
    ivl = hrr[0][xx]
    if fDist == ivl:
      return xx
    if fDist < ivl:
      return xx-1
    
def clearResults():
  #Clear results
  window['OUUTPUT'].update(value="") 
  window['KEYSTEPS'].update(value="")

def doStepFour(fMDist,i012):
  if bStep4ByTable == True:
    fDistReductn = doStepOriginalFour(fMDist,i012) #As original MCS020 Table 4
  else:
    fDistReductn = stepByEquatn4(fMDist,i012) #Use equation 
  return fDistReductn
  
def doStepOriginalFour(fMDist,i012):
  #Note 4: DB DISTANCE REDUCTION (STEP4)
  #fMDist is in range 1 thro 30 inclusive fitting into horizontal columns in Table
  #i012 is 0, 1 or 2 reflecting Q result 2, 4 or 8 down Table
  ixxCol = mToCol(fMDist) #Convert distance to column
  yy = i012 * 3 #So now 0, 3 or 6
  iTablVal = hrr[1][ixxCol] + yy #2nd row down with results
  if yy > 0 and ixxCol == 5:
    iTablVal -= 1 #anomaly
  print("{} {} {}  {}".format(fMDist,ixxCol,i012,iTablVal)) #For testing
  return iTablVal

#For Step 4 fit using 4PL Symetrical Sigmoidal with original 5,-21 for Q2
K1 = -84.13366
K2 = 29.64521
K3 = -84.13366
K4 = 9.496686
K5 = 0.3130866
def cuFit(fxx):
 return K1 + (K2 - K3)/( 1 + math.pow((fxx/K4),K5) ) #As float

def stepByEquatn4(fMDist,i012):
  #Note 4: DB DISTANCE REDUCTION (STEP4) but use equation not original MCS020 table
  #fMDist is in range 1 thro 30 inclusive fitting into horizontal columns in Table
  #i012 is 0, 1 or 2 reflecting Q result 2, 4 or 8 down Table
  fDBAdistanceReduction = cuFit(fMDist) #Worked for Q2
  if i012 == 1:
    fDBAdistanceReduction += 3 #For Q4
  elif i012 == 2:  
    fDBAdistanceReduction += 6 #For Q8
  return round(fDBAdistanceReduction,4) #For presentation curtail digits after decimal place 

def stepByEquatn9(fXin):
  #NOTE 7: DECIBEL CORRECTION (STEP 9)
  #y = 2.982714 - 0.4826954*x + 0.0284963*x^2 - 0.0005996798*x^3 Cubic Regression 3rd order polynomial
  Ka = 2.982714
  Kb = 0.4826954
  Kc = 0.0284963
  Kd = 0.0005996798
  fUt = Ka - Kb*fXin + Kc*(math.pow(fXin,2)) - Kd*(math.pow(fXin,3))
  return round(fUt,5)

#Test debug
#print("Debugxyz {}".format(stepByEquatn4(10,1)) )

def isfloat(string):
  try:
      float(string)
      return True
  except ValueError:
      return False
  
def sommary():
  #Input iRefl as 0, 1 or 2
  sBild = "S1 {}dB ".format(iDb)
  '''
  match str(iRefl):
    case "0":
      sBild += "S2 Q2 " #1 reflection
    case "1":
      sBild += "S2 Q4 " #2 reflections
    case "2":
      sBild += "S2 Q8 " #3 reflections
    case _:
      sBild += "err Stp2"
  '''
  if iRefl == 0:
    sBild += "S2 Q2 " #1 reflection
  elif iRefl == 1:
    sBild += "S2 Q4 " #2 reflection   
  elif iRefl == 2:
    sBild += "S2 Q8 " #3 reflection 
  else:
    sBild += "err Stp2"
  sBild += "S3 {}m ".format(fDm)
  sBild += "S4 {}dB ".format(iDbreduction)
  sBild += "S5 {}dB ".format(iBa)
  sBild += "S6 {}dB ".format(round(fStep6,4)) #(STEP 1) + (STEP 4) + (STEP 5)
  sBild += "S7 {}dB ".format(fBackgroundDb)    
  sBild += "S8 {}dB ".format(round(fStep8,4)) #(STEP 7) - (STEP 6)  
  sBild += "S9 Highest {}dB, Adj {}dB, Final {}dB(A) ".format(fHighest,fAdjustmentFigure,fFinal)
  if bStep4ByTable == False:
    sBild += "\nNB TABLES for STEPS 4 & 9 WERE REPLACED BY EQUATIONS"
  window['KEYSTEPS'].update(value=sBild)

def testCurvFits():
  sFilnm = "mcs020CurvFitTest.txt"
  sTmp = "For curve fitting original Step 4 table\n"
  #Note 4 hrr
  for xx in range(14):
    iTablVal = hrr[0][xx] #Distance from Heat Pump in metres. Step 3 result.
    iyVal = hrr[1][xx] #Q2 step result
    if xx == 5:
      iyVal -= 1 #anomaly
    sTmp += "{} {}\n".format(iTablVal,iyVal) 

  sTmp += "\nFor curve fitting original Step 9 table\n"
  for iXein in range(16): #0 to 15
    sTmp += "{} {}\n".format(iXein,ArrStp9[iXein])
  
  sTmp += "\nTest curve fit for Step 9"
  for iXein in range(16): #0 to 15
    sTmp += "{} {} {}\n".format(iXein,ArrStp9[iXein],stepByEquatn9(iXein))
  sTmp += "\n"  
  with open(sFilnm, 'w+') as fxz:
    fxz.write(sTmp)
  print( "Curve Fit Test results are in {}".format(sFilnm) )

#Testing
testCurvFits()
for y012 in range(3):
  doStepFour(1,y012)
  doStepFour(1.1,y012)
  doStepFour(1.5,y012)
  doStepFour(5.4,y012)
  doStepFour(29.999,y012)
  doStepFour(30,y012)
  print("------")
  
while True:
  event, values = window.read()
  #print(event, values)
  if event == '-OK-':
    sDb = values['KDdB']
    if sDb.isdigit():
       iDb  =  int(sDb) #Manufacturer max dBA

    sRefl = values['KDrefl'] #Reflections
    if sRefl.isdigit():
       iRefl  =  int(sRefl)-1 #so now 0, 1 or 2

    sDm = values['KDm'] #Metres       
    fDm  =  float(sDm) #NO IT CAN FLOAT!!!
    
    sKba = values['KBa'] #Barrier
    if sKba.isdigit(): 
      iBa  =  int(sKba)
      iBa = -iBa #as we entered +ve values
    #Step 4
    iDbreduction = doStepFour(fDm,iRefl) #All -ve numbers from Note 4 table (always negative integers in original table)
    #print("DeBUG1 {}".format(iDbreduction))
    #print("Stp1 {},Stp2 {},Stp3 {},Stp4 {},BarrierStp5 {}".format(iDb,iRefl,fDm,iDbreduction,iBa))
    #Step 5 gets barrier dB
    fStep6 = iDb+iDbreduction+iBa  #Steps 1+4+5 gives step 6
    fBackgroundDb = 40 #dB Step 7
    fStep8 = fBackgroundDb - fStep6 #(STEP 7) - (STEP 6)
    #print("Stp6 {},Stp7 {},Stp8 {}".format(fStep6,fBackgroundDb,fStep8))
    fAbsStp8 = abs(fStep8)
    #Find whichever is the higher dB from Step 6 and Step 7
    if fStep6 > fBackgroundDb:
      fHighest = fStep6
    else:  
      fHighest = fBackgroundDb
    #print("DeBUG2 {} {}".format(fAbsStp8,round(fAbsStp8)))
    if bStep4ByTable == True:  
      fAdjustmentFigure = ArrStp9[fAbsStp8] #fAbsStp8 was always an integer in original Step 4 table
    else:  
      #fAdjustmentFigure = ArrStp9[round(fAbsStp8)]
      fAdjustmentFigure = stepByEquatn9(fAbsStp8)
    fFinal = fHighest + fAdjustmentFigure
    #print("fHighest {},fAdjustmentFigure {},fFinal {}".format(fHighest,fAdjustmentFigure,fFinal))
    sRpt = "{} dB Pass if <= 42.0".format(fFinal)
    #window['OUUTPUT'].update(value="{} dB Pass if >= 42.0".format(fFinal))
    if fFinal > 42:
      sColr = 'red'
    else:
      sColr = 'green'
    window['OUUTPUT'].update(value=sRpt,text_color=sColr)
    sommary() #Make summary of each step

  if event == 'KDm' and values['KDm'] != "":
    clearResults()
    if isfloat(values['KDm']) == False:
      psg.popup("Must be number, decimals allowed")
      window['KDm'].update(values['KDm'][:-1]) #Blank entry input box
    
  if event == 'KDdB' and values['KDdB'] != "":
    clearResults()
    #window['OUUTPUT'].update(value="")
    if values['KDdB'].isdigit() == False:
      psg.popup("Must be number")
      window['KDdB'].update(values['KDdB'][:-1]) #Blank entry input box
    
  if event == 'KBa' and values['KBa'] != "":
    clearResults()
    if values['KBa'].isdigit() == False:
      psg.popup("Bad entry")
      window['KBa'].update(values['KBa'][:-1]) #Blank entry input box
         
  if event == 'KDrefl' and values['KDrefl'] != "":
    clearResults()
    #window['OUUTPUT'].update(value="")
    if values['KDrefl'][-1] not in ('123'):
      psg.popup("Bad entry")
      window['KDrefl'].update(values['KDrefl'][:-1]) #Blank entry input box

  if event == 'UEQ':
    #Toggle to use step 4 table or new equation
    clearResults()
    if bStep4ByTable == True:
      bStep4ByTable = False
      window['UEQ'].update(sEqatnLabl)
    else:
      bStep4ByTable = True
      window['UEQ'].update(sTableLabl)
         
  if event == psg.WIN_CLOSED or event == 'Exit':
      break
window.close()
