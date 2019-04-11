import random 
from ctypes import *
import struct 
import Globals 
import time 
import messageDefinitions as md
import Messenger as MR
from ctypes import * 
import socket 
import numpy as np 
import csv 

UDP_IP = Globals.SENDER_IP
UDP_PORT = Globals.SENDER_PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)


def enableGraphics(objectName, setVal):
    namePtr = (c_char_p) (addressof(objectName))
    message = md.M_GRAPHICS_SET_ENABLED()
    message.header.msg_type = c_int(md.GRAPHICS_SET_ENABLED)
    message.objectName = namePtr.value 
    message.enabled = c_int(setVal)
    packet = MR.makeMessage(message)
    sock.sendto(packet, (UDP_IP, UDP_PORT))

def removeEffect(effectName):
  rmField = md.M_HAPTICS_REMOVE_WORLD_EFFECT()
  rmField.header.msg_type = c_int(md.HAPTICS_REMOVE_WORLD_EFFECT)
  fieldNamePtr = (c_char_p) (addressof(effectName))
  rmField.effectName = fieldNamePtr.value
  packet = MR.makeMessage(rmField)
  sock.sendto(packet, (UDP_IP, UDP_PORT)) 


def freezeTool():
  freeze = md.M_HAPTICS_FREEZE_EFFECT()
  freeze.header.msg_type = c_int(md.HAPTICS_FREEZE_EFFECT)
  freezeName = create_string_buffer(b"freeze", md.MAX_STRING_LENGTH)
  freezeNamePtr = (c_char_p) (addressof(freezeName))
  freeze.effectName = freezeNamePtr.value
  packet = MR.makeMessage(freeze)
  sock.sendto(packet, (UDP_IP, UDP_PORT))

def unfreezeTool():
  unfreeze = md.M_HAPTICS_REMOVE_WORLD_EFFECT()
  unfreeze.header.msg_type = c_int(md.HAPTICS_REMOVE_WORLD_EFFECT)
  freezeName = create_string_buffer(b"freeze", md.MAX_STRING_LENGTH)
  freezeNamePtr = (c_char_p) (addressof(freezeName))
  unfreeze.effectName = freezeNamePtr.value 
  packet = MR.makeMessage(unfreeze)
  sock.sendto(packet, (UDP_IP, UDP_PORT))

def setup(saveFilePrefix):
  
  refVisc = np.arange(1.5, 3.5, 0.5)
  stepViscUp = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5]) #np.arange(0.1, 1.5, 0.1)
  stepViscDown = -1*np.array([0.05, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.25])#np.arange(0.05, 1.5, 0.1)
  steps = np.sort(np.concatenate([stepViscUp, stepViscDown]))
  fileName = saveFilePrefix
  logFilePath = fileName + "_data.csv"
  msgFilePath = fileName + "_msg.log"
  trialNum = 0
  field1Visc = 0.0
  field2Visc = 0.0 
  choice = ""
  
  fmsg = open(msgFilePath, 'ab')
  csvFile = open(logFilePath, 'a')
  fdata = csv.writer(csvFile)
  fmsg.flush()
  taskVars = { "refVisc": refVisc, "steps": steps,\
              "filepath": logFilePath, "msgFilePath": msgFilePath, "trialNum": trialNum,\
              "field1Visc": field1Visc, "field2Visc": field2Visc, "choice": choice,\
              "msgFile": fmsg, "logFile": fdata, "logFilePtr": csvFile }
  
  fdata.writerow(["Trial", "Reference Viscosity", "Compare Viscosity", "Choice"])

  obj1 = md.M_GRAPHICS_SHAPE_SPHERE()
  obj1.header.msg_type = c_int(md.GRAPHICS_SHAPE_SPHERE)
  obj1Name = create_string_buffer(b"field1Target", md.MAX_STRING_LENGTH)
  obj1NamePtr = (c_char_p) (addressof(obj1Name))
  obj1.objectName = obj1NamePtr.value
  obj1.radius = c_double(0.1)
  obj1.localPosition = (c_double * 3) (0.0, -1.0, 0.75)
  obj1.color = (c_float * 4) (4/250, 133/250, 209/250, 1)
  packet = MR.makeMessage(obj1)
  sock.sendto(packet, (UDP_IP, UDP_PORT))
  enableGraphics(obj1Name, 0)
  
  obj2 = md.M_GRAPHICS_SHAPE_SPHERE()
  obj2.header.msg_type = c_int(md.GRAPHICS_SHAPE_SPHERE)
  obj2Name = create_string_buffer(b"field2Target", md.MAX_STRING_LENGTH)
  obj2NamePtr = (c_char_p) (addressof(obj2Name))
  obj2.objectName = obj2NamePtr.value
  obj2.radius = c_double(0.1)
  obj2.localPosition = (c_double * 3) (0.0, 1.0, 0.75)
  obj2.color = (c_float * 4) (250/250, 194/250, 5/250, 1)
  packet = MR.makeMessage(obj2)
  sock.sendto(packet, (UDP_IP, UDP_PORT))
  enableGraphics(obj2Name, 0)
  
  return taskVars

def setBackground(red, green, blue):
  bg = md.M_GRAPHICS_CHANGE_BG_COLOR()
  bg.header.serial_no = c_int(1)
  bg.header.timestamp = c_double(0.1)
  bg.header.msg_type = c_int(md.GRAPHICS_CHANGE_BG_COLOR)
  bg.color = (c_float * 4) (red, green, blue, 1.0)
  packet = MR.makeMessage(bg)
  sock.sendto(packet, (UDP_IP, UDP_PORT))

def startEntry(options, taskVars):
  taskVars["msgFile"].flush()
  
  trialStart = md.M_TRIAL_START()
  trialStart.header.msg_type = c_int(md.TRIAL_START)
  packet = MR.makeMessage(trialStart)
  sock.sendto(packet, (UDP_IP, UDP_PORT))
  taskVars["msgFile"].write(packet)
  
  freezeTool()

  taskVars["trialNum"] = taskVars["trialNum"] + 1
  taskVars["choice"] = -1
  #print("Trial " + str(taskVars["trialNum"]))
  setBackground(0.0, 0.0, 0.0)
  obj1Name = create_string_buffer(b"field1Target", md.MAX_STRING_LENGTH)
  obj2Name = create_string_buffer(b"field2Target", md.MAX_STRING_LENGTH)
  enableGraphics(obj1Name, 0)
  enableGraphics(obj2Name, 0)
  time.sleep(1)
  
  return "next"

def field1Entry(options, taskVars):
  unfreezeTool()
  
  setBackground(4.0, 133.0, 209.0)
  field1Visc = random.choice(taskVars["refVisc"])
  taskVars["field1Visc"] = field1Visc
  #print("Reference Viscosity: ", field1Visc)
  
  field1 = md.M_HAPTICS_VISCOSITY_FIELD()
  field1.header.msg_type = c_int(md.HAPTICS_VISCOSITY_FIELD)
  field1Name = create_string_buffer(b"field1", md.MAX_STRING_LENGTH)
  field1NamePtr = (c_char_p) (addressof(field1Name))
  field1.effectName = field1NamePtr.value 
  field1.viscosityMatrix = (c_double * 9) (-1*field1Visc, 0.0, 0.0,\
                                           0.0, -1*field1Visc, 0.0,\
                                           0.0, 0.0, -1*field1Visc)
  packet = MR.makeMessage(field1)
  sock.sendto(packet, (UDP_IP, UDP_PORT))
  taskVars["msgFile"].flush()
  taskVars["msgFile"].write(packet)

  startTime = time.time()
  red = 4.0 
  green = 133.0
  blue = 209.0 
  while time.time() - startTime < 3:
    increment = round((3.0-(time.time()-startTime))/3.0, 2)
    redF = round(red*increment, 2)
    greenF = round(green*increment, 2)
    blueF = round(blue*increment, 2)
    setBackground(redF, greenF, blueF)
    time.sleep(0.1)
  return "next"

def intermediateEntry(options, taskVars):
  setBackground(0.0, 0.0, 0.0)
  time.sleep(0.001)
  freezeTool()
  fieldName = create_string_buffer(b"field1", md.MAX_STRING_LENGTH)
  removeEffect(fieldName)
  time.sleep(0.5)
  return "next"

def field2Entry(options, taskVars):
  unfreezeTool()
  setBackground(250.0, 194.0, 5.0)
  field2Visc = round(taskVars["field1Visc"] + random.choice(taskVars["steps"]), 2)
  taskVars["field2Visc"] = field2Visc 
  #print("Field Viscosity: ", taskVars["field2Visc"])
  
  field2 = md.M_HAPTICS_VISCOSITY_FIELD()
  field2.header.msg_type = c_int(md.HAPTICS_VISCOSITY_FIELD)
  field2Name = create_string_buffer(b"field2", md.MAX_STRING_LENGTH)
  field2NamePtr = (c_char_p) (addressof(field2Name))
  field2.effectName = field2NamePtr.value 
  field2.viscosityMatrix = (c_double * 9) (-1*field2Visc, 0.0, 0.0,\
                                           0.0, -1*field2Visc, 0.0,\
                                           0.0, 0.0, -1*field2Visc)
  packet = MR.makeMessage(field2)
  sock.sendto(packet, (UDP_IP, UDP_PORT))
  taskVars["msgFile"].flush()
  taskVars["msgFile"].write(packet)
  
  sameName = create_string_buffer(b"field1Target", md.MAX_STRING_LENGTH)
  diffName = create_string_buffer(b"field2Target", md.MAX_STRING_LENGTH)
  enableGraphics(sameName, 1)
  enableGraphics(diffName, 1)

  red = 250.0 
  green = 194.0 
  blue = 5.0 
  startTime = time.time()
  prevTime = time.time()
  while time.time() - startTime < 3:
    if time.time() - prevTime > 0.1:
      increment = round((3.0-(time.time()-startTime))/5.0, 3)
      redF = round(red*increment, 2)
      greenF = round(green*increment, 2)
      blueF = round(blue*increment, 2)
      setBackground(redF, greenF, blueF)
      prevTime = time.time()
    if np.abs(Globals.CHAI_DATA.posY - 1.0) < 0.12 and np.abs(Globals.CHAI_DATA.posZ - 0.75) < 0.12:
      taskVars["choice"] = 2
      return "next"
    elif np.abs(Globals.CHAI_DATA.posY + 1.0) < 0.12 and np.abs(Globals.CHAI_DATA.posZ - 0.75) < 0.12:
      taskVars["choice"] = 1 
      return "next"
    time.sleep(0.01)
  return "next"

def decisionEntry(options, taskVars):
  fieldName = create_string_buffer(b"field2", md.MAX_STRING_LENGTH)
  removeEffect(fieldName)

  decisionMade = False
  if taskVars["choice"] != -1:
    decisionMade = True
  
  setBackground(0.0, 0.0, 0.0)
  while decisionMade == False:
    if np.abs(Globals.CHAI_DATA.posY - 1.0) < 0.12 and np.abs(Globals.CHAI_DATA.posZ - 0.75) < 0.12:
      decisionMade = True
      taskVars["choice"] = 2 
    elif np.abs(Globals.CHAI_DATA.posY + 1.0) < 0.12 and np.abs(Globals.CHAI_DATA.posZ - 0.75) < 0.12:
      decisionMade = True
      taskVars["choice"] = 1 
    
  taskVars["logFile"].writerow([taskVars["trialNum"], taskVars["field1Visc"],\
                    taskVars["field2Visc"], taskVars["choice"]])
  
  trialEnd = md.M_TRIAL_END()
  trialEnd.header.msg_type = md.TRIAL_END
  packet = MR.makeMessage(trialEnd)
  sock.sendto(packet, (UDP_IP, UDP_PORT))
  taskVars["msgFile"].flush()
  taskVars["msgFile"].write(packet)

  taskControlPtr = taskVars["taskControl"]
  for k in taskVars.keys():
    if k != "taskControl":
      taskControlPtr.sessionInfo[k] = taskVars[k]
  taskControlPtr.addNode()
  return "next"
