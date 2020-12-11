#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Store script to purchase rewards for users"""
#---------------------------------------
# Libraries and references
#---------------------------------------
from collections import deque
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
Version = "1.0.2.1"
Description = "Allow your viewers to spend points to buy items or perks that you create!"

"""
Huge thanks to Castorr91, for without his help, this script would not exist.
Thanks are also due to Bare7a and Mopioid. I appreciate all the assistance you both gave me!
Also, thank you to anyone who has given/gives feedback or helps me find bugs!
"""

#---------------------------------------
# Versions
#---------------------------------------
"""
1.0.2.1 Minor text changes
1.0.2 Fixed Store Log to actually use permissions
1.0.0 Initial Release! Please, give me all your feedback!!

Note: Only important updates are saved here. For more details, check the README.txt
"""
#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
ItemsFile = os.path.join(os.path.dirname(__file__), "ItemsTest.json")
AudioFilesPath = os.path.join(os.path.dirname(__file__), "sounds")
AudioPlaybackQueue = deque()
LogFile = os.path.join(os.path.dirname(__file__), "Log.txt")
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
	if (not data.IsWhisper() and data.IsFromTwitch() and data.GetParam(0).lower() == MySet.command.lower()):
		if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
			return
	
		elif (MySet.onlylive and not Parent.IsLive()):
			SendResp(data, MySet.respNotLive.format(data.UserName))
			
		elif (data.GetParam(1) == ""):
			command = MySet.command.lower()
			if IsOnCooldown(data, command):
				StoreList(data)
		
		elif (data.GetParam(1).lower() == "info"):
			command = MySet.command.lower() + "info"
			if IsOnCooldown(data, command):
				ItemID = data.GetParam(2)
				StoreInfo(data, ItemID, command)
		
		elif (data.GetParam(1).lower() == "log"):
			command = MySet.command.lower() + "log"
			if not HasPermission(data, MySet.StoreLogPermission, MySet.StoreLogPermissionInfo):
				return
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
			else:
				message = MySet.atsfailed
				SendResp(data, message)
				if not (data.GetParam(2).lower() == ""):
					message = "The valid item types are [General], [Once], or [Code]"
					SendResp(data, message)
			
		elif (data.GetParam(1).lower() == "buy"):
			ItemID = data.GetParam(2)
			Purchase(data, ItemID)
		
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
	Parent.AddCooldown(ScriptName, command, MySet.timerCooldown)
	message = MySet.listbase.format(len([name for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))]), command)
	SendResp(data,message)
	
def LoadItem(data, ItemID):
	"""Checks if item file exists, and then loads all item information. ItemPermission and ItemCooldown are currently not used, but will be in a future update"""
	try:
		int(data.GetParam(2))
	except:
		(data.GetParam(2) == "")
		message = MySet.info.format(data.UserName, MySet.command.lower())
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
				ItemCost = Item[4]
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
		command = "!store buy" + ItemID
		if LoadItem(data, ItemID) and IsOnCooldown(data, command):
			Currency = Parent.GetCurrencyName()
			Points = Parent.GetPoints(data.User)
			if not Parent.GetPoints(data.User) <= ItemCost:
				message = MySet.notenough.format(data.UserName, ItemCost, Currency, Points)
				SendResp(data, message)
			elif (ItemSetting == "Disabled"):
				message = MySet.notavailable.format(data.UserName, ItemID)
				SendResp(data, message)
			else:
				PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command)

def PurchaseSuccess(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode, Currency, Points, command):
	"""Process for a successful item purchase"""
	SendResp(data, "Processing payment for " + ItemName + "...")
	ItemCost = int(ItemCost)
	Parent.RemovePoints(data.User,data.UserName, ItemCost)
	Parent.AddCooldown(ScriptName, command, ItemCooldown)
	message = MySet.itempurchasesuccess.format(data.UserName, ItemName, ItemCost, Currency)
	SendResp(data, message)
	Points = int(Points) - int(ItemCost)
	message = "Thanks for buying {0}. You now have {1} {2} remaining".format(ItemName, Points, Currency)
	Parent.SendStreamWhisper(data.UserName, message)
	if (ItemType.lower() == "once") or (ItemType.lower() == "code"):
		ItemDisable(data, ItemID, ItemName, ItemType, ItemPermission, ItemCost, ItemCooldown, ItemCode)
		if (ItemType.lower() == "code"):
			message = "Your code for redeeming {0} is {1}.".format(ItemName, ItemCode)
			Parent.SendStreamWhisper(data.UserName, message)
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
				Parent.AddCooldown(ScriptName,command,ItemCooldown)
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
	Parameters = data.GetParamCount()
	if (Parameters <= 4):
		message = MySet.atsfailed
		SendResp(data, message)
		return
	ItemSetting = "Enabled"
	ItemPermission = MySet.Permission
	if (data.GetParam(3) == "default"):
		ItemCost = MySet.atsdefaultcost
	else:
		try:
			int(data.GetParam(3))
		except:
			message = "<cost> must be a number, or the word default. " + MySet.atsfailed
			SendResp(data, message)
			return
		else:
			ItemCost = data.GetParam(3)
	ItemCooldown = MySet.timerCooldown
	if (ItemType == "general") or (ItemType == "once"):
		ItemCode = "None"
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
	ItemID = str(len([name for name in os.listdir(Path) if os.path.isfile(os.path.join(Path, name))]) + 1)
	SaveItemPath = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(ItemID))
	with codecs.open(SaveItemPath, "w", "utf-8") as fCI:
		CI = "Enabled" + "\r\n" + ItemName + "\r\n" + ItemType + "\r\n" + ItemPermission + "\r\n" + str(ItemCost) + "\r\n" + str(ItemCooldown) + "\r\n" + str(ItemCode)
		fCI.write(CI)
	message = MySet.atssuccess.format(data.UserName, ItemName)
	SendResp(data, message)
	
def SaveItemName(data, ItemType, StrtParameters, Parameters):
	global ItemName
	ItemName = ""
	for StrtParameters in range (4, Parameters):
		ItemName += (data.GetParam(StrtParameters) + " ")
		StrtParameters = StrtParameters + 1
	return ItemName
	
def StoreLog(data):
	"""Function to check last (x) purchases"""
	"""!store log"""
	if (data.GetParam(2) == ""):
		global LogCount
		LogCount = 11
		SendResp(data, "No value given, assigning default value...")
		"""!store log x"""
	else:
		global LogCount
		LogCount = (int(data.GetParam(2)) + 1)
		if (int(data.GetParam(2)) >= 21):
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
			self.StoreInfoWhisp = True
			self.Permission = "Everyone"
			self.PermissionInfo = ""
			self.togCooldown = True
			self.castercd = True
			self.usecd = True
			self.timerCooldown = 30
			self.oncooldown = "{0} the command is still on cooldown for {1} seconds!"
			self.timerUserCooldown = 60
			self.onusercooldown = "{0} the command is still on user cooldown for {1} seconds!"
			self.purchaseallow = True
			self.atsdefaultcost = 500
			self.stf = True
			self.StoreAddPermission = "Editor"
			self.StoreAddPermissionInfo = ""
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
			self.listbase = "There are currently {0} items available to be purchased. Use [{1} info <#>] to check an individual item."
			self.atssuccess = "{1} has successfully been added by {0}!"
			self.atsfailed = "Command failed. Command format: !store add <ItemType> <cost/default> <ItemName>"
			self.storeinfosuccess = "{0} -> {1} ({2}) is available for {4} {5}"

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