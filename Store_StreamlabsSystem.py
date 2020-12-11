#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
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
ScriptName = "Store"
Website = "https://www.twitch.tv/Xailran"
Creator = "Xailran"
Version = "1.4.0"
Description = "Allow your viewers to spend points to buy items or perks that you create!"

"""
Huge thanks to Castorr91, for without his help, this script would not exist.
Thanks are also due to Bare7a and Mopioid. I appreciate all the assistance you both gave me!
Finally, thank you to anyone who has given/gives feedback or helps me find bugs!
"""

#---------------------------------------
# Versions
#---------------------------------------
"""
1.4.0 - Added "Contribute" item type
1.3.0 - Added "delete" function
1.2.0 - Added Mixer and YT functionality
1.1.0 - Added "toggle" and "help" functions
1.0.0 - Initial Release!

Note: Only important updates are saved here. For more details, check the README.txt
"""
#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
LogFile = os.path.join(os.path.dirname(__file__), "Log.txt")
DelConfFile = os.path.join(os.path.dirname(__file__), "DelConf.txt")
MessageBox = ctypes.windll.user32.MessageBoxW
MB_YES = 6

#---------------------------------------
# Settings functions
#---------------------------------------
def SetDefaults():
	"""Set default settings function"""
	winsound.MessageBeep()
	returnValue = MessageBox(0, u"You are about to reset the settings, "
								"are you sure you want to contine?"
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
        Parent.SendDiscordmessage(message)

    if data.IsFromDiscord() and data.IsWhisper():
        Parent.SendDiscordDM(data.User, message)

def HasPermission(data, permission, permissioninfo):
    """Return true or false dending on if the user has permission.
    Also sends permission response if user doesn't"""
    if not Parent.HasPermission(data.User, permission, permissioninfo):
        message = MySet.notperm.format(data.UserName, permission, permissioninfo)
        SendResp(data, message)
        return False
    return True

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
	if (not data.IsFromDiscord() and data.GetParam(0).lower() == MySet.command.lower()):
		if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
			return
	
		elif (MySet.onlylive and not Parent.IsLive()):
			SendResp(data, MySet.respNotLive.format(data.UserName))
			
		elif (data.GetParam(1) == ""):
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			command = MySet.command.lower()
			if IsOnCooldown(data, command):
				StoreList(data)
		
		elif (data.GetParam(1).lower() == "info"):
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			else:
				command = MySet.command.lower() + "info"
				if IsOnCooldown(data, command):
					ItemID = data.GetParam(2)
					StoreInfo(data, ItemID, command)
		
		elif (data.GetParam(1).lower() == "log"):
			command = MySet.command.lower() + "log"
			if not HasPermission(data, MySet.StoreLogPermission, MySet.StoreLogPermissionInfo):
				return
			elif not MySet.stf:
				message = "The streamer currently has the store log disabled"
				SendResp(data, message)
			elif IsOnCooldown(data, command):
				StoreLog(data)
		
		elif (data.GetParam(1).lower() == "add"):
			if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
				return
			elif (data.GetParam(2).lower() == "general"):
				ItemType = "general"
				StoreAdd(data, ItemType)
			elif (data.GetParam(2).lower() == "code"):
				ItemType = "code"
				StoreAdd(data, ItemType)
			elif (data.GetParam(2).lower() == "once" or data.GetParam(2).lower() == "once-off"):
				ItemType = "once"
				StoreAdd(data, ItemType)
			elif (data.GetParam(2).lower() == "contribute" or data.GetParam(2).lower() == "ctb"or data.GetParam(2).lower() == "cont"):
				ItemType = "contribute"
				StoreAdd(data, ItemType)
			else:
				message = MySet.atsfailed
				SendResp(data, message)
				if not (data.GetParam(2).lower() == ""):
					message = "The valid item types are [General], [Code], [Once], or [Contribute/CTB]"
					SendResp(data, message)
			
		elif (data.GetParam(1).lower() == "buy"):
			if (data.IsWhisper() and not MySet.StoreBuyWhisp):
				message = "The streamer has disabled item purchases through whispers sorry. Please try again in the chat"
				SendResp(data,message)
				return
			else:
				ItemID = data.GetParam(2)
				Purchase(data, ItemID)
			
		elif (data.GetParam(1).lower() == "toggle"):
			if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
				return
			else:
				StoreToggle(data)
			
		elif (data.GetParam(1).lower() == "help"):
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			command = MySet.command.lower() + "help"
			if IsOnCooldown(data, command):
				StoreHelp(data, command)

		elif (data.GetParam(1).lower() == "delete"):
			if not HasPermission(data, MySet.StoreDelPermission, MySet.StoreDelPermissionInfo):
				return
			elif not MySet.StoreDelEnable:
				message = "The delete function must be enabled before it can be used, due to the nature of what it does"
				SendResp(data, message)
			elif (data.GetParam(2) == ""):
				message = "{0} -> [{1} delete #] is the required command format, where # is the item ID for an item you wish to delete".format(data.UserName,MySet.command)
				SendResp(data, message)
			else:
				ItemID = data.GetParam(2)
				StoreDelete(data, ItemID)
			
		else:
			message = MySet.info.format(data.UserName, MySet.command.lower())
			SendResp(data, message)

def Tick():
	"""Required tick function"""
	return

#---------------------------------------
# [Optional] Store functions
#---------------------------------------
def StoreList(data):
	command = MySet.command.lower()
	Path = os.path.join(os.path.dirname(__file__), "Items")
	Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
	Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
	message = MySet.listbase.format(len([name for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))]), command)
	SendResp(data,message)
	
def LoadItem(data, ItemID):
	"""Checks if item file exists, and then loads all item information. ItemPermission and ItemCooldown are currently not used, but will be in a future update"""
	try:
		int(data.GetParam(2))
	except:
		message = MySet.info.format(data.UserName, MySet.command)
		SendResp(data, message)
		return False
	else:
		global ItemsPath
		ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
		if os.path.exists(ItemsPath):
			with codecs.open(ItemsPath, encoding="utf-8-sig", mode="r") as file:
				Item = [line.strip() for line in file]
				global ItemSetting, ItemName, ItemType, ItemPermission, ItemUse, ItemCost, ItemCooldown, ItemCode
				ItemSetting = Item[0]
				ItemName = Item[1]
				ItemType = Item[2]
				ItemPermission = Item[3]
				ItemCost = int(Item[4])
				ItemCooldown = int(Item[5])
				ItemCode = Item[6]
			return True
		else:
			message = MySet.notavailable.format(data.UserName, ItemID)
			SendResp(data, message)
			return False
	
def Purchase(data, ItemID):
	"""Item purchasing function"""
	if not MySet.purchaseallow:
		message = "The streamer has all item purchases disabled currently."
		SendResp(data, message)	
	else:
		command = "{0} buy".format(MySet.command)
		if LoadItem(data, ItemID) and IsOnCooldown(data, command):
			Currency = Parent.GetCurrencyName()
			Points = Parent.GetPoints(data.UserName)
			if (ItemSetting == "Disabled"):
				message = MySet.notenabled.format(data.UserName, ItemID)
				SendResp(data, message)
				
			elif (ItemType == "contribute"):
				if not (data.GetParam(3) == ""):
					try:
						int(data.GetParam(3))
					except:
						message = "{0} -> Use [{1} buy <#> <amount>] when buying a 'contribute' type item!".format(data.UserName, MySet.command)
						SendResp(data,message)
					else:
						CTB(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command)
				elif Parent.RemovePoints(data.User,data.UserName, ItemCost):
					PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command)
					CTBreset(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command)
				else:
					message = "{0} -> Use [{1} buy <#> <amount>] when buying a 'contribute' type item!".format(data.UserName, MySet.command)
					SendResp(data,message)
					
			elif Parent.RemovePoints(data.User,data.UserName, ItemCost):
				"""All item types excluding contribute"""
				PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command)
			else:
				message = MySet.notenough.format(data.UserName, ItemCost, Currency, Points)
				SendResp(data, message)
				
def CTB(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command):
	"""Function for handling the "contribute" item type"""
	CTBamount = int(data.GetParam(3))
	if (int(data.GetParam(3)) >= ItemCost):
		"""Check if user is paying equal to or in excess of the remaining cost. If yes, pay full amount"""
		if (int(data.GetParam(3)) > ItemCost):
			CTBamount = int(data.GetParam(3))
			message = "{0} -> There is only {1} {2} remaining on this item. Reducing {3} to {1}...".format(data.UserName, ItemCost, Currency, CTBamount)
			SendResp(data, message)
		if Parent.RemovePoints(data.User,data.UserName, ItemCost):
			PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command)
			CTBreset(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command)
		else:
			message = MySet.notenough.format(data.UserName, ItemCost, Currency, Points)
			SendResp(data, message)
			return
	else:
		"""Function for accepting contribution"""
		if Parent.RemovePoints(data.User,data.UserName, CTBamount):
			ItemCost = str(int(ItemCost) - CTBamount)
			with codecs.open(ItemsPath, "w", "utf-8") as fRTC:
				RTC = "Enabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + "\r\n" + str(ItemCode)
				fRTC.write(RTC)
			message = "Thanks {0}! You have added {1} {2} to {3}, which now has {4} {2} remaining!".format(data.UserName, CTBamount, Currency, ItemName, ItemCost)
			SendResp(data, message)
			Points = Parent.GetPoints(data.User)
			message = "Thanks for buying {0}. You now have {1} {2}".format(ItemName, Points, Currency)
			if not data.IsFromYoutube():
				Parent.SendStreamWhisper(data.UserName, message)
			else:
				SendResp(data, message)
		else:
			message = MySet.notenough.format(data.UserName, CTBamount, Currency, Points)
			SendResp(data, message)
			return
		
def CTBreset(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command):
	with codecs.open(ItemsPath, "w", "utf-8") as fResetCost:
		ResetCost = "Disabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemCode) + "\r\n" + str(ItemCooldown) + "\r\n" + str(ItemCode)
		fResetCost.write(ResetCost)
	
def CTBthanks(data, ItemID, ItemName, ItemCost, Currency):
	"""Function for thanking users who contributed to purchasing the item. WORK IN PROGRESS"""
	message = "Thanks {0}, you've just paid the final amount of {1} {2} to purchase {3} for the stream!".format(data.UserName, ItemCost, Currency, ItemName)
	Parent.SendStreamMessage(message)

def PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command):
	"""Process for a successful item purchase"""
	if MySet.enabledDevMode:
		SendResp(data, "Processing payment for " + ItemName + "...")
	Parent.AddCooldown(ScriptName, command, ItemCooldown)
	Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
	if (ItemType == "contribute"):
		CTBthanks(data, ItemID, ItemName, ItemCost, Currency)
	else:
		message = MySet.itempurchasesuccess.format(data.UserName, ItemName, ItemCost, Currency)
		SendResp(data, message)
	Points = Parent.GetPoints(data.User)
	"""Sends message as whisper if not from youtube, else posts in chat"""
	message = "Thanks for buying {0}. You now have {1} {2}".format(ItemName, Points, Currency)
	if not data.IsFromYoutube():
		Parent.SendStreamWhisper(data.UserName, message)
	else:
		SendResp(data, message)
	"""Disables items with one use"""
	if ((ItemType.lower() == "once") or (ItemType.lower() == "code") or (ItemType.lower() == "contribute")):
		ItemDisable(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode)
		if (ItemType.lower() == "code"):
			message = "Your code for redeeming {0} is {1}.".format(ItemName, ItemCode)
			Parent.SendStreamWhisper(data.UserName, message)
	"""Saves to log"""
	if MySet.stf:
		date = datetime.datetime.now().strftime("Date: %d/%m-%Y Time: %H:%M:%S")
		textline = MySet.textline.format(data.UserName, ItemName, ItemCost, Currency, date)
		with codecs.open(LogFile, "a", "utf-8") as f:
			f.write(u"" + textline + "\r\n")
				
def StoreInfo(data, ItemID, command):
	"""Item information function"""
	if LoadItem(data, ItemID):
		if (ItemSetting == "Disabled"):
			message = MySet.notavailable.format(data.UserName, ItemID)
			SendResp(data, message)
		else:
			message = MySet.storeinfosuccess.format(data.UserName, ItemName, ItemType, ItemID, ItemCost, Parent.GetCurrencyName())
			if MySet.StoreInfoWhisp:
				Parent.SendStreamWhisper(data.UserName,message)
			else:
				Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
				Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
				SendResp(data, message)

def StoreToggle(data):
	"""Toggles whether an item is enabled or disabled"""
	ItemID = data.GetParam(2)
	if LoadItem(data, ItemID):
		if (ItemSetting.lower() == "disabled"):
			ItemEnable(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode)
			message = "Item {0} has been successfully enabled!".format(ItemID)
			SendResp(data, message)
		if (ItemSetting.lower() == "enabled"):
			ItemDisable(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode)
			message = "Item {0} has been successfully disabled!".format(ItemID)
			SendResp(data, message)

def ItemDisable(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode):
	"""when called upon, changes the first line of an item.txt from Enabled to Disabled"""
	with codecs.open(ItemsPath, "w", "utf-8") as fEtD:
		EtD = "Disabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + "\r\n" + str(ItemCode)
		fEtD.write(EtD)
		
def ItemEnable(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode):
	"""when called upon, changes the first line of an item.txt from Disabled to Enabled"""
	"""Currently not used anywhere, built in for a future update"""
	with codecs.open(ItemsPath, "w", "utf-8") as fEtD:
		EtD = "Enabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + "\r\n" + str(ItemCode)
		fEtD.write(EtD)

def StoreAdd(data, ItemType):
	"""Adding items to store function"""
	if ((data.GetParam(3).lower() == "code") and data.IsFromYoutube()):
		message = "Sorry, but due to the lack of a private messaging system on YouTube, the code item type cannot be used. Please see the README for more information."
		SendResp(data,message)
	Parameters = data.GetParamCount()
	if (Parameters <= 4):
		message = MySet.atsfailed
		SendResp(data, message)
		return
	if ((Parameters <= 5) and (data.GetParam(3).lower() == "code")):
		message = "Command failed. Command format: {0} add code <cost/default> <ItemCode> <ItemName>. Make sure there are no spaces in the code, or it won't save properly!".format(MySet.command)
		SendResp(data, message)
		return
	ItemSetting = "Enabled"
	ItemPermission = MySet.Permission
	if (data.GetParam(3).lower() == "default"):
		ItemCost = MySet.atsdefaultcost
	else:
		try:
			int(data.GetParam(3))
		except:
			message = "<cost> must be a number, or the word default. {0} was entered instead".format(data.GetParam(3).upper())
			SendResp(data, message)
			return
		else:
			ItemCost = data.GetParam(3)
	ItemCooldown = MySet.timerCooldown
	if (ItemType == "general") or (ItemType == "once"):
		ItemCode = "None"
		StrtParameters = 4
		SaveItemName(data, ItemType, StrtParameters, Parameters)
	elif (ItemType == "contribute"):
		ItemCode = ItemCost
		StrtParameters = 4
		SaveItemName(data, ItemType, StrtParameters, Parameters)
	elif (ItemType == "code"):
		ItemCode = data.GetParam(4)
		StrtParameters = 5
		SaveItemName(data, ItemType, StrtParameters, Parameters)
	else:
		message = "What? How did you get this? That shouldn't be possible!! Please send Xailran a DM containing exactly what you did to trigger this"
		SendResp(data, message)
		return
	Path = os.path.join(os.path.dirname(__file__), "Items")
	ItemID = 1
	ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
	ItemLimit = int(len([name for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))]) + 1)
	for ItemID in range (1, ItemLimit):
		ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
		if os.path.exists(ItemsPath):
			ItemID = ItemID + 1
		else:
			break
	SaveItemPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
	with codecs.open(SaveItemPath, "w", "utf-8") as fCI:
		CI = "Enabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + "\r\n" + str(ItemCode)
		fCI.write(CI)
	message = MySet.atssuccess.format(data.UserName, ItemName)
	SendResp(data, message)
	
def SaveItemName(data, ItemType, StrtParameters, Parameters):
	"""Function for collecting full item name"""
	global ItemName
	ItemName = ""
	for StrtParameters in range (StrtParameters, Parameters):
		ItemName += (data.GetParam(StrtParameters) + " ")
		StrtParameters = StrtParameters + 1
	return ItemName
	
def StoreLog(data):
	"""Function to check last (x) purchases"""
	if (data.GetParam(2) == ""):
		"""!store log"""
		global LogCount
		LogCount = 10
		SendResp(data, "No value given, assigning default value...")
	else:
		"""!store log x"""
		global LogCount
		LogCount = int(data.GetParam(2))
		if (int(data.GetParam(2)) >= 20):
			message = "Sorry, but there is a limit of 20 when using this command."
			SendResp(data, message)
			return
	try:
		with codecs.open(LogFile, encoding="utf-8-sig", mode="r") as file:
			Item = [line.strip() for line in file]
			global count
			count = 0
			while count < LogCount:
				message = Item[count]
				SendResp(data, message)
				count = count + 1
	except:
		message = "Tried to load more log data, but none exists!"
		SendResp(data, message)
	if MySet.enabledDevMode:
		SendResp(data, "LogCount = " + LogCount)
		Parent.Log(ScriptName,"LogCount = " + LogCount)
		
def StoreDelete(data, ItemID):
	"""Deletes an item forever, freeing up its itemID to be used by the next item"""
	if not LoadItem(data, ItemID):
		with codecs.open(DelConfFile, "w", "utf-8") as fCD:
			CD = "Reset"
			fCD.write(CD)
			return
	if LoadItem(data, ItemID):
		with codecs.open(DelConfFile, encoding="utf-8-sig", mode="r") as DCF:
			Item = [line.strip() for line in DCF]
			CurrentItemID = Item[0]
		if (CurrentItemID == ItemID):
			ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
			if os.path.exists(ItemsPath):
				os.remove(ItemsPath)
				message = MySet.StoreDelMsg.format(ItemID,data.UserName)
				SendResp(data, message)
				with codecs.open(DelConfFile, "w", "utf-8") as fCD:
					CD = "Reset"
					fCD.write(CD)
			else:
				message = MySet.notavailable.format(data.UserName, ItemID)
				SendResp(data, message)
		else:
			with codecs.open(DelConfFile, "w", "utf-8") as fCD:
				CD = ItemID
				fCD.write(CD)
			message = "Please send the delete command again to confirm deleting item {0}, {1}. DELETING AN ITEM CANNOT BE UNDONE".format(ItemID,ItemName)
			SendResp(data, message)

def StoreHelp(data, command):
	"""Adds a variety of help responses"""
	if (data.GetParam(2) == "add"):
		if (data.GetParam(3).lower() == "general"):
			message = "[{0} add general <cost/default> <ItemName>] Use this function to add items that can be bought multiple times".format(MySet.command)
		elif (data.GetParam(3).lower() == "once"):
			message = "[{0} add once <cost/default> <ItemName>] Use this function to add items that can only be purchased once".format(MySet.command)
		elif (data.GetParam(3).lower() == "contribute" or data.GetParam(3).lower() == "ctb"):
			message = "[{0} add contribute <cost/default> <ItemName>] Use this function to add items that can everyone can work together to purchase. Can also use 'ctb' as short form for contribute".format(MySet.command)
		elif (data.GetParam(3).lower() == "unique"):
			message = "New Item type for a future update! [{0} add unique <cost/default> <ItemName>] Use this function to add items that can only be purchased once per user.".format(MySet.command)
		elif (data.GetParam(3).lower() == "code"):
			message = "[{0} add code <cost/default> <ItemCode> <ItemName>] use this function to add items that contain a code, so the bot can send a whisper containing the code. Code items can only be purchased once".format(MySet.command)
			if MySet.StoreHelpWhisp:
				Parent.SendStreamWhisper(data.UserName,message)
			else:
				SendResp(data, message)
			message = "Make sure there are no spaces in the <ItemCode>, or it won't save properly!"
		else:
			message = "[{0} add <ItemType> <cost/default> <ItemName>]. Add an item for viewers to purchase with {1}! You can also use {0} toggle to enable/disable an existing item in the store. Use {0} help add [general/once/code/contribute/unique] for more information.".format(MySet.command,Parent.GetCurrencyName())
	elif (data.GetParam(2) == "buy"):
		message = MySet.info.format(data.UserName, MySet.command)
	elif (data.GetParam(2) == "info"):
		message = MySet.info.format(data.UserName, MySet.command)
	elif (data.GetParam(2) == "log"):
		message = "When you use {0} log #, it will load the last # entries, and post them in chat. If no number is given, it will load the last 10 entries. If # is higher than the amount of entries, the bot will load as many as it can before returning an error message.".format(MySet.command)
	elif (data.GetParam(2) == "toggle"):
		message = "Use [{0} toggle #] to enable or disable the purchase of an existing item! Useful if you have a once-off item that you want to make available, or you don't want a general item to be purchased for whatever reason".format(MySet.command)
	elif (data.GetParam(2) == "delete"):
		message = "Use {{0} delete #] to completely remove an item from the system, and allow another item to take its item ID. Once deleted, it can't be undone, so use with caution!".format(MySet.command)
	else:
		message = "The available parameters for [{0} help <function>] are add, buy, delete, info, log, and toggle".format(MySet.command)
	if MySet.HelpCooldown:
		Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
		Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
	if MySet.StoreHelpWhisp:
		Parent.SendStreamWhisper(data.UserName,message)
	else:
		SendResp(data, message)
		
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
			self.enabledDevMode = False
			self.command = "!store"
			self.StoreInfoWhisp = True
			self.StoreHelpWhisp = False
			self.Permission = "Everyone"
			self.PermissionInfo = ""
			self.togCooldown = True
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
			self.StoreDelEnable = False
			self.StoreDelPermission = "Caster"
			self.StoreDelPermissionInfo = ""
			self.stf = True
			self.StoreLogPermission = "Editor"
			self.StoreLogPermissionInfo = ""
			self.textline = "{4}: {0} - {1} - {2} {3}"
			self.atsactivate = False
			self.atsitemname = "ItemName"
			self.atsitemtype = "General"
			self.atscode = "XXXXX-XXXXX-XXXXX"
			self.atsitemcost = 500
			self.respNotLive = "Sorry {0}, but the stream must be live in order to use that command."
			self.info = "{0} -> Use [{1} info <#>] to learn about an item, or [{1} buy <#>] to buy an item!"
			self.itempurchasesuccess = "{0} successfully purchased {1} for {2} {3}!"
			self.notenough = "{0} -> you don't have the {1} {2} required to buy this item."
			self.notavailable = "{0} -> item {1} isn't an available item"
			self.notenabled = "{0} -> item {1} is currently disabled"
			self.notperm = "{0} -> you don't have permission to use this command. permission is: [{1} / {2}]"
			self.listbase = "There are currently {0} items in the store. Use [{1} info <#>] to learn about an item, or [{1} buy <#>] to buy an item"
			self.atssuccess = "{1} has successfully been added by {0}!"
			self.atsfailed = "Command failed. Command format: !store add <ItemType> <cost/default> <ItemName>"
			self.storeinfosuccess = "{0} -> {1} ({2}) is available for {4} {5}"
			self.StoreDelMsg = "Item {0} has been successfully deleted by {1}"

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