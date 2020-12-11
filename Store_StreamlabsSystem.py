#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Store script to purchase rewards for users"""
# ---------------------------------------
# Libraries and references
# ---------------------------------------
import codecs
import json
import os
import datetime
import ctypes
import winsound

# ---------------------------------------
# Script information
# ---------------------------------------
ScriptName = "Store"
Website = "https://www.xailran.com/"
Creator = "Xailran"
Version = "2.0.1"
Description = "Allow your viewers to spend points to buy items or perks that you create; now with inventory"

# ---------------------------------------
# Versions
# ---------------------------------------
"""
2.0.1 - Changed list messages to be customizable. Added quantities that can be added to items
2.0.0 - Added list and sound functionality, and new item types. "Help" messages are now customizable. Major code re-work
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

# ---------------------------------------
# Variables
# ---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
itemPath = os.path.join(os.path.dirname(__file__), "Items")
inventoryFile = os.path.join(os.path.dirname(__file__), "inventory.json")
backupInvFile = os.path.join(os.path.dirname(__file__), "inventory_backup.json")
MySet = None  # type: Settings
LogFile = os.path.join(os.path.dirname(__file__), "Log.txt")
SoundPath = os.path.join(os.path.dirname(__file__), "sounds")
MessageBox = ctypes.windll.user32.MessageBoxW
MB_YES = 6
DelConf = "Reset"
sessionItems = set()
soundQueue = []


# ---------------------------------------
# Settings functions
# ---------------------------------------
def SetDefaults():
    """Set default settings function"""
    winsound.MessageBeep()
    return_value = MessageBox(0, u"You are about to reset the settings, "
                                 "are you sure you want to continue?",
                              u"Reset settings file?", 4)

    if return_value == MB_YES:
        Settings(None, None).Save(settingsFile)
        MessageBox(0, u"Settings successfully restored to default values!"
                      "\r\nMake sure to reload script to load new values into UI",
                   u"Reset complete!", 0)


def ReloadSettings(json_data):
    """Reload settings on Save"""
    global MySet
    MySet.Reload(json_data)


# ---------------------------------------
# UI functions
# ---------------------------------------
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
    return_value = MessageBox(0, u"You are about to reset the log file "
                                 "are you sure you want to continue?",
                              u"Reset log file?", 4)
    if return_value == MB_YES:
        with open(LogFile, "w") as f:
            f.write("")
            MessageBox(0, u"Log file successfully reset.",
                       u"Log file reset!", 0)


def CreatorWebsite():
    """Opens Xailran.com"""
    OpenLink(Website)


def OpenLink(link):
    """Open links through buttons in UI"""
    os.system("explorer " + link)


# ---------------------------------------
# Optional functions
# ---------------------------------------
def IsOnCooldown(data, command):
    """Handle cooldowns"""
    command = str(command)
    cooldown = Parent.IsOnCooldown(ScriptName, command)
    user_cooldown = Parent.IsOnUserCooldown(ScriptName, command, data.User)
    caster = (Parent.HasPermission(data.User, "Caster", "") and MySet.castercd)

    if (cooldown or user_cooldown) and caster is False:

        if MySet.usecd:
            cooldown_duration = Parent.GetCooldownDuration(ScriptName, command)
            user_cdd = Parent.GetUserCooldownDuration(ScriptName, command, data.User)

            if cooldown_duration > user_cdd:
                SendResp(data, MySet.oncooldown.format(data.UserName, cooldown_duration))

            else:
                SendResp(data, MySet.onusercooldown.format(data.UserName, user_cdd))
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


def LoadTextFile(textfile):
    """Loads content of a textfile, with each line as a string in a list"""
    textlines = []
    if os.path.exists(textfile) and os.path.isfile(textfile):
        with codecs.open(textfile, encoding="utf-8-sig", mode="r") as text:
            textlines = [line.strip() for line in text]
    return textlines


def SaveTextFile(textfile, inputstring):
    with codecs.open(textfile, "w", "utf-8") as f:
        f.write(inputstring)


def LoadJSONFile(jsonfile):
    database = {}
    if os.path.exists(jsonfile) and os.path.isfile(jsonfile):
        with codecs.open(jsonfile, encoding='utf-8-sig', mode='r') as f:
            database = json.load(f, encoding='utf-8-sig')
    return database


def SaveJSONFile(jsonfile, inputjson):
    with codecs.open(jsonfile, "w", "utf-8") as f:
        json.dump(inputjson, f, indent=4, sort_keys=True)


def MatchUsage(data, usageperm):
    """Returns true if usage matches settings, otherwise returns false"""
    if usageperm == "All":
        return True
    if not data.IsFromDiscord():
        if usageperm == "Stream Both" or usageperm == "Stream Chat" and not data.IsWhisper() \
                or usageperm == "Stream Whisper" and data.IsWhisper():
            return True
    elif usageperm == "Discord Both" or usageperm == "Discord Chat" and not data.IsWhisper() \
            or usageperm == "Discord Whisper" and data.IsWhisper():
        return True
    else:
        return False


# ---------------------------------------
# [Required] functions
# ---------------------------------------
def Init():
    """data on Load, required function"""
    global MySet
    MySet = Settings(Parent, settingsFile)
    global parent
    parent = Parent


def Execute(data):
    """Required Execute data function"""
    if data.GetParam(0).lower() == MySet.command.lower():

        if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
            return
        if data.IsFromDiscord() and not MySet.EnabledDiscord:
            Parent.Log(ScriptName, "Command used in discord, not enabled")
            return
        if MySet.onlylive and not Parent.IsLive():
            SendResp(data, MySet.respNotLive.format(data.UserName))
            return

        function = data.GetParam(1).lower()
        item_id = data.GetParam(2)

        # Calls basic function
        if function == "":
            if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
                return
            command = "StoreBasic"
            if IsOnCooldown(data, command):
                StoreBasic(data)

        # Calls add function
        elif function == "add":
            if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
                return
            item_type = data.GetParam(2)
            if item_type == ItemType.code and data.IsFromYoutube():
                message = "Sorry, but due to the lack of a private messaging system on YouTube, " \
                          "the code item type cannot be used. Please see the README for more information."
                SendResp(data, message)
                return
            if item_type != "":
                StoreAdd(data, item_type)
            else:
                message = MySet.atsfailed
                SendResp(data, message)
                if not data.GetParam(2).lower() == "":
                    message = "The valid item types are [General], [Code], [Once], [Unique], " \
                              "[Contribute/CTB], or [Session]"
                    SendResp(data, message)

            # Calls log function
        elif function == "log":
            if not HasPermission(data, MySet.StoreLogPermission, MySet.StoreLogPermissionInfo):
                return
            if not MySet.stf:
                message = "The log function disabled is currently disabled in the UI"
                SendResp(data, message)
                return
            StoreLog(data)

        # Calls list function
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

        # Calls info function
        elif function == "info":
            if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
                return
            command = "StoreInfo"
            if IsOnCooldown(data, command):
                StoreInfo(data, item_id, command)

        # Calls edit function
        elif function == "edit":
            if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
                return
            else:
                StoreEdit(data, item_id, data.GetParam(3).lower(), data.GetParam(4))

        # Calls buy function
        elif function == "buy":
            if data.IsWhisper() and not MySet.StoreBuyWhisp:
                message = "Item purchases in whispers have been disabled sorry. Please try again in the chat"
                SendResp(data, message)
                return
            if item_id == "all":
                if IsOnCooldown(data, "buyall"):
                    EasterEggs(data, "buyall")
            else:
                Purchase(data, item_id)

        # Calls toggle function
        elif function == "toggle":
            if not HasPermission(data, MySet.StoreAddPermission, MySet.StoreAddPermissionInfo):
                return
            else:
                StoreToggle(data, item_id)

        # Calls help function
        elif function == "help":
            if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
                return
            command = "StoreHelp"
            if IsOnCooldown(data, command):
                StoreHelp(data, command)

        # Calls delete function
        elif function == "delete":
            if not HasPermission(data, MySet.StoreDelPermission, MySet.StoreDelPermissionInfo):
                return
            elif not MySet.StoreDelEnable:
                message = "The delete function must be enabled in the UI before it can be used, " \
                          "due to the nature of what it does"
                SendResp(data, message)
            elif item_id == "":
                message = "{0} -> [{1} delete #] is the required command format, " \
                          "where # is the item ID for an item you wish to delete".format(data.UserName, MySet.command)
                SendResp(data, message)
            else:
                StoreDelete(data, item_id)

        # Calls inventory function
        elif function == "inventory" or function == "inv":
            if not HasPermission(data, MySet.Permission, MySet.PermissionInfo):
                return
            command = Trigger.inventory
            if IsOnCooldown(data, command):
                StoreInventory(data)

        # No valid function found
        else:
            message = MySet.info.format(data.UserName, MySet.command.lower())
            SendResp(data, message)


def Tick():
    """Required tick function"""
    if not Parent.IsOnCooldown(ScriptName, "sounds"):
        Parent.AddCooldown(ScriptName, "sounds", 2)
        if soundQueue:
            playsound = soundQueue[0]
            if playsound == "playrandom":
                filelist = [filename for filename in os.listdir("path") if os.path.isfile(filename)]
                playsound = filelist[Parent.GetRandom(0, len(filelist))]
            if Parent.PlaySound(playsound, MySet.volume * 0.01):
                soundQueue.pop(0)


def Unload():
    SessionEnded()


# ---------------------------------------
# [Optional] Store functions
# ---------------------------------------
def StoreBasic(data):
    """Gives basic instructions for viewers, and gives amount of items in the store"""
    Parent.AddCooldown(ScriptName, "StoreBasic", MySet.timerCooldown)
    Parent.AddUserCooldown(ScriptName, "StoreBasic", data.User, MySet.timerUserCooldown)
    path = os.path.join(os.path.dirname(__file__), "Items")
    message = MySet.listbase.format(
        len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]), MySet.command)
    SendResp(data, message)


def LoadItem(data, item_id, trigger):
    """Checks if item file exists, and then loads all item information."""
    try:
        int(item_id)
    except ValueError:
        # If itemID is not a number
        message = MySet.info.format(data.UserName, MySet.command)
        if trigger == Trigger.info:
            if MySet.StoreInfoWhisp:
                if data.IsFromDiscord():
                    Parent.SendDiscordDM(data.User, message)
                else:
                    Parent.SendStreamWhisper(data.UserName, message)
            else:
                SendResp(data, message)
        elif trigger == "edit":
            message = "[{0} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, " \
                      "cost, permission, cooldown, code, or sound".format(MySet.command)
            SendResp(data, message)
        else:
            SendResp(data, message)
        return None
    else:
        try:
            item = Item(item_id)
            return item
        except IOError:
            # If item cannot be found
            if not trigger == "list":
                message = MySet.notavailable.format(data.UserName, item_id)
                if trigger == "info":
                    if MySet.StoreInfoWhisp:
                        if data.IsFromDiscord():
                            Parent.SendDiscordDM(data.User, message)
                        else:
                            Parent.SendStreamWhisper(data.UserName, message)
                    else:
                        SendResp(data, message)
                else:
                    SendResp(data, message)
            return None


def StoreList(data, page, command):
    """Based on settings in UI, will show a collection AKA page of basic item information"""
    # Sets variables
    path = os.path.join(os.path.dirname(__file__), "Items")
    item_list = [int(name.replace(".txt", "")) for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
    item_list.sort()
    page_max = -(-len(item_list) // MySet.StoreListNumber)
    # Checks for an incorrect data entry
    if page == "":
        message = "The format to use this command is [{0} list <page>], where page is a positive integer. " \
                  "There are {1} pages in total".format(MySet.command, page_max)
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
        except ValueError:
            message = "Sorry, but <page> must be a number. [{0} list page]".format(MySet.command)
            SendResp(data, message)
            return
    if page == 0:
        message = "0 is an invalid page number. Defaulting to the first page available:"
        SendResp(data, message)
        page = 1
    elif page > page_max and page != "all":
        message = "There are only {0} pages of items. Defaulting to the last page available:".format(page_max)
        SendResp(data, message)
        page = page_max
    # Grabs all items for the page
    if page == "all":
        startingitem = 0
        closingitem = len(item_list)
    else:
        startingitem = MySet.StoreListNumber * (page - 1)
        closingitem = min(MySet.StoreListNumber * page, len(item_list))

    list_contents = ""
    for x in range(startingitem, closingitem):
        item = LoadItem(data, item_list[x], Trigger.list)
        if item.setting == "Disabled" and not MySet.StoreListShowDisabled:
            continue
        list_contents += MySet.StoreListFormat.format(item.name, item.ID, item.cost, item.type, item.setting)

    message = MySet.StoreListMessage.format(list_contents, page, page_max)
    if MySet.StoreListWhisp:
        if data.IsFromDiscord():
            Parent.SendDiscordDM(data.User, message)
        else:
            Parent.SendStreamWhisper(data.UserName, message)
    else:
        SendResp(data, message)
    Parent.AddCooldown(ScriptName, command, MySet.timerCooldown)
    Parent.AddUserCooldown(ScriptName, command, data.User, MySet.timerUserCooldown)


def StoreInfo(data, item_id, command):
    """Item information function"""
    item = LoadItem(data, item_id, Trigger.info)
    if item:
        if item.setting == "Disabled":
            message = MySet.notenabled.format(data.UserName, item.ID)
            SendResp(data, message)
        else:
            message = MySet.storeinfosuccess.format(data.UserName, item.name, ItemType.ToText(item.type), item.ID,
                                                    item.cost, Parent.GetCurrencyName())
            if MySet.StoreInfoWhisp:
                if data.IsFromDiscord():
                    Parent.SendDiscordDM(data.User, message)
                else:
                    Parent.SendStreamWhisper(data.UserName, message)
            else:
                Parent.AddCooldown(ScriptName, command, MySet.timerCooldown)
                Parent.AddUserCooldown(ScriptName, command, data.User, MySet.timerUserCooldown)
                SendResp(data, message)


def Purchase(data, item_id):
    """Checks that all conditions for purchase are met"""
    # Checks if item purchases are enabled
    if not MySet.purchaseallow:
        message = "The streamer has all item purchases disabled currently."
        SendResp(data, message)
        return

    # Checks if the item exists
    item = LoadItem(data, item_id, Trigger.buy)
    if item is None:
        return

    # Checks if item is disabled
    if item.setting == "Disabled":
        message = MySet.notenabled.format(data.UserName, item_id)
        SendResp(data, message)
        return

    # Check if the item is on cooldown
    command = "Item{0}".format(item.ID)
    if not IsOnCooldown(data, command):
        return

    # Checks if user has permission to buy items
    if not HasPermission(data, item.permission, item.permissioninfo):
        return

    # Checks if item has high enough quantity
    if item.quantity < 1 and item.quantity != Item.noquantitylimit:
        message = MySet.quantitytoolow.format(data.UserName, item_id)
        SendResp(data, message)
        return

    # Contribute type specifics
    if item.type == ItemType.contribute:
        payment = data.GetParam(3)
        if not payment == "":
            try:
                payment = int(payment)
                if payment < 0:
                    raise ValueError("Negative values not permitted")
            except ValueError:
                message = "{0} -> Please use the format [{1} buy itemID amount] when " \
                          "buying a 'contribute' type item.".format(data.UserName, MySet.command)
                SendResp(data, message)
                return
        else:
            payment = item.cost
        Contributions(data, item, payment)
        return

    # Unique type specifics
    if ItemType.inventory and UserHasInv(data, item) or ItemType.unique and data.User in item.code:
        message = "{0} -> You have purchased this item before, so it is unavailable for you sorry".format(
            data.UserName)
        SendResp(data, message)
        return

    # Checks finished, start payment process
    if Parent.RemovePoints(data.User, data.UserName, item.cost):
        PurchaseSuccess(data, item)
    else:
        message = MySet.notenough.format(data.UserName, item.cost, Parent.GetCurrencyName(),
                                         Parent.GetPoints(data.UserName))
        SendResp(data, message)


def PurchaseSuccess(data, item):
    """Payment process for purchasing an item"""
    # Add cooldown to item
    command = "Item{0}".format(item.ID)
    Parent.AddCooldown(ScriptName, command, item.cooldown)
    Parent.AddUserCooldown(ScriptName, command, data.User, item.usercooldown)
    # Successful payment messages
    message = "Thanks for buying {0}. You now have {1} {2}".format(item.name, Parent.GetPoints(data.User),
                                                                   Parent.GetCurrencyName())
    if not data.IsFromYoutube():
        if data.IsFromDiscord():
            Parent.SendDiscordDM(data.User, message)
        else:
            Parent.SendStreamWhisper(data.UserName, message)
    else:
        SendResp(data, message)
    if item.type == ItemType.contribute:
        message = "Thanks {0}, you've just paid the final amount of {1} {2} to purchase {3} for the stream!".format(
            data.UserName, item.cost, Parent.GetCurrencyName(), item.name)
    else:
        message = MySet.itempurchasesuccess.format(data.UserName, item.name, item.cost,
                                                   Parent.GetCurrencyName())
    SendResp(data, message)
    if item.type == ItemType.code:
        message = "Your code for redeeming {0} is {1}.".format(item.name, item.code)
        # Sends message as a whisper
        if data.IsFromDiscord():
            Parent.SendDiscordDM(data.User, message)
        else:
            Parent.SendStreamWhisper(data.UserName, message)

    # Removes from quantity if appropriate
    if item.quantity > 0:
        item.quantity -= 1

    # Special saving conditions
    if item.type == ItemType.unique:
        item.code = item.code + data.User + "%#%"

    if item.type in [ItemType.once, ItemType.code, ItemType.contribute, ItemType.session, ItemType.inventory]:
        item.setting = "Disabled"
        if item.type == ItemType.session:
            global sessionItems
            sessionItems.add(item.ID)
        if item.type == ItemType.inventory:
            AddToInv(data, item)

    if MySet.DeleteOnRedeemCode and item.type == ItemType.code:
        items_path = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(item.ID))
        if os.path.exists(items_path):
            os.remove(items_path)
        else:
            Parent.Log(ScriptName, "Something went wrong! Please send Xailran a screenshot of this in discord,"
                                   "and give as much information as you can about what happened beforehand")
    else:
        item.Save()

    # Plays sound
    if item.sound != "None":
        sound = os.path.join(SoundPath, item.sound)
        soundQueue.append(sound)
    else:
        if MySet.enableSounds:
            if MySet.randomSounds:
                sound = "playrandom"
            else:
                sound = os.path.join(SoundPath, MySet.soundFile)
            soundQueue.append(sound)

    # Saves to log
    if MySet.stf:
        textline = MySet.textline.format(data.UserName, item.name, item.cost, Parent.GetCurrencyName(),
                                         datetime.datetime.now().strftime("Date: %d/%m-%Y Time: %H:%M:%S"))
        with codecs.open(LogFile, "a", "utf-8") as f:
            f.write(u"" + textline + "\r\n")


def SessionEnded():
    """Changes all session items to be enabled, ready for the next session"""
    global sessionItems
    for x in sessionItems:
        item = LoadItem(None, x, Trigger.sessionend)
        item.setting = "Enabled"
        item.Save()


def Contributions(data, item, payment):
    """Process for registering contributions to contribute type items"""
    # If user is attempting to pay full amount/excess of item cost
    if payment > item.cost:
        message = "{0} -> There are only {1} {2} remaining on this item. Reducing payment amount from {3} to {1}" \
            .format(data.UserName, str(item.cost), Parent.GetCurrencyName(), str(payment))
        SendResp(data, message)
        payment = item.cost
    # Adjust remaining cost of contribute item
    if Parent.RemovePoints(data.User, data.UserName, payment):
        item.cost = item.cost - payment
        # If full amount is paid, resets price, and sends messages
        if item.cost == 0:
            item.cost = item.cost
            PurchaseSuccess(data, item)
        # If item has not been finished
        else:
            message = "Thanks {0}! You have added {1} {2} to {3}, which now has {4} {2} remaining!".format(
                data.UserName, str(payment), Parent.GetCurrencyName(), item.name, item.cost)
            SendResp(data, message)
            item.Save()
    # If user can't afford to pay
    else:
        message = MySet.notenough.format(data.UserName, str(payment), Parent.GetCurrencyName(),
                                         Parent.GetPoints(data.UserName))
        SendResp(data, message)
        return


def StoreLog(data):
    """Function to check last (x) purchases"""
    # Check if a number was given
    if data.GetParam(2) == "":
        logcount = 10
        SendResp(data, "No value given, assigning default value of 10")
    # Check if entry was a valid integer
    else:
        try:
            logcount = abs(int(data.GetParam(2)))
        except ValueError:
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

    # Prints set amount of log entries, in order of latest to oldest
    with codecs.open(LogFile, encoding="utf-8-sig", mode="r") as text:
        item = [line.strip() for line in text]
        entries = len(item) - 1
        for x in range(0, logcount):
            if (entries - x) < 0:
                message = "Tried to load more log data, but none exists!"
                SendResp(data, message)
                break
            message = item[entries - x]
            SendResp(data, message)


def StoreToggle(data, item_id):
    """Toggles whether an item is enabled or disabled"""
    item = LoadItem(data, item_id, Trigger.toggle)
    if item is not None:

        if item.setting.lower() == "disabled":
            item.setting = "Enabled"
            message = "Item {0} has been successfully enabled!".format(item_id)
        else:
            item.setting = "Disabled"
            message = "Item {0} has been successfully disabled!".format(item_id)

        item.Save()
        SendResp(data, message)


def StoreDelete(data, item_id):
    """Deletes an item forever, freeing up its itemID to be used by the next item"""
    global DelConf
    # When item doesn't exist, reset the delete mode
    item = LoadItem(data, item_id, Trigger.delete)
    if item is None:
        DelConf = "Reset"
    # Process for when item exists
    else:
        # When delete command is set to this item
        if DelConf == item_id:
            items_path = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(item_id))
            os.remove(items_path)
            message = MySet.StoreDelMsg.format(item_id, data.UserName)
            SendResp(data, message)
            DelConf = "Reset"
        # Sets delete command to this item
        else:
            DelConf = item_id
            message = "Please send the delete command again to confirm deleting item {0}, {1}. " \
                      "DELETING AN ITEM CANNOT BE UNDONE".format(item_id, item.name)
            SendResp(data, message)


def StoreAdd(data, item_type):
    """Adding items to store function"""
    # Checks if enough information has been provided
    parameters = data.GetParamCount()
    if parameters <= 4:
        message = MySet.atsfailed
        SendResp(data, message)
        return
    item_type = ItemType.FromText(item_type)
    if parameters <= 5 and item_type == ItemType.code:
        message = "Command failed. Command format: {0} add code <cost/default> <ItemCode> <ItemName>. " \
                  "Make sure there are no spaces in the code, or it won't save properly!".format(MySet.command)
        SendResp(data, message)
        return

    # Establish data for the new item
    item_data = {"type": item_type}
    if data.GetParam(3).lower() == "default" or data.GetParam(3).lower() == "dflt":
        item_data["cost"] = MySet.atsdefaultcost
    else:
        try:
            item_data["cost"] = int(data.GetParam(3))
        except ValueError:
            message = "<cost> must be a number, or the word default. " \
                      "{0} was entered instead".format(data.GetParam(3).upper())
            SendResp(data, message)
            return

    # Sets code and name data for the item
    if item_type == ItemType.contribute:
        item_data["code"] = item_data["cost"]
        item_data["name"] = SaveItemName(data, 4, parameters)
    elif item_type == ItemType.unique:
        item_data["code"] = " "
        item_data["name"] = SaveItemName(data, 4, parameters)
    elif item_type == ItemType.code:
        item_data["code"] = data.GetParam(4)
        item_data["name"] = SaveItemName(data, 5, parameters)
    else:
        item_data["code"] = "None"
        item_data["name"] = SaveItemName(data, 4, parameters)

    item = Item(Item.CalcID(), "CREATE", item_data)
    item.Save()
    message = MySet.atssuccess.format(data.UserName, item.name, item.ID)
    SendResp(data, message)


def SaveItemName(data, start_params, params):
    """Function for collecting full item name"""
    item_name = ""
    for x in range(start_params, params):
        item_name += (data.GetParam(x) + " ")
    return item_name


def StoreEdit(data, item_id, edit_type, edit_value):
    item = LoadItem(data, item_id, Trigger.edit)
    message = ""
    if item is not None:
        if edit_type == "name" or edit_type == "itemname":
            message = item.EditName(SaveItemName(data, 4, data.GetParamCount()))
            SendResp(data, message)

        elif edit_type == "type":
            message = "Item types are core to how an item works, and it would be very easy for this to go wrong. " \
                      "Thus, editing item types has not been permitted"
            SendResp(data, message)

        elif edit_type == "permission":
            message = item.EditPermission(edit_value, data)
            SendResp(data, message)

        elif edit_type in ["cost", "cooldown", "usercooldown"]:
            try:
                edit_value = int(edit_value)
                if edit_value < 0:
                    raise ValueError("negative value")
            except ValueError:
                message = "[{0} edit itemID {1} value] When editing the {1} of an item, " \
                          "you must enter a positive integer as the value.".format(MySet.command, edit_type)
                SendResp(data, message)
                return
            else:
                if edit_type == "cost":
                    message = item.EditCost(edit_value)
                elif edit_type == "cooldown":
                    message = item.EditCooldown(edit_value)
                elif edit_type == "usercooldown":
                    message = item.EditUserCooldown(edit_value)
                SendResp(data, message)

        elif edit_type in ["quantity", "qnty", "qty"]:
            try:
                edit_value = int(edit_value)
                if edit_value < 0 and not edit_value == Item.noquantitylimit:
                    raise ValueError("negative value")
            except ValueError:
                message = "[{0} edit itemID {1} value] When editing the {1} of an item, " \
                          "you must enter a positive integer as the value, or the default " \
                          "value ({2})".format(MySet.command, edit_type, Item.noquantitylimit)
                SendResp(data, message)
                return
            else:
                message = item.EditQuantity(edit_value)
                SendResp(data, message)

        elif edit_type == "code":
            message = item.EditCode(edit_value)
            SendResp(data, message)

        elif edit_type == "sound":
            message = item.EditSound(edit_value)
            SendResp(data, message)

        # ItemEditType not recognised
        else:
            message = "[{0} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, cost, " \
                      "permission, cooldown, code, quantity, or sound".format(MySet.command)
            SendResp(data, message)
            return
        # Save item data changes
        item.Save()


def StoreHelp(data, command):
    """Adds a variety of help responses"""
    # Choosing which help message to send
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
        elif data.GetParam(3).lower() == "inventory":
            message = MySet.helpmessageAddInventory.format(data.UserName, MySet.command)
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
        Parent.AddCooldown(ScriptName, command, MySet.timerCooldown)
        Parent.AddUserCooldown(ScriptName, command, data.User, MySet.timerUserCooldown)
    if MySet.StoreHelpWhisp:
        if data.IsFromDiscord():
            Parent.SendDiscordDM(data.User, message)
        else:
            Parent.SendStreamWhisper(data.UserName, message)
    else:
        SendResp(data, message)


def EasterEggs(data, egg_val):
    """Some (hopefully) fun easter eggs, that add no actual functionality"""
    if MySet.EggsEnabled:
        if egg_val == "buyall":
            message = "Come on, isn't that just a LITTLE excessive {0}?".format(data.UserName)
            SendResp(data, message)
    Parent.AddCooldown(ScriptName, egg_val, MySet.timerCooldown)
    Parent.AddUserCooldown(ScriptName, egg_val, data.User, MySet.timerUserCooldown)


# ---------------------------------------
# Inventory
# ---------------------------------------
def StoreInventory(data):
    message = ""
    if data.GetParamCount() == 2:
        message = MySet.InvMsg.format(data.UserName, PrintInv(data.UserName))
    if data.GetParamCount() > 2:
        if data.GetParam(2).lower() == "reset":
            if HasPermission(data, MySet.InvPermission, MySet.InvPermissionInfo):
                # Specific reset
                if data.GetParamCount() > 3:
                    username = " ".join(data.GetParam(x) for x in xrange(3, data.GetParamCount()))
                    Parent.Log(ScriptName, PrintInv(username))
                    ResetUserInv(username)
                    message = "{0}'s inventory has been reset. A list of their inventory items have been sent " \
                              "to the script log in case of accident".format(username)
                # General reset
                else:
                    ResetInv()
                    message = "The inventory for all users has been reset! If you "
        else:
            message = MySet.InvMsg.format(data.UserName, PrintInv(data.UserName))
    SendResp(data, message)


def UserHasInv(data, item):
    invdata = LoadJSONFile(inventoryFile)
    if data.UserName in invdata:
        if item.name in invdata[data.UserName]:
            return True
    return False


def AddToInv(data, item):
    invdata = LoadJSONFile(inventoryFile)
    if data.UserName in invdata:
        invdata[data.UserName].append(item.name)
    else:
        invdata[data.UserName] = list()
        invdata[data.UserName].append(item.name)
    SaveJSONFile(inventoryFile, invdata)


def PrintInv(username):
    invdata = LoadJSONFile(inventoryFile)
    message = ""
    if username in invdata:
        message = ", ".join(invdata[username])
    return message


def ResetUserInv(username):
    invdata = LoadJSONFile(inventoryFile)
    if username in invdata:
        del invdata[username]
        SaveJSONFile(inventoryFile, invdata)


def ResetInv():
    contents = LoadJSONFile(inventoryFile)
    if contents:
        os.remove(inventoryFile)
        SaveJSONFile(backupInvFile, contents)


# ---------------------------------------
# Classes
# ---------------------------------------
class Item:
    """Object for loading, saving, and accessing items"""
    noquantitylimit = -1  # type: int # This must be a negative integer,
    # and should not be changed once the script has been used at least once

    def __init__(self, item_id, mode="LOAD", item_data=None):
        """init for loading an item"""
        if item_data is None:
            item_data = {}
        self.ID = 0
        self.setting = "Disabled"
        self.name = ""
        self.type = ItemType.general
        self.permission = "Everyone"
        self.permissioninfo = ""
        self.cost = 0
        self.cooldown = 0
        self.usercooldown = 0
        self.code = ""
        self.sound = "None"
        self.quantity = Item.noquantitylimit

        if mode == "LOAD":
            self.Load(item_id)
        else:  # mode = "CREATE"
            self.Create(item_id, item_data)

    def EditName(self, edit_value):
        if edit_value == "":
            message = "[{0} edit itemID name value]. Value is equal to the new name " \
                      "you wish to change the item to".format(MySet.command)
        else:
            temp_name = self.name
            self.name = edit_value
            message = "Success! {0} ({1}) has changed from '{0}' to '{2}'!".format(temp_name, self.ID, self.name)
        return message

    def EditCost(self, edit_value):
        message = "Success! {0} ({1}) has changed from {2} {3} to {4} {3}".format(self.name, self.ID, self.cost,
                                                                                  Parent.GetCurrencyName(), edit_value)
        self.cost = edit_value
        if self.type == ItemType.contribute:
            self.code = self.cost
        return message

    def EditCooldown(self, edit_value):
        message = "Success! {0} ({1}) has changed from {2} seconds to {3} seconds".format(self.name, self.ID,
                                                                                          self.cooldown, edit_value)
        self.cooldown = edit_value
        return message

    def EditUserCooldown(self, edit_value):
        message = "Success! {0} ({1}) has changed from {2} seconds to {3} seconds".format(self.name, self.ID,
                                                                                          self.usercooldown, edit_value)
        self.usercooldown = edit_value
        return message

    def EditPermission(self, edit_value, data):
        edit_value = edit_value.lower()
        old_permission = self.permission
        old_pinfo = self.permissioninfo

        perm_values = {"everyone": "Everyone", "regular": "Regular", "VIP exclusive": "VIP Exclusive",
                       "vip+": "VIP+", "subscriber": "Subscriber", "gamewispsubscriber": "GameWispSubscriber",
                       "moderator": "Moderator", "editor": "Editor", "caster": "Caster"}
        perm_sp_values = {"min_rank": "Min_Rank", "min_points": "Min_Points", "min_hours": "Min_Hours",
                          "user_specific": "User_Specific"}

        if edit_value in perm_values:
            self.permission = perm_values[edit_value]

        elif edit_value in perm_sp_values:
            self.permission = perm_values[edit_value]
            if data.GetParamCount() == 5:
                message = "When setting the {1} permission, you need to choose a value! " \
                          "[{0} edit itemID permission {1} value]".format(MySet.command, self.permission)
                return message

            if self.permission == "Min_Rank":
                rank = ""
                for x in range(5, data.GetParamCount()):
                    rank += data.GetParam(x)
                self.permissioninfo = rank
            else:
                self.permissioninfo = data.GetParam(5)
        else:
            values = perm_values.values() + perm_sp_values.values()
            message = "The valid item permission values that can be changed through this command are: ".join(values)
            return message
        message = "Success! {0} ({1}) has changed from ({2}/{3}) to ({4}/{5})".format(self.name, self.ID,
                                                                                      old_permission, old_pinfo,
                                                                                      self.permission,
                                                                                      self.permissioninfo)
        return message

    def EditCode(self, edit_value):
        if edit_value == "":
            message = "[{0} edit itemID code value]. Value is equal to the new code you wish to assign to the " \
                      "item. WARNING: This will delete the old code!".format(MySet.command)
        elif self.type != ItemType.code:
            message = "Items with the '{0}' type don't have a code! " \
                      "Please try again with another item.".format(self.type)
        else:
            message = "Success! {0} ({1}) has changed from {2} to {3}".format(self.name, self.ID, self.code, edit_value)
            self.code = edit_value
        return message

    def EditSound(self, edit_value):
        if edit_value == "":
            message = "[{0} edit itemID sound filename]. Filename must be in the format of 'name.mp3', " \
                      "or it won't play correctly".format(MySet.command)
        else:
            message = "Success! {0} ({1}) has changed from {2} to {3}".format(self.name, self.ID, self.sound,
                                                                              edit_value)
            self.sound = edit_value
        return message

    def EditQuantity(self, edit_value):
        message = "Success! {0} ({1}) has changed from {2} to {3} copies. (Set to {4} to remove the limit)"\
            .format(self.name, self.ID, self.quantity, edit_value, Item.noquantitylimit)
        self.quantity = edit_value
        if self.type == ItemType.contribute:
            self.code = self.cost
        return message

    def Create(self, item_id, item_data):
        self.ID = item_id
        self.setting = "Enabled"
        self.name = item_data["name"]
        self.type = item_data["type"]
        self.permission = MySet.Permission
        self.permissioninfo = MySet.PermissionInfo
        self.cost = item_data["cost"]
        self.cooldown = MySet.timerCooldown
        self.usercooldown = MySet.timerUserCooldown
        self.code = item_data["code"]
        self.sound = "None"
        self.quantity = Item.noquantitylimit

    def Load(self, item_id):
        items_path = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(item_id))
        item_info = LoadTextFile(items_path)
        if item_info:
            self.ID = item_id
            self.setting = item_info[0]
            self.name = item_info[1]
            self.type = ItemType.FromText(item_info[2])
            self.cost = int(item_info[4])
            self.code = item_info[6]
            try:
                self.sound = item_info[7]
            except IndexError:
                self.sound = None
            try:
                self.quantity = int(item_info[8])
            except IndexError:
                self.quantity = Item.noquantitylimit

            permission_data = item_info[3].split(" ")
            self.permission = permission_data[0]
            try:
                self.permissioninfo = permission_data[1]
            except IndexError:
                self.permissioninfo = ""

            cooldown_data = item_info[5].split(" ")
            self.cooldown = int(cooldown_data[0])
            try:
                self.usercooldown = int(cooldown_data[1])
            except IndexError:
                self.usercooldown = self.cooldown

        # If item cannot be found
        else:
            raise IOError("Item file does not exist!")

    def Save(self):
        save_item_path = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(self.ID))
        item_type = ItemType.ToText(self.type)
        with codecs.open(save_item_path, "w", "utf-8") as f:
            filedata = self.setting + "\r\n" + self.name + "\r\n" + item_type + "\r\n" + self.permission + \
                       " " + self.permissioninfo + "\r\n" + str(self.cost) + "\r\n" + str(self.cooldown) + \
                       " " + str(self.usercooldown) + "\r\n" + str(self.code) + "\r\n" + self.sound + \
                       "\r\n" + str(self.quantity)
            f.write(filedata)

    @staticmethod
    def CalcID():
        path = os.path.join(os.path.dirname(__file__), "Items")
        item_limit = int(len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]) + 2)
        for x in range(1, item_limit):
            items_path = os.path.join(os.path.dirname(__file__), "Items\\{0}.txt".format(x))
            if not os.path.exists(items_path):
                return x


class ItemType:
    failed = -1
    general = 1
    code = 2
    once = 3
    contribute = 4
    unique = 5
    session = 6
    inventory = 7

    @staticmethod
    def FromText(str_type):
        str_type = str_type.lower()
        if str_type == "general": return ItemType.general
        if str_type == "code": return ItemType.code
        if str_type in ["once", "once-off"]: return ItemType.once
        if str_type in ["ctb", "cont", "contribute"]: return ItemType.contribute
        if str_type == "unique": return ItemType.unique
        if str_type in ["session", "stream"]: return ItemType.session
        if str_type in ["inventory", "inv"]: return ItemType.inventory
        return -1

    @staticmethod
    def ToText(itemtype):
        if itemtype == ItemType.general: return "general"
        if itemtype == ItemType.code: return "code"
        if itemtype == ItemType.once: return "once"
        if itemtype == ItemType.contribute: return "contribute"
        if itemtype == ItemType.unique: return "unique"
        if itemtype == ItemType.session: return "session"
        if itemtype == ItemType.inventory: return "inventory"
        return ""

    @staticmethod
    def TypesMessage():
        return "The valid item types are [General], [Code], [Once], [Unique], " \
               "[Contribute/CTB], [Session], or [Inventory/Inv]"


class Trigger:
    none = "NONE"
    info = "INFO"
    list = "LIST"
    buy = "BUY"
    sessionend = "SESSIONEND"
    toggle = "TOGGLE"
    delete = "DELETE"
    edit = "EDIT"
    inventory = "INVENTORY"


class Settings:
    """ Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, system, settings_file=None):
        if settings_file and os.path.isfile(settings_file):
            with codecs.open(settings_file, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
        else:  # set variables if no custom settings file is found
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
            self.StoreListMessage = "Format = Item Name (itemID, item cost). {0}. Page {1}/{2}"
            self.StoreListFormat = "{0} ({1}, {2}). "
            self.SLSAusage = "Stream Chat"
            self.StoreDelEnable = False
            self.StoreDelPermission = "Caster"
            self.StoreDelPermissionInfo = ""
            self.stf = True
            self.StoreLogPermission = "Editor"
            self.StoreLogPermissionInfo = ""
            self.textline = "{4}: {0} - {1} - {2} {3}"
            self.InvPermission = "Editor"
            self.InvPermissionInfo = ""
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
            self.quantitytoolow = "{0} -> there aren't any remaining copies of item {1}"
            self.incorrectusage = "{0} -> That command is designated for use in the following location: {1}"
            self.listbase = "There are currently {0} items in the store. Use [{1} info <#>] to learn about an item, " \
                            "or [{1} buy <#>] to buy an item"
            self.atssuccess = "{1} (ID: {2}) has successfully been added by {0}!"
            self.atsfailed = "Command failed. Command format: !store add <ItemType> <cost/default> <ItemName>"
            self.storeinfosuccess = "{0} -> {1} ({2}) is available for {4} {5}"
            self.StoreDelMsg = "Item {0} has been successfully deleted by {1}"
            self.InvMsg = "{0}, the following items are in your inventory: {1}"
            self.EggsEnabled = True
            self.helpmessageGeneral = "The available parameters for [{1} help <function>] are add, buy, delete, " \
                                      "info, list, log, edit, and toggle"
            self.helpmessageBuy = "{0} -> Use [{1} buy #] to purchase an item. If the item has the 'contribute' " \
                                  "type, you can put an amount to pay after specifying the item number"
            self.helpmessageInfo = "{0} -> Use [{1} info #] to get a detailed information message about item #!"
            self.helpmessageList = "Use [{1} list <page>] to see a collection of items at once, with their name, " \
                                   "item number, and cost"
            self.helpmessageAdd = "[{1} add <ItemType> <cost/default> <ItemName>]. Add an item for viewers " \
                                  "to purchase with {2}! You can also use [{1} toggle] to enable/disable an " \
                                  "existing item in the store. Use {0} help add " \
                                  "[general/once/code/contribute/unique] for more information."
            self.helpmessageAddGeneral = "[{1} add general <cost/default> <ItemName>] Use this function to add items " \
                                         "that can be bought multiple times"
            self.helpmessageAddContribute = "[{1} add contribute <cost/default> <ItemName>] Use this function to add " \
                                            "items that can everyone can work together to purchase. Can also use " \
                                            "'ctb' as a short form for contribute"
            self.helpmessageAddUnique = "[{1} add unique <cost/default> <ItemName>] Use this function to add items " \
                                        "that can only be purchased once per user."
            self.helpmessageAddOnce = "[{1} add once <cost/default> <ItemName>] Use this function to add items that " \
                                      "can only be purchased once"
            self.helpmessageAddSession = "[{1} add session <cost/default> <ItemName>] Use this function to add items " \
                                         "that can only be purchased once per session. " \
                                         "A session ends when the script is restarted, or the bot is closed."
            self.helpmessageAddInventory = "[{1} add inventory <cost/default> <ItemName>] Use this function to add " \
                                           "items that can be bought and then shown off (like a trophy). " \
                                           "Items of this type act like Once-Off items otherwise."
            self.helpmessageAddCode = "[{1} add code <cost/default> <ItemCode> <ItemName>] use this function to add " \
                                      "items that contain a code, so the bot can send a whisper containing the code. " \
                                      "Code items can only be purchased once"
            self.helpmessageAddCode2 = "Make sure there are no spaces in the ItemCode, or it won't save properly!"
            self.helpmessageLog = "When you use [{1} log #], it will load the last # entries, and post them in chat. " \
                                  "If no number is given, it will load the last 10 entries. " \
                                  "If # is higher than the amount of entries, the bot will load as many as it can " \
                                  "before returning an error message."
            self.helpmessageToggle = "Use [{1} toggle #] to enable or disable the purchase of an existing item! " \
                                     "Useful if you have a once-off item that you want to make available, " \
                                     "or you don't want a general item to be purchased for whatever reason"
            self.helpmessageEdit = "[{1} edit <itemID> <DataType> <#>]. <DataType> can be an item's name, cost, " \
                                   "permission, cooldown, or code"
            self.helpmessageDelete = "Use [{1} delete #] to completely remove an item from the system, " \
                                     "and allow another item to take its item ID. Once deleted, " \
                                     "it can't be undone, so use with caution!"

        self.parent = system

    # Reload settings on save through UI
    def Reload(self, data):
        """Reload settings on save through UI"""
        system = self.parent
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        self.parent = system

    def Save(self, settings_file):
        """ Save settings contained within the .json and .js settings files. """
        try:
            with codecs.open(settings_file, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            with codecs.open(settings_file.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except ValueError:
            MessageBox(0, u"Settings failed to save to file",
                       u"Saving failed", 0)
