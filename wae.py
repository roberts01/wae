import os
import re
import subprocess as sp
from termcolor import colored, cprint
from view_extract import ExtractAB
from packaging import version


# Global Variables
# SDKVersion = ''
WhatsAppapkPath = 'WhatsApp-2.11.431.apk'
# SDPath = '' # Internal storage.
# versionName = ''
# contentLength = '' # To check if APK even exists at a given path to download!
appURLWhatsCryptCDN = 'https://whatcrypt.com/WhatsApp-2.11.431.apk'
isJAVAInstalled = False

# Global command line helpers
#adb = 'adb -s ' + ADBSerialId
adb = 'adb'
delete = 'rm -r -f'
tmp = 'tmp/'
confirmDelete = ''
grep = 'grep'
curl = 'curl'
extracted = 'extracted/'

#former CustomCI.py
def CustomInput(textToInput, color = 'green', attr=[]): 
    return input(colored(textToInput, color, attrs=attr)).casefold()

def CustomPrint(textToPrint, color = 'green', attr=[]): 
    cprint(textToPrint, color, attrs=attr)

def Exit():
    CustomPrint('\nExiting...', 'green')
    os.system('adb kill-server')
    quit()

#former ADBDeviceSerialId.py

# Global command line helpers
currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))

cmd = adb + ' devices'
# Kill server before getting list to avoid daemon texts.
os.system(adb + ' kill-server')
os.system(adb + ' start-server')
proc = sp.Popen(cmd.split(), stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=False)
output, error = proc.communicate()
output = output.decode('utf-8')
error = error.decode('utf-8')

if len(output) == 0 or error:
    output = None
    CustomPrint(error, 'red')
    Exit()
else:
    output = [x.strip() for x in output.split('\n') if len(x.strip()) > 0]

if(len(output) == 1):
    CustomPrint('Could not find any connected device. Is USB Debugging on?', 'red')
    return ''

deviceToConnect = None
i = 1
if(len(output) == 2):
    if(output[1].split()[1] == 'offline'):
        CustomPrint('Device is offline, try turning off USB debugging and turn on again.', 'yellow')
        Exit()
    if(output[1].split()[1] == 'unauthorized'):
        CustomPrint('Device unauthorized. Please check the confirmation dialog on your device.', 'red')
        Exit()
    return output[1].split()[0]

CustomPrint(output[0])
print('\n')
if deviceToConnect is None:
    for device in output[1:]:
        name = adb + ' -s ' + \
        device.split()[0] + ' shell getprop ro.product.model'
        CustomPrint(str(i) + '. ' + device.split()[0] + '  ' + device.split()[1] + '  ' + sp.getoutput(name).strip())
        i += 1

while deviceToConnect is None:
    deviceIndex = int(CustomInput('Enter device number (for ex : 2) : '))
    if deviceIndex <= 0 or deviceIndex + 1 > len(output):
        continue
    deviceToConnect = output[deviceIndex]

if(deviceToConnect.split()[1] == 'offline'):
    CustomPrint('Device is offline, try turning off USB debugging and turn on again.', 'yellow')
    Exit()
if(deviceToConnect.split()[1] == 'unauthorized'):
    CustomPrint('Device unauthorized. Please check the confirmation dialog on your device.', 'red')
    Exit()
ADBSerialId = deviceToConnect.split()[0]

def CheckJAVA() : 
    JAVAVersion = re.search('(?<=version ")(.*)(?=")', str(sp.check_output('java -version'.split(), stderr=sp.STDOUT))).group(1)
    
    if(JAVAVersion):
        isJAVAInstalled = True 
    else:
        isJAVAInstalled = False
        
    if (isJAVAInstalled): 
        CustomPrint('Found Java installed on system. Continuing...')
        return isJAVAInstalled
    else: 
        CustomPrint('It looks like you don\'t have JAVA installed on your system. Please install it first.')
        Exit()

#BEGINNING-------------------------------------------------
    
if __name__ == "__main__":
    os.system('clear')

   
    isJAVAInstalled = CheckJAVA()
    
    CustomPrint('Temporarily continuing without Java.')
    
    #USB Mode
    #Former Termux.py
    #def TermuxMode(ADBSerialId)
    _deviceName= 'adb -s ' + ADBSerialId + ' shell getprop ro.product.model'
    CustomPrint('Connected to ' + re.search("(?<=b')(.*)(?=\\\\n)", str(check_output(_deviceName.split()))).group(1) , 'green')

    _sdkVersionText = 'adb -s ' + ADBSerialId + ' shell getprop ro.build.version.sdk'
    SDKVersion = int(re.search('[0-9]{2,3}', str(check_output(_sdkVersionText.split()))).group(0))
    if (SDKVersion <= 13) :
        CustomPrint('Unsupported device. This method only works on Android v4.0 or higer.', 'green')
        CustomPrint('Cleaning up temporary direcory.', 'green')
        os.system('rm -r -f tmp/*')
        Exit()
        
    _waPathText = 'adb -s ' + ADBSerialId + ' shell pm path com.whatsapp'
    WhatsAppapkPath = re.search('(?<=package:)(.*)(?=apk)', str(check_output(_waPathText.split()))).group(1) + 'apk'
    if not (WhatsAppapkPath): 
        CustomPrint('Looks like WhatsApp is not installed on device.')
        Exit()
    #SDPath = re.search("(?<=b')(.*)(?=\\\\n)", str(check_output('adb shell "echo $EXTERNAL_STORAGE"'.split()))).group(1)
    contentLength = int(re.search("(?<=Content-Length:)(.*[0-9])(?=)", str(check_output('curl -sI https://whatcrypt.com/WhatsApp-2.11.431.apk'.split()))).group(1))
    _versionNameText = 'adb -s ' + ADBSerialId + ' shell dumpsys package com.whatsapp'
    versionName = re.search("(?<=versionName=)(.*?)(?=\\\\n)", str(check_output(_versionNameText.split()))).group(1)
    CustomPrint('WhatsApp Version' + versionName + ' installed on device') 
    ACReturnCode = 1
    
    #If works, start Whatapp operations
    if ACReturnCode==1:
        
        #Backup WhatsApp Apk
        if(SDKVersion > 11):
            os.system(adb + ' shell am force-stop com.whatsapp')
        else:
            os.system(adb + ' shell am kill com.whatsapp')
            
        CustomPrint('Backing up WhatsApp ' + versionName + ' apk, the one installed on device to ' + tmp + 'WhatsAppbackup.apk')
        os.system(adb + ' pull ' + WhatsAppapkPath + ' ' + tmp + 'WhatsAppbackup.apk')
        CustomPrint('Apk backup complete.')

        #UninstallWhatsApp
        if(SDKVersion >= 23) :
            try : 
                CustomPrint('Uninstalling WhatsApp, skipping data.')
                os.system(adb + ' shell pm uninstall -k com.whatsapp')
                CustomPrint('Uninstalled.')
            except Exception as e : 
                CustomPrint('Could not uninstall WhatsApp.')
                CustomPrint(e)
                Exit()

        #InstallLegacyWhatsapp
        CustomPrint("installing Legacy WhatsApp v2.11.431...")
        if(SDKVersion >= 17) :
            os.system(adb + ' install -r -d WhatsApp-2.11.431.apk')
        else : 
            os.system(adb + ' install -r WhatsApp-2.11.431.apk')
        CustomPrint('Installation Complete.')

        #Backup WhatsApp Data as .ab File
        CustomPrint('Backing up WhatsApp data as ' + tmp + 'whatsapp.ab. May take time, don\'t panic.')
        try : 
            
            if(SDKVersion >= 23):
                os.system(adb + ' backup -f '+ tmp + 'whatsapp.ab com.whatsapp')
            else:
                os.system(adb + ' backup -f '+ tmp + 'whatsapp.ab -noapk com.whatsapp')
        except Exception as e : 
            CustomPrint(e)
        CustomPrint('Done backing up data.')

        #Reinstall WhatsApp
        CustomPrint('Reinstallting original WhatsApp...')
        try : 
            os.system(adb + ' install -r -d ' + tmp + 'WhatsAppbackup.apk')
        except Exception as e : 
            print(e)
            CustomPrint('Could not install WhatsApp, install by running \'restore_whatsapp.py\' or manually installing from Play Store.\nHowever if it crashes then you have to clear storage/clear data from settings => app settings => WhatsApp.')    

        CustomPrint('Our work with device has finished.')
        
        ExtractAB(isJAVAInstalled)
        CustomPrint('Extraction is not possible on termux as of now. I have to back \'whatsapp.ab\' up in \'extracted\' folder.')
        userName = CustomInput('Enter a reference name for this user (Remeber this name for later). : ') or 'user'
        os.mkdir(extracted + userName) if not (os.path.isdir(extracted + userName)) else CustomPrint('Folder already exists.')
        
        # copy from to here.
        os.system('mv ' + tmp + 'whatsapp.ab ' + extracted + userName + '/whatsapp.ab')
        CustomPrint('Done copying, deleting from \'tmp\' folder. Now run \'view_extract.py\' from computer.')
        os.system('rm -r -f ' + tmp + 'whatsapp.ab') 
    else:
        Exit()