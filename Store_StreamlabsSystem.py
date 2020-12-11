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
Version = "1.6.0"
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
1.6.0 - Added "list" function. Added new VIP permission types.
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
	if MySet.StoreInvEnable:
		if MySet.StoreTradingEnable:
			if MySet.StoreTradingCut > 100:
				message = "ERROR: You have set the % cut of inventory trades too high! Must be a number between 0 and 100"
				Parent.SendStreamMessage(message)
	
def Execute(data):
	"""Required Execute data function"""
	if data.GetParam(0).lower() == MySet.command.lower():
		if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
			return
			
		if data.IsFromDiscord() and not MySet.EnabledDiscord:
			Parent.Log(ScriptName,"Command used in discord, not enabled")
			return
	
		elif MySet.onlylive and not Parent.IsLive():
			SendResp(data, MySet.respNotLive.format(data.UserName))
			"""Calls basic function"""
		elif data.GetParam(1) == "":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			command = "StoreBasic"
			if IsOnCooldown(data, command):
				StoreBasic(data)
			"""Calls list function"""		
		elif data.GetParam(1).lower() == "list":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			if not MySet.StoreListEnable:
				message = "The streamer currently has the list function disabled"
				SendResp(data, message)
				return
			command = "StoreList"
			if IsOnCooldown(data, command):
				page = data.GetParam(2)
				StoreList(data, page, command)
			"""Calls info function"""	
		elif data.GetParam(1).lower() == "info":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			command = "StoreInfo"
			if IsOnCooldown(data, command):
				ItemID = data.GetParam(2)
				StoreInfo(data, ItemID, command)
			"""Calls log function"""	
		elif data.GetParam(1).lower() == "log":
			command = "StoreLog"
			if not HasPermission(data, MySet.StoreLogPermission, MySet.StoreLogPermissionInfo):
				return
			if not MySet.stf:
				message = "The streamer currently has the log function disabled"
				SendResp(data, message)
				return
			if IsOnCooldown(data, command):
				StoreLog(data)
			"""Calls add function"""	
		elif data.GetParam(1).lower() == "add":
			if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
				return
			elif data.GetParam(2).lower() == "general":
				ItemType = "general"
				StoreAdd(data, ItemType)
			elif data.GetParam(2).lower() == "code":
				ItemType = "code"
				StoreAdd(data, ItemType)
			elif data.GetParam(2).lower() == "once" or data.GetParam(2).lower() == "once-off":
				ItemType = "once"
				StoreAdd(data, ItemType)
			elif data.GetParam(2).lower() == "contribute" or data.GetParam(2).lower() == "ctb" or data.GetParam(2).lower() == "cont":
				ItemType = "contribute"
				StoreAdd(data, ItemType)
			elif data.GetParam(2).lower() == "unique":
				ItemType = "unique"
				StoreAdd(data, ItemType)
			else:
				message = MySet.atsfailed
				SendResp(data, message)
				if not data.GetParam(2).lower() == "":
					message = "The valid item types are [General], [Code], [Once], or [Contribute/CTB]"
					SendResp(data, message)
			"""Calls edit function"""				
		elif data.GetParam(1).lower() == "edit":
			if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
				return
			else:
				try:
					int(data.GetParam(2))
				except:
					message = "[{0} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, type, cost, permission, or cooldown".format(MySet.command)
					SendResp(data, message)
				else:
					ItemID = data.GetParam(2)
					ItemEditType = data.GetParam(3).lower()
					ItemEditValue = data.GetParam(4)
					StoreEdit(data, ItemID, ItemEditType, ItemEditValue)
			"""Calls buy function"""	
		elif data.GetParam(1).lower() == "buy":
			if data.IsWhisper() and not MySet.StoreBuyWhisp:
				message = "The streamer has disabled item purchases through whispers sorry. Please try again in the chat"
				SendResp(data,message)
				return
			ItemID = data.GetParam(2)
			command = "StoreBuy{0}".format(ItemID)
			if ItemID == all:
				EggType = "buyall"
				Parent.AddCooldown(ScriptName, command, ItemCooldown)
				Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
				EasterEggs(data,EggType)
			else:
				Purchase(data, ItemID, command)
			"""Calls toggle function"""		
		elif data.GetParam(1).lower() == "toggle":
			if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
				return
			else:
				StoreToggle(data)
			"""Calls help function"""		
		elif data.GetParam(1).lower() == "help":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			command = "StoreHelp"
			if IsOnCooldown(data, command):
				StoreHelp(data, command)
			"""Calls delete function"""	
		elif data.GetParam(1).lower() == "delete":
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
				"""Calls inventory function"""
		elif data.GetParam(1).lower() == "inventory" or data.GetParam(1).lower() == "inv":
			if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
				return
			elif not MySet.StoreInvEnable:
				message = "Sorry, the streamer currently has the inventory system disabled."
				SendResp(data, message)
				return
			command = "StoreInventory"
			if IsOnCooldown(data, command):
				StoreInventory(data)
			"""No valid function found"""	
		else:
			message = MySet.info.format(data.UserName, MySet.command.lower())
			SendResp(data, message)

def Tick():
	"""Required tick function"""
	return

#---------------------------------------
# [Optional] Store functions
#---------------------------------------
def StoreBasic(data):
	"""Gives basic instructions for viewers, and gives amount of items in the store"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"StoreBasic activated")
	Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
	Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
	Path = os.path.join(os.path.dirname(__file__), "Items")
	message = MySet.listbase.format(len([name for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))]), command)
	SendResp(data,message)
	
def StoreList(data, page, command):
	"""Based on settings in UI, will show a collection AKA page of basic item information"""
	if page == "":
		message = "The format to use this command is [{0} list <page>], where page is a positive integer.".format(MySet.command)
		SendResp(data, message)
		return
	try:
		page = int(page)
		if page > 0:
			"""Required set-up for defining what goes into a page"""
			trigger = "list"
			item = MySet.StoreListNumber * (page - 1) + 1
			pageLimit = MySet.StoreListNumber * page + 1
			Path = os.path.join(os.path.dirname(__file__), "Items")
			itemMax = len([name for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))])
			pageMax = (itemMax//MySet.StoreListNumber) + 1
			if page > pageMax:
				message = "There are only {0} pages of items. Defaulting to the last page available:".format(pageMax)
				SendResp(data, message)
				page = pageMax
			"""Grabs all items for the page"""
			message = "Format = Item Name (itemID, item cost). "
			for item in range (item, pageLimit):
				if item > itemMax:
					break
				"""If there is a gap between items, the while loop finds the end of the gap"""
				while not LoadItem(data, item, trigger):
					item = item + 1
					if item == pageLimit:
						break
				message += "{0} ({1}, {2}). ".format(ItemName, item, ItemCost)
				item = item + 1
			message += "Page {0}/{1}".format(page,pageMax)
			SendResp(data, message)
		else:
			message = "Sorry, but <page> must be a positive integer. [{0} list <page>]".format(MySet.command)
			SendResp(data, message)
	except:
		message = "Sorry, but <page> must be a positive, whole number. [{0} list <page>]".format(MySet.command)
		SendResp(data, message)
	Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
	Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
	
def LoadItem(data, ItemID, trigger):
	"""Checks if item file exists, and then loads all item information."""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"LoadItem activated")
	try:
		int(data.GetParam(2))
	except:
		"""If itemID is not a number"""
		message = MySet.info.format(data.UserName, MySet.command)
		if (trigger == "info"):
			if MySet.StoreInfoWhisp:
				if data.IsFromDiscord():
					Parent.SendDiscordDM(data.User, message)
				else:
					Parent.SendStreamWhisper(data.UserName,message)
			else:
				SendResp(data, message)
		else:
			SendResp(data, message)
		if (trigger == "edit"):
			message = "[{0} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, cost, permission, or cooldown".format(MySet.command)
			SendResp(data, message)	
		else:
			SendResp(data, message)
		if MySet.enabledDevMode:
			Parent.Log(ScriptName,"LoadItem False, not number")
		return False
	else:
		"""Loads item data"""
		global ItemsPath
		ItemsPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
		if os.path.exists(ItemsPath):
			with codecs.open(ItemsPath, encoding="utf-8-sig", mode="r") as file:
				Item = [line.strip() for line in file]
				global ItemSetting, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode
				ItemSetting = Item[0]
				ItemName = Item[1]
				ItemType = Item[2]
				PermissionData = (Item[3]).split(" ")
				ItemPermission = Item[3]
				ItemCost = int(Item[4])
				CooldownData = (Item[5]).split(" ")
				ItemCode = Item[6]
				ItemPermission = PermissionData[0]
				try:
					ItemPermissionInfo = PermissionData[1]
				except:
					ItemPermissionInfo = ""
				ItemCooldown = int(CooldownData[0])
				try:
					ItemUserCooldown = int(CooldownData[1])
				except:
					ItemUserCooldown = ""
			if MySet.enabledDevMode:
				Parent.Log(ScriptName,"LoadItem True")
				message = "Setting: " + ItemSetting + "Name: " + ItemName + " Type: " + ItemType + " P: " + ItemPermission + " PInfo: " + ItemPermissionInfo + " Cost: " + str(ItemCost) + " Cooldown: " + str(ItemCooldown) + " UCooldown: " + str(ItemUserCooldown)  + " Code: " + ItemCode
				SendResp(data, message)
			return True
			"""If item cannot be found"""
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
			if MySet.enabledDevMode:
				Parent.Log(ScriptName,"LoadItem False, not found")
			return False
	
def Purchase(data, ItemID, command):
	"""Item purchasing function"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"Purchase activated")
	if not MySet.purchaseallow:
		message = "The streamer has all item purchases disabled currently."
		SendResp(data, message)	
	else:
		trigger = "buy"
		if  IsOnCooldown(data, command) and LoadItem(data, ItemID, trigger):
			Currency = Parent.GetCurrencyName()
			Points = Parent.GetPoints(data.UserName)
			if (ItemSetting == "Disabled"):
				message = MySet.notenabled.format(data.UserName, ItemID)
				SendResp(data, message)
				return
			if not HasPermission(data, ItemPermission, ItemPermissionInfo):
				return
			"""Contribute type specifics"""
			if (ItemType == "contribute"):
				if not (data.GetParam(3) == ""):
					try:
						int(data.GetParam(3))
					except:
						message = "{0} -> Use [{1} buy <#> <amount>] when buying a 'contribute' type item!".format(data.UserName, MySet.command)
						SendResp(data,message)
					else:
						CTB(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command)
				elif Parent.RemovePoints(data.User,data.UserName, ItemCost):
					PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command)
					CTBreset(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command)
				else:
					message = "{0} -> Use [{1} buy <#> <amount>] when buying a 'contribute' type item!".format(data.UserName, MySet.command)
					SendResp(data,message)
				return
			"""Unique type specifics"""
			if (ItemType == "unique"):
				if MySet.enabledDevMode:
					Parent.Log(ScriptName, "Starting unique item type sequence")
				if data.User in ItemCode:
					message = "{0} -> You have purchased this item before, so it is unavailable for you sorry".format(data.UserName)
					SendResp(data, message)
					return
				if MySet.enabledDevMode:
					Parent.Log(ScriptName, "Finished unique item type sequence")
			"""All item types excluding contribute"""
			if Parent.RemovePoints(data.User,data.UserName, ItemCost):
				PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command)
			else:
				message = MySet.notenough.format(data.UserName, ItemCost, Currency, Points)
				SendResp(data, message)
				
def CTB(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command):
	"""Function for handling the "contribute" item type"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"CTB activated")
	CTBamount = int(data.GetParam(3))
	if (int(data.GetParam(3)) >= ItemCost):
		"""Check if user is paying equal to or in excess of the remaining cost. If yes, pay full amount"""
		if (int(data.GetParam(3)) > ItemCost):
			CTBamount = int(data.GetParam(3))
			message = "{0} -> There is only {1} {2} remaining on this item. Reducing {3} to {1}...".format(data.UserName, ItemCost, Currency, CTBamount)
			SendResp(data, message)
		if Parent.RemovePoints(data.User,data.UserName, ItemCost):
			PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command)
			CTBreset(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command)
		else:
			message = MySet.notenough.format(data.UserName, ItemCost, Currency, Points)
			SendResp(data, message)
			return
	else:
		"""Function for accepting contribution"""
		if Parent.RemovePoints(data.User,data.UserName, CTBamount):
			ItemCost = str(int(ItemCost) - CTBamount)
			with codecs.open(ItemsPath, "w", "utf-8") as fRTC:
				RTC = "Enabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
				fRTC.write(RTC)
			message = "Thanks {0}! You have added {1} {2} to {3}, which now has {4} {2} remaining!".format(data.UserName, CTBamount, Currency, ItemName, ItemCost)
			SendResp(data, message)
			Points = Parent.GetPoints(data.User)
			message = "Thanks for buying {0}. You now have {1} {2}".format(ItemName, Points, Currency)
			if not data.IsFromYoutube():
				if data.IsFromDiscord():
					Parent.SendDiscordDM(data.User, message)
				else:
					Parent.SendStreamWhisper(data.UserName, message)
			else:
				SendResp(data, message)
		else:
			message = MySet.notenough.format(data.UserName, CTBamount, Currency, Points)
			SendResp(data, message)
			return
		
def CTBreset(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command):
	"""Changes item cost back to original item cost"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"CTBreset activated")
	with codecs.open(ItemsPath, "w", "utf-8") as fResetCost:
		ResetCost = "Disabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCode) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
		fResetCost.write(ResetCost)
	
def CTBthanks(data, ItemID, ItemName, ItemCost, Currency):
	"""Function for thanking users who contributed to purchasing the item. WORK IN PROGRESS"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"CTBthanks activated")
	message = "Thanks {0}, you've just paid the final amount of {1} {2} to purchase {3} for the stream!".format(data.UserName, ItemCost, Currency, ItemName)
	if data.IsFromDiscord():
		Parent.SendDiscordMessage(message)
	else:
		Parent.SendStreamMessage(message)

def PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode, Currency, Points, command):
	"""Process for a successful item purchase"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"PurchaseSuccess activated")
	if MySet.enabledDevMode:
		SendResp(data, "Processing payment for " + ItemName + "...")
	Parent.AddCooldown(ScriptName, command, ItemCooldown)
	Parent.AddUserCooldown(ScriptName,command,data.User,int(ItemUserCooldown))
	if (ItemType == "contribute"):
		CTBthanks(data, ItemID, ItemName, ItemCost, Currency)
	else:
		message = MySet.itempurchasesuccess.format(data.UserName, ItemName, ItemCost, Currency)
		SendResp(data, message)
	if (ItemType == "unique"):
		with codecs.open(ItemsPath, "w", "utf-8") as fAtU:
			AtU = "Enabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode) + data.User + "%#%" 
			fAtU.write(AtU)
	Points = Parent.GetPoints(data.User)
	"""Sends message as whisper if not from youtube, else posts in chat"""
	message = "Thanks for buying {0}. You now have {1} {2}".format(ItemName, Points, Currency)
	if not data.IsFromYoutube():
		if data.IsFromDiscord():
			Parent.SendDiscordDM(data.User, message)
		else:
			Parent.SendStreamWhisper(data.UserName, message)
	else:
		SendResp(data, message)
	"""Disables items with one use"""
	if ((ItemType.lower() == "once") or (ItemType.lower() == "code") or (ItemType.lower() == "contribute")):
		ItemDisable(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode)
		if (ItemType.lower() == "code"):
			message = "Your code for redeeming {0} is {1}.".format(ItemName, ItemCode)
			if data.IsFromDiscord():
				Parent.SendDiscordDM(data.User, message)
			else:
				Parent.SendStreamWhisper(data.UserName, message)
	"""Saves to log"""
	if MySet.stf:
		date = datetime.datetime.now().strftime("Date: %d/%m-%Y Time: %H:%M:%S")
		textline = MySet.textline.format(data.UserName, ItemName, ItemCost, Currency, date)
		with codecs.open(LogFile, "a", "utf-8") as f:
			f.write(u"" + textline + "\r\n")
				
def StoreInfo(data, ItemID, command):
	"""Item information function"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"StoreInfo activated")
	trigger = "info"
	if LoadItem(data, ItemID, trigger):
		if (ItemSetting == "Disabled"):
			message = MySet.notavailable.format(data.UserName, ItemID)
			SendResp(data, message)
		else:
			message = MySet.storeinfosuccess.format(data.UserName, ItemName, ItemType, ItemID, ItemCost, Parent.GetCurrencyName())
			if MySet.StoreInfoWhisp:
				if data.IsFromDiscord():
					Parent.SendDiscordDM(data.User, message)
				else:
					Parent.SendStreamWhisper(data.UserName, message)
			else:
				Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
				Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)
				SendResp(data, message)

def StoreToggle(data):
	"""Toggles whether an item is enabled or disabled"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"StoreToggle activated")
	ItemID = data.GetParam(2)
	trigger = "toggle"
	if LoadItem(data, ItemID, trigger):
		if (ItemSetting.lower() == "disabled"):
			ItemEnable(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode)
			message = "Item {0} has been successfully enabled!".format(ItemID)
			SendResp(data, message)
		if (ItemSetting.lower() == "enabled"):
			ItemDisable(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode)
			message = "Item {0} has been successfully disabled!".format(ItemID)
			SendResp(data, message)

def ItemDisable(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode):
	"""when called upon, changes the first line of an item.txt from Enabled to Disabled"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"ItemDisable activated")
	with codecs.open(ItemsPath, "w", "utf-8") as fEtD:
		EtD = "Disabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
		fEtD.write(EtD)
		
def ItemEnable(data, ItemID, ItemName, ItemType, ItemPermission, ItemPermissionInfo, ItemCost, ItemCooldown, ItemUserCooldown, ItemCode):
	"""when called upon, changes the first line of an item.txt from Disabled to Enabled"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"ItemEnable activated")
	with codecs.open(ItemsPath, "w", "utf-8") as fEtD:
		EtD = "Enabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
		fEtD.write(EtD)

def StoreAdd(data, ItemType):
	"""Adding items to store function"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"StoreAdd activated")
	"""Checks if enough information has been provided"""
	if (data.GetParam(2).lower() == "code") and data.IsFromYoutube():
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
	"""Starts establishing data for the new item"""
	ItemSetting = "Enabled"
	ItemPermission = MySet.Permission + " " + MySet.PermissionInfo
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
	ItemUserCooldown = MySet.timerUserCooldown
	"""Sets code and name data for the item"""
	if (ItemType == "general") or (ItemType == "once"):
		ItemCode = "None"
		StrtParameters = 4
		SaveItemName(data, ItemType, StrtParameters, Parameters)
	elif (ItemType == "contribute"):
		ItemCode = ItemCost
		StrtParameters = 4
		SaveItemName(data, ItemType, StrtParameters, Parameters)
	elif (ItemType == "unique"):
		ItemCode = " "
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
	"""Sets itemID data"""
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
	"""Brings all the data together, and saves the item"""
	SaveItemPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
	with codecs.open(SaveItemPath, "w", "utf-8") as fCI:
		CI = "Enabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
		fCI.write(CI)
	message = MySet.atssuccess.format(data.UserName, ItemName)
	SendResp(data, message)
	
def SaveItemName(data, ItemType, StrtParameters, Parameters):
	"""Function for collecting full item name"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"SaveItemName activated")
	global ItemName
	ItemName = ""
	for x in range(StrtParameters, Parameters):
		ItemName += (data.GetParam(x) + " ")
	return ItemName
		
def StoreEdit(data, ItemID, ItemEditType, ItemEditValue):
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"StoreEdit activated")
	trigger = "edit"
	if LoadItem(data, ItemID, trigger):
		if ItemEditType == "name" or ItemEditType == "itemname":
			"""Changing item name"""
			if ItemEditValue == "":
				if MySet.enabledDevMode:
					Parent.Log(ScriptName,"No item name found")
				message = "[{0} edit <itemID> name <DataValue>]. <DataValue> is the new name you wish to change the item to".format(MySet.command)
				SendResp(data, message)
				return
			OldItemName = ItemName
			StrtParameters = 4
			Parameters = data.GetParamCount()
			SaveItemName(data, ItemType, StrtParameters, Parameters)
			with codecs.open(ItemsPath, "w", "utf-8") as fEIN:
					EIN = ItemSetting + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
					fEIN.write(EIN)
			message = "Success! {0} ({1}) has changed to {2}!".format(OldItemName, ItemID, ItemName)
			SendResp(data, message)
			
		elif ItemEditType == "type":
			"""Changing item type"""	
			message = "Item types are core to how an item works, and it would be very easy for this to go wrong. Thus, editing item types has not been permitted"
			SendResp(data, message)
		
		elif ItemEditType == "permission":
			"""Changing item permission"""
			ItemEditValue = ItemEditValue.lower()
			global ItemPermission, ItemPermissionInfo, ItemCode
			if not ItemPermissionInfo == "":
				OldItemPermission = ItemPermission + " " + ItemPermissionInfo
			else:
				OldItemPermission = ItemPermission
			ItemPermission = ""
			if ItemEditValue == "everyone":
				ItemPermission = "Everyone"
			elif ItemEditValue == "regular":
				ItemPermission = "Regular"
			elif ItemEditValue == "subscriber":
				ItemPermission = "Subscriber"
			elif ItemEditValue == "gamewispsubscriber":
				ItemPermission = "GameWisp Subscriber"
			elif ItemEditValue == "moderator":
				ItemPermission = "Moderator"
			elif ItemEditValue == "editor":
				ItemPermission = "Editor"
			elif ItemEditValue == "caster":
				ItemPermission = "Caster"
			elif ItemEditValue == "min_rank":
				if data.GetParamCount() == 5:
					message = "When setting the min_rank permission, you need to choose a rank! [{0} edit <itemID> permission min_rank <rank>]".format(MySet.command)
					SendResp(data,message)
					return
				ItemPermission = "Min_Rank " + data.GetParam(5)
			elif ItemEditValue == "min_points":
				if data.GetParamCount() == 5:
					message = "When setting the min_points permission, you need to choose an amount of points! [{0} edit <itemID> permission min_points <points>]".format(MySet.command)
					SendResp(data,message)
					return
				ItemPermission = "Min_Points " + data.GetParam(5)
			elif ItemEditValue == "min_hours":
				if data.GetParamCount() == 5:
					message = "When setting the min_hours permission, you need to choose an amount of hours! [{0} edit <itemID> permission min_hours <hours>]".format(MySet.command)
					SendResp(data,message)
					return
				ItemPermission = "Min_Hours " + data.GetParam(5)
			elif ItemEditValue == "user_specific":
				if data.GetParamCount() == 5:
					message = "When setting the min_rank permission, you need to choose an user! [{0} edit <itemID> permission user_specific <user>]".format(MySet.command)
					SendResp(data,message)
					return
				ItemPermission = "user_Specific " + data.GetParam(5)
			else:
				message = "The valid item permission values that can be changed through this command are: Everyone, Regular, Subscriber, GameWispSubscriber, Moderator, Editor, Caster, min_rank, min_points, min_hours, or user_specific"
				SendResp(data, message)
				return
			if MySet.enabledDevMode:
				Parent.Log(ScriptName,"Permission is set to " + ItemPermission + ". Parameter count = " + str(data.GetParamCount()))
			with codecs.open(ItemsPath, "w", "utf-8") as fEP:
				EP = ItemSetting + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
				fEP.write(EP)
			message = "Success! {0} ({1}) has changed from {2} to {3}".format(ItemName, ItemID, OldItemPermission, ItemPermission)
			SendResp(data,message)
			if MySet.enabledDevMode:
				message = ItemSetting + ", " + ItemName + ", " + ItemType + ", " + ItemPermission + ", " + str(ItemCost) + ", " + str(ItemCooldown) + " " + str(ItemUserCooldown) + ", " + str(ItemCode)
				SendResp(data, message)
		
		elif ItemEditType == "cost":
			"""Changing item cost"""
			try:
				int(ItemEditValue)
			except:
				message = "[{0} edit <itemID> cost <EditValue>] When editing the cost of an item, you must enter a valid number as the <EditValue>.".format(MySet.command) 
			else:
				if ItemType == "contribute":
					ItemCode = ItemEditValue
				with codecs.open(ItemsPath, "w", "utf-8") as fEC:
					EC = ItemSetting + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemEditValue) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
					fEC.write(EC)
				message = "Success! {0} ({1}) has changed from {2} {3} to {4} {3}".format(ItemName, ItemID, ItemCost, Parent.GetCurrencyName(), ItemEditValue)
				SendResp(data, message)
	
		elif (ItemEditType == "cooldown"):
			"""Changing item cooldown"""
			try:
				int(ItemEditValue)
			except:
				message = "[{0} edit <itemID> cooldown <#>] When editing the cooldown of an item, you must enter a number!".format(MySet.command) 
			else:
				with codecs.open(ItemsPath, "w", "utf-8") as fECD:
					ECD = ItemSetting + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCost) + "\r\n" + str(ItemEditValue) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemCode)
					fECD.write(ECD)
				message = "Success! {0} ({1}) has changed from {2} seconds to {3} seconds.".format(ItemName, ItemID, ItemCooldown, ItemEditValue)
				SendResp(data, message)
		
		elif (ItemEditType == "usercooldown"):
			"""Changing item cooldown"""
			try:
				int(ItemEditValue)
			except:
				message = "[{0} edit <itemID> usercooldown <#>] When editing the user cooldown of an item, you must enter a number!".format(MySet.command) 
			else:
				with codecs.open(ItemsPath, "w", "utf-8") as fECD:
					ECD = ItemSetting + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemEditValue) + "\r\n" + str(ItemCode)
					fECD.write(ECD)
				message = "Success! {0} ({1}) has changed from {2} seconds to {3} seconds.".format(ItemName, ItemID, ItemUserCooldown, ItemEditValue)
				SendResp(data, message)

		elif (ItemEditType == "code"):
			"""Changing item code"""
			if (ItemEditValue == ""):
				if MySet.enabledDevMode:
					Parent.Log(ScriptName,"No item name found")
				message = "[{0} edit <itemID> code <DataValue>]. <DataValue> is the new code you wish to assign to the item. WARNING: This will delete the old code!".format(MySet.command)
				SendResp(data, message)
				return
			if not ItemType == "code":
				message = "Items with the '{0}' type don't have a code! Please try again with another item.".format(ItemType)
				SendResp(data, message)
				return
			else:
				with codecs.open(ItemsPath, "w", "utf-8") as fEC:
					EC = ItemSetting + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + " " + ItemPermissionInfo + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + " " + str(ItemUserCooldown) + "\r\n" + str(ItemEditValue)
					fEC.write(EC)
				message = "Success! {0} ({1}) has changed from {2} to {3}".format(ItemName, ItemID, ItemCode, ItemEditValue)
				SendResp(data, message)
				
		else:
			"""ItemEditType not recognised"""
			message = "[{0} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, cost, permission, cooldown, or code".format(MySet.command)
			SendResp(data, message)
			
def StoreLog(data):
	"""Function to check last (x) purchases"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"StoreLog activated")
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
	"""Printing set amount of log entries, in order of latest to oldest"""
	with codecs.open(LogFile, encoding="utf-8-sig", mode="r") as file:
		Item = [line.strip() for line in file]
		global count
		count = 0
		entry = len(Item) - 1
		while count < LogCount:
			if (entry - count) < 0:
				message = "Tried to load more log data, but none exists!"
				SendResp(data, message)
				break
			message = Item[entry - count]
			SendResp(data, message)
			count = count + 1
	if MySet.enabledDevMode:
		SendResp(data, "LogCount = " + LogCount)
		Parent.Log(ScriptName,"LogCount = " + LogCount)
		
def StoreDelete(data, ItemID):
	"""Deletes an item forever, freeing up its itemID to be used by the next item"""
	trigger = "delete"
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"StoreDelete activated")
	"""If item doesn't exist, resets the delete file"""
	if not LoadItem(data, ItemID, trigger):
		with codecs.open(DelConfFile, "w", "utf-8") as fCD:
			CD = "Reset"
			fCD.write(CD)
			return
	"""Checks if delete function has been set to the current item"""
	if LoadItem(data, ItemID, trigger):
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
			"""Sets delete function to current item"""
		else:
			with codecs.open(DelConfFile, "w", "utf-8") as fCD:
				CD = ItemID
				fCD.write(CD)
			message = "Please send the delete command again to confirm deleting item {0}, {1}. DELETING AN ITEM CANNOT BE UNDONE".format(ItemID,ItemName)
			SendResp(data, message)

def StoreHelp(data, command):
	"""Adds a variety of help responses"""
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"StoreHelp activated")
	"""Choosing which help message to send"""
	if (data.GetParam(2) == "add"):
		if (data.GetParam(3).lower() == "general"):
			message = MySet.helpmessageAddGeneral.format(data.UserName, MySet.command)
		elif (data.GetParam(3).lower() == "once"):
			message = MySet.helpmessageAddOnce.format(data.UserName, MySet.command)
		elif (data.GetParam(3).lower() == "contribute" or data.GetParam(3).lower() == "ctb"):
			message = MySet.helpmessageAddContribute.format(data.UserName, MySet.command)
		elif (data.GetParam(3).lower() == "unique"):
			message = MySet.helpmessageAddUnique.format(data.UserName, MySet.command)
		elif (data.GetParam(3).lower() == "code"):
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
	if MySet.enabledDevMode:
		Parent.Log(ScriptName,"EasterEggs activated")
	if MySet.EggsEnabled:
		if EggType == "buyall":
			message = "Come on, isn't that just a LITTLE excessive {0}?".format(data.UserName)
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
			self.StoreListEnable = True
			self.StoreListNumber = 10
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
			self.helpmessageAddCode = "[{1} add code <cost/default> <ItemCode> <ItemName>] use this function to add items that contain a code, so the bot can send a whisper containing the code. Code items can only be purchased once"
			self.helpmessageAddCode2 = "Make sure there are no spaces in the ItemCode, or it won't save properly!"
			self.helpmessageLog = "When you use [{1} log #], it will load the last # entries, and post them in chat. If no number is given, it will load the last 10 entries. If # is higher than the amount of entries, the bot will load as many as it can before returning an error message."
			self.helpmessageToggle = "Use [{1} toggle #] to enable or disable the purchase of an existing item! Useful if you have a once-off item that you want to make available, or you don't want a general item to be purchased for whatever reason"
			self.helpmessageEdit = "[{1} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, cost, permission, cooldown, or code"
			self.helpmessageDelete = "Use {1} delete #] to completely remove an item from the system, and allow another item to take its item ID. Once deleted, it can't be undone, so use with caution!"


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