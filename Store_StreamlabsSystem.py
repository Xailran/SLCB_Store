#!/usr/bin/python
# -*- coding: utf-8 -*-
#Parent = Parent #pylint: disable=undefined-variable
"""Store script to purchase rewards for users"""
#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import json
import os
import datetime
import ctypes
import winsound

#---------------------------------------
# Script information
#---------------------------------------
ScriptName = "Store V2"
Website = "https://www.twitch.tv/Xailran"
Creator = "Xailran"
Version = "2.0.0"
Description = "Allow your viewers to spend points to buy items or perks that you create! This update is a big one!"

#---------------------------------------
# Versions
#---------------------------------------
"""
2.0.0 - Added list function, "session" item type, and sound functionality. "Help" messages are now customizable. Major code re-work
1.5.2 - Updated permission types
1.5.0 - Added "edit" function. Added "unique" item type. Added Discord functionality. 
1.4.1 - Changed !store info failed responses to follow whisper setting. Added easter egg function
1.4.0 - Added "Contribute" item type
1.3.0 - Added "delete" function
1.2.0 - Added Mixer and YT functionality
1.1.0 - Added "toggle" and "help" functions
1.0.0 - Initial Release!

Note: Only important updates are saved here. For more detailed version information, check the README.txt
"""

#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
LogFile = os.path.join(os.path.dirname(__file__), "Log.txt")
SoundPath = os.path.join(os.path.dirname(__file__), "sounds")
MessageBox = ctypes.windll.user32.MessageBoxW
MB_YES = 6
DelConf = "Reset"
sessionItems = set()
soundQueue = []

#---------------------------------------
# Settings functions
#---------------------------------------
def SetDefaults():
	"""Set default settings function"""
	winsound.MessageBeep()
	returnValue = MessageBox(0, u"You are about to reset the settings, "
								"are you sure you want to continue?"
							 , u"Reset settings file?", 4)

	if returnValue == MB_YES:
		Settings(None, None).Save(settingsFile)
		MessageBox(0, u"Settings successfully restored to default values!"
					  "\r\nMake sure to reload script to load new values into UI"
				   , u"Reset complete!", 0)

def ReloadSettings(jsonData):
	"""Reload settings on Save"""
	global MySet
	MySet.Reload(jsonData)

#---------------------------------------
# UI functions
#---------------------------------------
def OpenReadMe():
	"""Open the readme.txt in the scripts folder"""
	location = os.path.join(os.path.dirname(__file__), "README.txt")
	os.startfile(location)

def OpenFolder():
	"""Open Store Script Folder"""
	location = (os.path.dirname(os.path.realpath(__file__)))
	os.startfile(location)

def OpenSoundFolder():
    """Open specific sounds folder"""
    location = (os.path.dirname(os.path.realpath(__file__))) + "/sounds/"
    os.startfile(location)

def OpenLog():
	"""Open the Log.txt in the scripts folder"""
	location = os.path.join(os.path.dirname(__file__), "Log.txt")
	try:
		os.startfile(location)

	except WindowsError:
		with open(LogFile, "w") as f:
			f.write("")
		os.startfile(location)

def ResetLog():
	"""Reset Log.txt file"""
	winsound.MessageBeep(-1)
	returnValue = MessageBox(0, u"You are about to reset the log file "
								"are you sure you want to contine?"
							 , u"Reset log file?", 4)
	if returnValue == MB_YES:
		with open(LogFile, "w") as f:
			f.write("")
			MessageBox(0, u"Log file successfully reset."
					   , u"Log file reset!", 0)

#---------------------------------------
# Optional functions
#---------------------------------------
def IsOnCooldown(data, command):
	"""Handle cooldowns"""
	cooldown = Parent.IsOnCooldown(ScriptName, command)
	usercooldown = Parent.IsOnUserCooldown(ScriptName, command, data.User)
	caster = (Parent.HasPermission(data.User, "Caster", "") and MySet.castercd)

	if (cooldown or usercooldown) and caster is False:

		if MySet.usecd:
			cooldownDuration = Parent.GetCooldownDuration(ScriptName, command)
			userCDD = Parent.GetUserCooldownDuration(ScriptName, command, data.User)

			if cooldownDuration > userCDD:
				SendResp(data, MySet.oncooldown.format(data.UserName, cooldownDuration))

			else:
				SendResp(data, MySet.onusercooldown.format(data.UserName, userCDD))
		return False
	return True

def SendResp(data, message):
    """Sends message to Stream or discord chat depending on settings"""
    message = message.replace("$user", data.UserName)
    message = message.replace("$currencyname", Parent.GetCurrencyName())
    message = message.replace("$target", data.GetParam(1))

    if not data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendStreamMessage(message)

    if not data.IsFromDiscord() and data.IsWhisper():
        Parent.SendStreamWhisper(data.User, message)

    if data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendDiscordMessage(message)

    if data.IsFromDiscord() and data.IsWhisper():
        Parent.SendDiscordDM(data.User, message)

def HasPermission(data, permission, permissioninfo):
    """Return true or false depending on if the user has permission.
    Also sends permission response if user doesn't"""
    if not Parent.HasPermission(data.User, permission, permissioninfo):
        message = MySet.notperm.format(data.UserName, permission, permissioninfo)
        SendResp(data, message)
        return False
    return True

def MatchUsage(data, usageperm):
	"""Returns true if usage matches settings, otherwise returns false"""
	if usageperm == "All":
		return True
	if not data.IsFromDiscord():
		if usageperm == "Stream Both" or usageperm == "Stream Chat" and not data.IsWhisper() or usageperm == "Stream Whisper" and data.IsWhisper():
			return True
	elif usageperm == "Discord Both" or usageperm == "Discord Chat" and not data.IsWhisper() or usageperm == "Discord Whisper" and data.IsWhisper():
			return True
	else:
		return False
#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
	"""data on Load, required function"""
	global MySet
	MySet = Settings(Parent, settingsFile)
	global parent
	parent = Parent
	
def Execute(data):
	"""Required Execute data function"""
	if data.GetParam(0).lower() == MySet.command.lower():
		function = data.GetParam(1).lower()
		ItemID = data.GetParam(2)

		if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
			return	
		if data.IsFromDiscord() and not MySet.EnabledDiscord:
			Parent.Log(ScriptName,"Command used in discord, not enabled")
			return
		if MySet.onlylive and not Parent.IsLive():
			SendResp(data, MySet.respNotLive.format(data.UserName))
			return
		
        #Calls basic function
		if function == "":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			command = "StoreBasic"
			if IsOnCooldown(data, command):
				StoreBasic(data)
                
        #Calls add function	
		elif function == "add":
			if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
				return
			ItemType = ""
			if data.GetParam(2).lower() == "general":
				ItemType = "general"
			elif data.GetParam(2).lower() == "code":
				ItemType = "code"
				if data.IsFromYoutube():
					message = "Sorry, but due to the lack of a private messaging system on YouTube, the code item type cannot be used. Please see the README for more information."
					SendResp(data,message)
					return
			elif data.GetParam(2).lower() == "once" or data.GetParam(2).lower() == "once-off":
				ItemType = "once"
			elif data.GetParam(2).lower() == "contribute" or data.GetParam(2).lower() == "ctb" or data.GetParam(2).lower() == "cont":
				ItemType = "contribute"
			elif data.GetParam(2).lower() == "unique":
				ItemType = "unique"
			elif data.GetParam(2).lower() == "session" or data.GetParam(2).lower() == "stream":
				ItemType = "session"
			if ItemType != "":
				StoreAdd(data, ItemType)
			else:
				message = MySet.atsfailed
				SendResp(data, message)
				if not data.GetParam(2).lower() == "":
					message = "The valid item types are [General], [Code], [Once], [Unique], [Contribute/CTB], or [Session]"
					SendResp(data, message)

        #Calls log function
		elif function == "log":
			if not HasPermission(data, MySet.StoreLogPermission, MySet.StoreLogPermissionInfo):
				return
			if not MySet.stf:
				message = "The log function disabled is currently disabled in the UI"
				SendResp(data, message)
				return
			StoreLog(data)

		#Calls list function		
		elif function == "list":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			if not MySet.StoreListEnable:
				message = "The streamer currently has the list function disabled"
				SendResp(data, message)
				return
			command = "StoreList"
			if IsOnCooldown(data, command):
				StoreList(data, data.GetParam(2), command)

		#Calls info function
		elif function == "info":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			command = "StoreInfo"
			if IsOnCooldown(data, command):
				StoreInfo(data, ItemID, command)
	    
		#Calls edit function			
		elif function == "edit":
			if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
				return
			else:
				StoreEdit(data, ItemID, data.GetParam(3).lower(), data.GetParam(4))
		
        #Calls buy function
		elif function == "buy":
			if data.IsWhisper() and not MySet.StoreBuyWhisp:
				message = "Item purchases in whispers have been disabled sorry. Please try again in the chat"
				SendResp(data,message)
				return
			if ItemID == "all":
				if IsOnCooldown(data, "buyall"):
					EasterEggs(data, "buyall")
			else:
				Purchase(data, ItemID)
		
        #Calls toggle function		
		elif function == "toggle":
			if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
				return
			else:
				StoreToggle(data, ItemID)
		
        #Calls help function	
		elif function == "help":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			command = "StoreHelp"
			if IsOnCooldown(data, command):
				StoreHelp(data, command)
        
		#Calls delete function
		elif function == "delete":
			if not HasPermission(data, MySet.StoreDelPermission, MySet.StoreDelPermissionInfo):
				return
			elif not MySet.StoreDelEnable:
				message = "The delete function must be enabled in the UI before it can be used, due to the nature of what it does"
				SendResp(data, message)
			elif ItemID == "":
				message = "{0} -> [{1} delete #] is the required command format, where # is the item ID for an item you wish to delete".format(data.UserName,MySet.command)
				SendResp(data, message)
			else:
				StoreDelete(data, ItemID)
		
        #Calls inventory function
		elif function == "inventory" or function == "inv":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			elif not MySet.StoreInvEnable:
				message = "Sorry, the inventory system is currently disabled."
				SendResp(data, message)
				return
			command = "StoreInventory"
			if IsOnCooldown(data, command):
				StoreInventory(data)
		
        #No valid function found
		else:
			message = MySet.info.format(data.UserName, MySet.command.lower())
			SendResp(data, message)

def Tick():
	"""Required tick function"""
	if not Parent.IsOnCooldown(ScriptName, "sounds"):
		Parent.AddCooldown(ScriptName,"sounds",2)
		if soundQueue:
			playsound = soundQueue[0]
			if playsound == "playrandom":
				filelist = [filename for filename in os.listdir("path") if os.path.isfile(filename)]
				playsound = filelist[Parent.GetRandom(0,len(filelist))]
			if Parent.PlaySound(playsound, MySet.volume*0.01):
				soundQueue.pop(0)

def Unload():
	SessionEnded()

#---------------------------------------
# [Optional] Store functions
#---------------------------------------
def StoreBasic(data):
	"""Gives basic instructions for viewers, and gives amount of items in the store"""
	Parent.AddCooldown(ScriptName,"StoreBasic",MySet.timerCooldown)
	Parent.AddUserCooldown(ScriptName,"StoreBasic",data.User,MySet.timerUserCooldown)
	Path = os.path.join(os.path.dirname(__file__), "Items")
	message = MySet.listbase.format(len([name for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))]), MySet.command)
	SendResp(data,message)

def LoadItem(data, ItemID, trigger):
	"""Checks if item file exists, and then loads all item information."""
	try:
		int(ItemID)
	except:
		#If itemID is not a number
		message = MySet.info.format(data.UserName, MySet.command)
		if trigger == "info":
			if MySet.StoreInfoWhisp:
				if data.IsFromDiscord():
					Parent.SendDiscordDM(data.User, message)
				else:
					Parent.SendStreamWhisper(data.UserName,message)
			else:
				SendResp(data, message)
		elif trigger == "edit":
			message = "[{0} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, cost, permission, cooldown, code, or sound".format(MySet.command)
			SendResp(data, message)	
		else:
			SendResp(data, message)
		return False
	else:
		#Loads all item data
		ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
		if os.path.exists(ItemsPath):
			global ItemData
			ItemData = {}
			with codecs.open(ItemsPath, encoding="utf-8-sig", mode="r") as file:
				Item = [line.strip() for line in file]
				if len(Item) < 8:
					Item.append("None")
				ItemData["ID"] = ItemID
				ItemData["setting"] = Item[0]
				ItemData["name"] = Item[1]
				ItemData["type"] = Item[2]
				ItemData["cost"] = int(Item[4])
				ItemData["code"] = Item[6]
				ItemData["sound"] = Item[7]
				PermissionData = Item[3].split(" ")
				ItemData["permission"] = PermissionData[0]
				try:
					ItemData["permissioninfo"] = PermissionData[1]
				except:
					ItemData["permissioninfo"] = ""
				CooldownData = Item[5].split(" ")
				ItemData["cooldown"] = int(CooldownData[0])
				try:
					ItemData["usercooldown"] = int(CooldownData[1])
				except:
					ItemData["usercooldown"] = ItemData["cooldown"]
			return True
		#If item cannot be found
		else:
			if not trigger == "list":
				message = MySet.notavailable.format(data.UserName, ItemID)
				if trigger == "info":
					if MySet.StoreInfoWhisp:
						if data.IsFromDiscord():
							Parent.SendDiscordDM(data.User, message)
						else:
							Parent.SendStreamWhisper(data.UserName,message)
					else:
						SendResp(data, message)
				else:
					SendResp(data, message)
			return False

def StoreList(data, page, command):
	"""Based on settings in UI, will show a collection AKA page of basic item information"""
	#Sets variables
	trigger = "list"
	Path = os.path.join(os.path.dirname(__file__), "Items")
	itemList = [int(name.replace(".txt","")) for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))]
	itemList.sort()
	pageMax = -(-len(itemList)//MySet.StoreListNumber)
	#Checks for an incorrect data entry
	if page == "":
		message = "The format to use this command is [{0} list <page>], where page is a positive integer. There are {1} pages in total".format(MySet.command, pageMax)
		SendResp(data, message)
		return
	elif page.lower() == "all":
		if not MySet.StoreListShowAll:
			message = "Sorry, but <page> must be a number. [{0} list page]".format(MySet.command)
			SendResp(data, message)
			return
		if not MatchUsage(data, MySet.SLSAusage):
			message = MySet.incorrectusage.format(data.UserName, MySet.SLSAusage)
			SendResp(data, message)
			return
	else:
		try:
			page = abs(int(page))
		except:
			message = "Sorry, but <page> must be a number. [{0} list page]".format(MySet.command)
			SendResp(data, message)
			return
	if page == 0:
		message = "0 is an invalid page number. Defaulting to the first page available:"
		SendResp(data, message)
		page = 1
	elif page > pageMax and page != "all":
		message = "There are only {0} pages of items. Defaulting to the last page available:".format(pageMax)
		SendResp(data, message)
		page = pageMax
	#Grabs all items for the page
	message = "Format = Item Name (itemID, item cost). "
	if page == "all":
		startingitem = 0
		closingitem = len(itemList)
	else:
		startingitem = MySet.StoreListNumber*(page-1)
		closingitem = min(MySet.StoreListNumber*page, len(itemList))
	for x in range(startingitem, closingitem):
		LoadItem(data, itemList[x], trigger)
		if ItemData["setting"] == "Disabled" and not MySet.StoreListShowDisabled:
			continue
		message += "{0} ({1}, {2}). ".format(ItemData["name"], ItemData["ID"], ItemData["cost"])
	message += "Page {0}/{1}".format(page,pageMax)
	if MySet.StoreListWhisp:
		if data.IsFromDiscord():
			Parent.SendDiscordDM(data.User, message)
		else:
			Parent.SendStreamWhisper(data.UserName, message)
	else:
		SendResp(data, message)
	Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
	Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)

def StoreInfo(data, ItemID, command):
	"""Item information function"""
	trigger = "info"
	if LoadItem(data, ItemID, trigger):
		if ItemData["setting"] == "Disabled":
			message = MySet.notenabled.format(data.UserName, ItemData["ID"])
			SendResp(data, message)
		else:
			message = MySet.storeinfosuccess.format(data.UserName, ItemData["name"], ItemData["type"], ItemData["ID"], ItemData["cost"], Parent.GetCurrencyName())
			if MySet.StoreInfoWhisp:
				if data.IsFromDiscord():
					Parent.SendDiscordDM(data.User, message)
				else:
					Parent.SendStreamWhisper(data.UserName, message)
			else:
				Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
				Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
				SendResp(data, message)

def Purchase(data, ItemID):
	"""Checks that all conditions for purchase are met"""
	#Checks if item purchases are enabled
	if not MySet.purchaseallow:
		message = "The streamer has all item purchases disabled currently."
		SendResp(data, message)
		return
	#Checks if the item exists
	if  not LoadItem(data, ItemID, "buy"):
		return
	#Checks if item is disabled
	if ItemData["setting"] == "Disabled":
		message = MySet.notenabled.format(data.UserName, ItemID)
		SendResp(data, message)
		return
	#Check if the item is on cooldown
	command = "Item{0}".format(ItemData["ID"])
	if not IsOnCooldown(data, command):
		return
	#Checks if user has permission to buy items
	if not HasPermission(data, ItemData["permission"], ItemData["permissioninfo"]):
		return
	#Contribute type specifics
	if ItemData["type"] == "contribute":
		payment = data.GetParam(3)
		if not payment == "":
			try:
				payment = int(payment)
			except:
				message = "{0} -> Please use the format [{1} buy itemID amount] when buying a 'contribute' type item.".format(data.UserName, MySet.command)
				SendResp(data,message)
				return
		else:
			payment = ItemData["cost"]
		Contributions(data, ItemData, payment)
		return
	#Unique type specifics
	if ItemData["type"] == "unique":
		if data.User in ItemData["code"]:
			message = "{0} -> You have purchased this item before, so it is unavailable for you sorry".format(data.UserName)
			SendResp(data, message)
			return
	#Checks finished, start payment process
	if Parent.RemovePoints(data.User,data.UserName, ItemData["cost"]):
		PurchaseSuccess(data, ItemData)
	else:
		message = MySet.notenough.format(data.UserName, ItemData["cost"], Parent.GetCurrencyName(), Parent.GetPoints(data.UserName))
		SendResp(data, message)

def PurchaseSuccess(data, ItemData):
	"""Payment process for purchasing an item"""
	#Add cooldown to item
	command = "Item{0}".format(ItemData["ID"])
	Parent.AddCooldown(ScriptName, command, ItemData["cooldown"])
	Parent.AddUserCooldown(ScriptName,command, data.User, ItemData["usercooldown"])
	#Successful payment messages
	message = "Thanks for buying {0}. You now have {1} {2}".format(ItemData["name"], Parent.GetPoints(data.User), Parent.GetCurrencyName())
	if not data.IsFromYoutube():
		if data.IsFromDiscord():
			Parent.SendDiscordDM(data.User, message)
		else:
			Parent.SendStreamWhisper(data.UserName, message)
	else:
		SendResp(data, message)
	if ItemData["type"] == "contribute":
		message = "Thanks {0}, you've just paid the final amount of {1} {2} to purchase {3} for the stream!".format(data.UserName, ItemData["cost"], Parent.GetCurrencyName(), ItemData["name"])
	else:
		message = MySet.itempurchasesuccess.format(data.UserName, ItemData["name"], ItemData["cost"], Parent.GetCurrencyName())
	SendResp(data, message)
	if ItemData["type"] == "code":
		message = "Your code for redeeming {0} is {1}.".format(ItemData["name"], ItemData["code"])
		#Sends message as a whisper
		if data.IsFromDiscord():
			Parent.SendDiscordDM(data.User, message)
		else:
			Parent.SendStreamWhisper(data.UserName, message)
	#Special saving conditions
	if ItemData["type"] == "unique":
		ItemData["code"] = ItemData["code"] + data.User + "%#%"
	if ItemData["type"] in ["once", "code", "contribute", "session"]:
		ItemData["setting"] = "Disabled"
		if ItemData["type"] == "session":
			global sessionItems
			sessionItems.add(ItemData["ID"])
	if MySet.DeleteOnRedeemCode and ItemData["type"] == "code":
		ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemData["ID"]))
		if os.path.exists(ItemsPath):
			os.remove(ItemsPath)
		else:
			Parent.Log(ScriptName, "Something went wrong! Please send Xailran a screenshot of this in discord, and give as much information as you can about what happened beforehand")
	else:
		SaveItem(ItemData)
	#Plays sound
	if ItemData["sound"] != "None":
		sound = os.path.join(SoundPath, ItemData["sound"])
		soundQueue.append(sound)
	else:
		if MySet.enableSounds:
			if MySet.randomSounds:
				sound = "playrandom"
			else:
				sound = os.path.join(SoundPath, MySet.soundFile)
			soundQueue.append(sound)

	#Saves to log
	if MySet.stf:
		textline = MySet.textline.format(data.UserName, ItemData["name"], ItemData["cost"], Parent.GetCurrencyName(), datetime.datetime.now().strftime("Date: %d/%m-%Y Time: %H:%M:%S"))
		with codecs.open(LogFile, "a", "utf-8") as f:
			f.write(u"" + textline + "\r\n")
	
def SessionEnded():
	"""Changes all session items to be enabled, ready for the next session"""
	global sessionItems
	for x in sessionItems:
		LoadItem("", x, "endsession")
		ItemData["setting"] = "Enabled"
		SaveItem(ItemData)

def Contributions(data, ItemData, payment):
	"""Process for registering contributions to contribute type items"""
	#If user is attempting to pay full amount/excess of item cost
	if payment > ItemData["cost"]:
		message = "{0} -> There are only {1} {2} remaining on this item. Reducing payment amoutn from {3} to {1}".format(data.UserName, str(ItemData["Cost"]), Parent.GetCurrencyName(), str(payment))
		SendResp(data, message)
		payment = ItemData["cost"]
	#Adjust remaining cost of contribute item
	if Parent.RemovePoints(data.User,data.UserName, payment):
		ItemData["cost"] = ItemData["cost"] - payment
		#If full amount is paid, resets price, and sends messages
		if ItemData["cost"] == 0:
			ItemData["cost"] = ItemData["code"]
			PurchaseSuccess(data, ItemData)
		#If item has not been finished
		else:
			message = "Thanks {0}! You have added {1} {2} to {3}, which now has {4} {2} remaining!".format(data.UserName, str(payment), Parent.GetCurrencyName(), ItemData["name"], ItemData["cost"])
			SendResp(data, message)
			SaveItem(ItemData)
	#If user can't afford to pay
	else:
		message = MySet.notenough.format(data.UserName, str(payment), Parent.GetCurrencyName(), Parent.GetPoints(data.UserName))
		SendResp(data, message)
		return

def StoreLog(data):
	"""Function to check last (x) purchases"""
	#Check if a number was given
	if data.GetParam(2) == "":
		logcount = 10
		SendResp(data, "No value given, assigning default value of 10")
	#Check if entry was a valid integer
	else:
		try:
			logcount = abs(int(data.GetParam(2)))
		except:
			message = "You must enter a number when using the log function. [{0} log #]".format(MySet.command)
			SendResp(data, message)
			return
		else:
			if logcount == 0:
				SendResp(data, "Invalid value of 0 was given, assigning default value of 10")
				logcount = 10
			if logcount > 20:
				message = "The log function has a maximum value of 20. Assigning value of 20"
				SendResp(data, message)
				logcount = 20
	#Prints set amount of log entries, in order of latest to oldest
	with codecs.open(LogFile, encoding="utf-8-sig", mode="r") as file:
		Item = [line.strip() for line in file]
		entries = len(Item) - 1
		for x in range(0,logcount):
			if (entries - x) < 0:
				message = "Tried to load more log data, but none exists!"
				SendResp(data, message)
				break
			message = Item[entries - x]
			SendResp(data, message)

def StoreToggle(data, ItemID):
	"""Toggles whether an item is enabled or disabled"""
	trigger = "toggle"
	if LoadItem(data, ItemID, trigger):
		if (ItemData["setting"].lower() == "disabled"):
			ItemData["setting"] = "Enabled"
			SaveItem(ItemData)
			message = "Item {0} has been successfully enabled!".format(ItemID)
			SendResp(data, message)
		elif (ItemData["setting"].lower() == "enabled"):
			ItemData["setting"] = "Disabled"
			SaveItem(ItemData)
			message = "Item {0} has been successfully disabled!".format(ItemID)
			SendResp(data, message)

def StoreDelete(data, ItemID):
	"""Deletes an item forever, freeing up its itemID to be used by the next item"""
	global DelConf
	trigger = "delete"
	#When item doesn't exist, reset the delete mode
	if not LoadItem(data, ItemID, trigger):
		DelConf = "Reset"
	#Process for when item exists
	else:
		#When delete command is set to this item
		if DelConf == ItemID:
			ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
			os.remove(ItemsPath)
			message = MySet.StoreDelMsg.format(ItemID,data.UserName)
			SendResp(data, message)
			DelConf = "Reset"
		#Sets delete command to this item
		else:
			DelConf = ItemID
			message = "Please send the delete command again to confirm deleting item {0}, {1}. DELETING AN ITEM CANNOT BE UNDONE".format(ItemID,ItemData["name"])
			SendResp(data, message)

def StoreAdd(data, ItemType):
	"""Adding items to store function"""
	#Checks if enough information has been provided
	Parameters = data.GetParamCount()
	if Parameters <= 4:
		message = MySet.atsfailed
		SendResp(data, message)
		return
	if Parameters <= 5 and ItemType == "code":
		message = "Command failed. Command format: {0} add code <cost/default> <ItemCode> <ItemName>. Make sure there are no spaces in the code, or it won't save properly!".format(MySet.command)
		SendResp(data, message)
		return
	#Establish data for the new item
	ItemData = {}
	ItemData["type"] = ItemType
	ItemData["setting"] = "Enabled"
	ItemData["permission"] = MySet.Permission
	ItemData["permissioninfo"] = MySet.PermissionInfo
	ItemData["sound"] = "None"
	if data.GetParam(3).lower() == "default" or data.GetParam(3).lower() == "dflt":
		ItemData["cost"] = MySet.atsdefaultcost
	else:
		try:
			ItemData["cost"] = int(data.GetParam(3))
		except:
			message = "<cost> must be a number, or the word default. {0} was entered instead".format(data.GetParam(3).upper())
			SendResp(data, message)
			return
	ItemData["cooldown"] = MySet.timerCooldown
	ItemData["usercooldown"] = MySet.timerUserCooldown
	#Sets code and name data for the item
	if ItemType in ["general", "once", "session"]:
		ItemData["code"] = "None"
		ItemData["name"] = SaveItemName(data, 4, Parameters)
	elif ItemType == "contribute":
		ItemData["code"] = ItemData["cost"]
		ItemData["name"] = SaveItemName(data, 4, Parameters)
	elif ItemType == "unique":
		ItemData["code"] = " "
		ItemData["name"] = SaveItemName(data, 4, Parameters)
	elif ItemType == "code":
		ItemData["code"] = data.GetParam(4)
		ItemData["name"] = SaveItemName(data, 5, Parameters)
	else:
		message = "What? How did you get this? That shouldn't be possible!! Please send Xailran a DM containing exactly what you did to trigger this"
		SendResp(data, message)
		return
	#Saves item data
	Path = os.path.join(os.path.dirname(__file__), "Items")
	ItemLimit = int(len([name for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))]) + 2)
	for x in range (1, ItemLimit):
		ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(x))
		if not os.path.exists(ItemsPath):
			ItemData["ID"] = x
			break
	#Brings all the data together, and saves the item
	SaveItem(ItemData)
	message = MySet.atssuccess.format(data.UserName, ItemData["name"], ItemData["ID"])
	SendResp(data, message)

def SaveItemName(data, StrtParameters, Parameters):
	"""Function for collecting full item name"""
	ItemName = ""
	for x in range(StrtParameters, Parameters):
		ItemName += (data.GetParam(x) + " ")
	return ItemName

def SaveItem(ItemData):
	SaveItemPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemData["ID"]))
	with codecs.open(SaveItemPath, "w", "utf-8") as f:
		filedata = ItemData["setting"] + "\r\n" + ItemData["name"] + "\r\n" + ItemData["type"] + "\r\n" + ItemData["permission"] + " " + ItemData["permissioninfo"] + "\r\n" + str(ItemData["cost"]) + "\r\n" + str(ItemData["cooldown"]) + " " + str(ItemData["usercooldown"]) + "\r\n" + str(ItemData["code"] + "\r\n" + ItemData["sound"])
		f.write(filedata)

def StoreEdit(data, ItemID, ItemEditType, ItemEditValue):
	trigger = "edit"
	if LoadItem(data, ItemID, trigger):
		#Changing item name
		if ItemEditType == "name" or ItemEditType == "itemname":
			#No item name set
			if ItemEditValue == "":
				message = "[{0} edit itemID name value]. Value is equal to the new name you wish to change the item to".format(MySet.command)
				SendResp(data, message)
				return
			#Item name set
			OldItemName = ItemData["name"]
			ItemEditValue = SaveItemName(data, 4, data.GetParamCount())
			message = "Success! {0} ({1}) has changed from '{2}' to '{3}'!".format(OldItemName, ItemID, ItemData["name"], ItemEditValue)
			ItemData["name"] = ItemEditValue
			SendResp(data, message)

		#Changing item type
		elif ItemEditType == "type":
			message = "Item types are core to how an item works, and it would be very easy for this to go wrong. Thus, editing item types has not been permitted"
			SendResp(data, message)

		#Changing item permission
		elif ItemEditType == "permission":
			ItemEditValue = ItemEditValue.lower()
			oldItemPermission = ItemData["permission"]
			oldItemPermissionInfo = ItemData["permissioninfo"]
			permittedValues = {"everyone":"Everyone", "regular":"Regular", "VIP exclusive":"VIP Exclusive", "vip+":"VIP+", "subscriber":"Subscriber", "gamewispsubscriber":"GameWispSubscriber", "moderator":"Moderator", "editor":"Editor", "caster":"Caster"}
			permittedSpecialValues = {"min_rank":"Min_Rank", "min_points":"Min_Points", "min_hours":"Min_Hours", "user_specific":"User_Specific"}
			if ItemEditValue in permittedValues:
				ItemData["permission"] = permittedValues[ItemEditValue]
			elif ItemEditValue in permittedValues:
				ItemData["permission"] = permittedValues[ItemEditValue]
				if data.GetParamCount() == 5:
					message = "When setting the {1} permission, you need to choose a value! [{0} edit itemID permission {1} value]".format(MySet.command, ItemData["permission"])
					SendResp(data,message)
					return
				if ItemData["permission"] == "Min_Rank":
					rank = ""
					for x in range(5, data.GetParamCount()):
						rank =+ data.GetParam(x)
					ItemData["permissioninfo"] = rank
				else:
					ItemData["permissioninfo"] = data.GetParam(5)
			else:
				values = permittedValues.values() + permittedSpecialValues.values()
				message = "The valid item permission values that can be changed through this command are: ".join(values)
				SendResp(data, message)
				return
			message = "Success! {0} ({1}) has changed from ({2}/{3}) to ({4}/{5})".format(ItemData["name"], ItemID, oldItemPermission, oldItemPermissionInfo, ItemData["permission"], ItemData["permissioninfo"])
			SendResp(data,message)\

		#Changing item cost
		elif ItemEditType == "cost" or ItemEditType == "cooldown" or ItemEditType == "usercooldown":
			try:
				ItemEditValue = int(ItemEditValue)
			except:
				message = "[{0} edit itemID {1} value] When editing the {1} of an item, you must enter a valid number as the value.".format(MySet.command, ItemEditType)
				SendResp(data, message)
				return
			else:
				if ItemEditValue < 0:
					message = "[{0} edit itemID {1} value] When editing the {1} of an item, you must enter a positive number as the value.".format(MySet.command, ItemEditType)
					SendResp(data, message)
					return
				if ItemEditType == "cost":
					message = "Success! {0} ({1}) has changed from {2} {3} to {4} {3}".format(ItemData["name"], ItemData["ID"], ItemData["cost"], Parent.GetCurrencyName(), ItemEditValue)
					SendResp(data, message)
					ItemData["cost"] = ItemEditValue
					if ItemData["type"] == "contribute":
						ItemData["code"] = ItemData["cost"]
				else:
					message = "Success! {0} ({1}) has changed from {2} seconds to {3} seconds".format(ItemData["name"], ItemID, ItemData[ItemEditType], ItemEditValue)
					SendResp(data, message)
					ItemData[ItemEditType] = ItemEditValue
		
		#Changing item code
		elif ItemEditType == "code":
			if ItemEditValue == "":
				message = "[{0} edit itemID code value]. Value is equal to the new code you wish to assign to the item. WARNING: This will delete the old code!".format(MySet.command)
				SendResp(data, message)
				return
			if not ItemData["type"] == "code":
				message = "Items with the '{0}' type don't have a code! Please try again with another item.".format(ItemData["type"])
				SendResp(data, message)
				return
			else:
				message = "Success! {0} ({1}) has changed from {2} to {3}".format(ItemData["name"], ItemData["ID"], ItemData["code"], ItemEditValue)
				SendResp(data, message)
				ItemData["code"] = ItemEditValue
		
		elif ItemEditType == "sound":
			if ItemEditValue == "":
				message = "[{0} edit itemID sound filename]. Filename must be in the format of 'name.mp3', or it won't play correctly".format(MySet.command)
				SendResp(data, message)
				return
			else:
				message = "Success! {0} ({1}) has changed from {2} to {3}".format(ItemData["name"], ItemData["ID"], ItemData["sound"], ItemEditValue)
				SendResp(data, message)
				ItemData["sound"] = ItemEditValue
		
		#ItemEditType not recognised
		else:
			message = "[{0} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, cost, permission, cooldown, code, or sound".format(MySet.command)
			SendResp(data, message)
			return
		#Save item data changes
		SaveItem(ItemData)

def StoreHelp(data, command):
	"""Adds a variety of help responses"""
	#Choosing which help message to send
	if data.GetParam(2) == "add":
		if data.GetParam(3).lower() == "general":
			message = MySet.helpmessageAddGeneral.format(data.UserName, MySet.command)
		elif data.GetParam(3).lower() == "once":
			message = MySet.helpmessageAddOnce.format(data.UserName, MySet.command)
		elif data.GetParam(3).lower() == "session":
			message = MySet.helpmessageAddSession.format(data.UserName, MySet.command)
		elif data.GetParam(3).lower() == "contribute" or data.GetParam(3).lower() == "ctb":
			message = MySet.helpmessageAddContribute.format(data.UserName, MySet.command)
		elif data.GetParam(3).lower() == "unique":
			message = MySet.helpmessageAddUnique.format(data.UserName, MySet.command)
		elif data.GetParam(3).lower() == "code":
			message = MySet.helpmessageAddCode.format(data.UserName, MySet.command)
			if MySet.StoreHelpWhisp:
				if data.IsFromDiscord():
					Parent.SendDiscordDM(data.User, message)
				else:
					Parent.SendStreamWhisper(data.UserName, message)
			else:
				SendResp(data, message)
			message = MySet.helpmessageAddCode2.format(data.UserName, MySet.command)
		else:
			message = MySet.helpmessageAdd.format(data.UserName, MySet.command, Parent.GetCurrencyName())
	elif data.GetParam(2) == "buy":
		message = MySet.helpmessageBuy.format(data.UserName, MySet.command)
	elif data.GetParam(2) == "info":
		message = MySet.helpmessageInfo.format(data.UserName, MySet.command)
	elif data.GetParam(2) == "list":
		message = MySet.helpmessageList.format(data.UserName, MySet.command)
	elif data.GetParam(2) == "log":
		message = MySet.helpmessageLog.format(data.UserName, MySet.command)
	elif data.GetParam(2) == "toggle":
		message = MySet.helpmessageToggle.format(data.UserName, MySet.command)
	elif data.GetParam(2) == "delete":
		message = MySet.helpmessageDelete.format(data.UserName, MySet.command)
	elif data.GetParam(2) == "edit":
		message = MySet.helpmessageEdit.format(data.UserName, MySet.command)
	else:
		message = MySet.helpmessageGeneral.format(data.UserName, MySet.command)
	"""Functions that apply to all help parameters"""
	if MySet.HelpCooldown:
		Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
		Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
	if MySet.StoreHelpWhisp:
		if data.IsFromDiscord():
			Parent.SendDiscordDM(data.User, message)
		else:
			Parent.SendStreamWhisper(data.UserName, message)
	else:
		SendResp(data, message)

def EasterEggs(data, EggType):
	"""Some (hopefully) fun easter eggs, that add no actual functionality"""
	if MySet.EggsEnabled:
		if EggType == "buyall":
			message = "Come on, isn't that just a LITTLE excessive {0}?".format(data.UserName)
			SendResp(data, message)
	Parent.AddCooldown(ScriptName, EggType, MySet.timerCooldown)
	Parent.AddUserCooldown(ScriptName, EggType, data.User,MySet.timerUserCooldown)
#---------------------------------------
# Classes
#---------------------------------------
class Settings:
	""" Loads settings from file if file is found if not uses default values"""

	# The 'default' variable names need to match UI_Config
	def __init__(self, parent, settingsFile=None):
		if settingsFile and os.path.isfile(settingsFile):
			with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
				self.__dict__ = json.load(f, encoding='utf-8-sig')
		else: #set variables if no custom settings file is found
			self.onlylive = False
			self.command = "!store"
			self.EnabledDiscord = True
			self.StoreInfoWhisp = True
			self.StoreHelpWhisp = False
			self.Permission = "Everyone"
			self.PermissionInfo = ""
			self.castercd = True
			self.usecd = True
			self.HelpCooldown = False
			self.timerCooldown = 2
			self.oncooldown = "{0} the command is still on cooldown for {1} seconds!"
			self.timerUserCooldown = 10
			self.onusercooldown = "{0} the command is still on user cooldown for {1} seconds!"
			self.purchaseallow = True
			self.StoreBuyWhisp = False
			self.atsdefaultcost = 5000
			self.StoreAddPermission = "Editor"
			self.StoreAddPermissionInfo = ""
			self.DeleteOnRedeemCode = False
			self.StoreListEnable = True
			self.StoreListWhisp = False
			self.StoreListNumber = 10
			self.StoreListShowAll = False
			self.StoreListShowDisabled = True
			self.SLSAusage = "Stream Chat"
			self.StoreDelEnable = False
			self.StoreDelPermission = "Caster"
			self.StoreDelPermissionInfo = ""
			self.stf = True
			self.StoreLogPermission = "Editor"
			self.StoreLogPermissionInfo = ""
			self.textline = "{4}: {0} - {1} - {2} {3}"
			self.StoreInvEnable = True
			self.StoreTradingEnable = True
			self.StoreTradingCut = 0
			self.enableSounds = False
			self.randomSounds = False
			self.soundFile = "name.mp3"
			self.volume = 50
			self.respNotLive = "Sorry {0}, but the stream must be live in order to use that command."
			self.info = "{0} -> Use [{1} info <#>] to learn about an item, or [{1} buy <#>] to buy an item!"
			self.itempurchasesuccess = "{0} successfully purchased {1} for {2} {3}!"
			self.notenough = "{0} -> you don't have the {1} {2} required to buy this item."
			self.notavailable = "{0} -> item {1} isn't an available item"
			self.notenabled = "{0} -> item {1} is currently disabled"
			self.notperm = "{0} -> you don't have permission to use this command. permission is: [{1} / {2}]"
			self.incorrectusage = "{0} -> That command is designated for use in the following location: {1}"
			self.listbase = "There are currently {0} items in the store. Use [{1} info <#>] to learn about an item, or [{1} buy <#>] to buy an item"
			self.atssuccess = "{1} (ID: {2}) has successfully been added by {0}!"
			self.atsfailed = "Command failed. Command format: !store add <ItemType> <cost/default> <ItemName>"
			self.storeinfosuccess = "{0} -> {1} ({2}) is available for {4} {5}"
			self.StoreDelMsg = "Item {0} has been successfully deleted by {1}"
			self.EggsEnabled = True
			self.helpmessageGeneral = "The available parameters for [{1} help <function>] are add, buy, delete, info, list, log, edit, and toggle"
			self.helpmessageBuy = "{0} -> Use [{1} buy #] to purchase an item. If the item has the 'contribute' type, you can put an amount to pay after specifying the item number"
			self.helpmessageInfo = "{0} -> Use [{1} info #] to get a detailed information message about item #!"
			self.helpmessageList = "Use [{1} list <page>] to see a collection of items at once, with their name, item number, and cost"
			self.helpmessageAdd = "[{1} add <ItemType> <cost/default> <ItemName>]. Add an item for viewers to purchase with {2}! You can also use [{1} toggle] to enable/disable an existing item in the store. Use {0} help add [general/once/code/contribute/unique] for more information."
			self.helpmessageAddGeneral = "[{1} add general <cost/default> <ItemName>] Use this function to add items that can be bought multiple times"
			self.helpmessageAddContribute = "[{1} add contribute <cost/default> <ItemName>] Use this function to add items that can everyone can work together to purchase. Can also use 'ctb' as a short form for contribute"
			self.helpmessageAddUnique = "[{1} add unique <cost/default> <ItemName>] Use this function to add items that can only be purchased once per user."
			self.helpmessageAddOnce = "[{1} add once <cost/default> <ItemName>] Use this function to add items that can only be purchased once"
			self.helpmessageAddSession = "[{1} add session <cost/default> <ItemName>] Use this function to add items that can only be purchased once per session. A session ends when the script is restarted, or the bot is closed."
			self.helpmessageAddCode = "[{1} add code <cost/default> <ItemCode> <ItemName>] use this function to add items that contain a code, so the bot can send a whisper containing the code. Code items can only be purchased once"
			self.helpmessageAddCode2 = "Make sure there are no spaces in the ItemCode, or it won't save properly!"
			self.helpmessageLog = "When you use [{1} log #], it will load the last # entries, and post them in chat. If no number is given, it will load the last 10 entries. If # is higher than the amount of entries, the bot will load as many as it can before returning an error message."
			self.helpmessageToggle = "Use [{1} toggle #] to enable or disable the purchase of an existing item! Useful if you have a once-off item that you want to make available, or you don't want a general item to be purchased for whatever reason"
			self.helpmessageEdit = "[{1} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, cost, permission, cooldown, or code"
			self.helpmessageDelete = "Use [{1} delete #] to completely remove an item from the system, and allow another item to take its item ID. Once deleted, it can't be undone, so use with caution!"

		self.parent = parent

	# Reload settings on save through UI
	def Reload(self, data):
		"""Reload settings on save through UI"""
		parent = self.parent
		self.__dict__ = json.loads(data, encoding='utf-8-sig')
		self.parent = parent
	
	def Save(self, settingsfile):
		""" Save settings contained within the .json and .js settings files. """
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
				json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
			with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
				f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
		except ValueError:
			MessageBox(0, u"Settings failed to save to file"
					   , u"Saving failed", 0)