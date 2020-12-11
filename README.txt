#####################
#   Store Script    #
#####################

Description: Allow your viewers to spend points to buy items or perks that you create! 
Made By: Xailran
Website: https://www.twitch.tv/xailran
	 https://www.twitter.com/xailran

#############################
#         Versions          #
#############################

2.0.2.1 - Fixed issue causing inventory items to not be saved to a player's inventory.
          Creates item folder if it does not exist
2.0.2 - Deprecated once-off items with the addition of quantities. Revised inventory items to be alike to uniques.
2.0.1 - Changed list messages to be customizable. Added quantities that can be added to items
2.0.0 - Added list and sound functionality, and new item types. "Help" messages are now customizable. Major code re-work 
        (Inventory systems funded by Andrew [TLUN])

1.5.2 - Updated permission types
1.5.1 - (Public Build 3.1) Turns out removing the Dev Mode option broke things. Things aren't broken anymore.
1.5.0 - (Public Build 3) Added "edit" function. Added "unique" item type. Added Discord functionality.
        PermissionInfo settings are actually followed now
1.4.1 - Changed !store info failed responses to follow whisper setting
1.4.0 - Added "Contribute" item type!
1.3.1 - Minor text changes, bug fixes
1.3.0 - (Public Build 2) - Added [!store delete] function. Altered file saving system accordingly
1.2.0 - Added Mixer and YouTube functionality
1.1.2 - Commands can now be sent as whispers. Added toggle for allowing items to be bought through whispers.
1.1.1 - Fixed user cooldowns to actually be used!
1.1.0 - Added "toggle" and "help" functions
1.0.2.1 - (Public Build 1) - Minor text changes
1.0.2 - Fixed store log to actually use permissions.
1.0.1 - Minor bug fixes and text changes
1.0.0 - Initial Release

Bug fixes since last update:
None

Known bugs/issues:
None

#####################
#       Usage       #
#####################
	EDITOR ONLY
!store add <ItemType> <cost/default/dflt> <Item Name>
Adds a purchasable item for viewers. See below for specifics
Default cost is the same for each item type, and can be changed in the UI. Dlft also works, as short form for default

!store edit <ItemID> <DataType> <Value>
Use this command to change something in an existing item
<DataType> = Item name, type, permission, cost, cooldown, code, or sound.

!store log <#>
Shows last <x> purchases (user, time of purchase, item)
Default <#> is 10

!store toggle <#>
Disables or enables an item, depending on its current setting.
WARNING: Items with codes are automatically disabled on purchase. Enabling them again could result in giving away a dodgy code!

!store inventory reset <User Name>
Removes all items from <User Name>. If no name is given, the full system inventory is wiped. If wiping full inventory system, a backup file is saved.
Only one of these files is saved though, so using the command again will erase it.
WARNING: While an emergency list of an individual user's items is sent to the script logs, these are only temporary! This command cannot be undone!

	STREAMER ONLY
!store delete <#>
Deletes an item permanently, allowing its item ID to be used by the next new item. The command needs to be entered twice as a safeguard, in case a mistake is made.
WARNING: Once you delete an item, there is no going back! Make sure you are absolutely sure before using this command!!

	ALL VIEWERS
!store
Shows how many items are currently in the store, and points to !store info and buy

!store list <page>
Lists a collection of items together, organised by item number. Shows in the format ItemName(item number, item cost).

!store info <#>
Outputs ItemName, ItemType, and cost of the chosen id

!store buy <#> (CTBvalue)
Purchase item # in the store. 
If the item is of the "contribute" item type, they need to specify how much they are contributing as their (CTBvalue). If the user has enough to pay off the full amount however, they don't need to include a (CTBvalue)

!store help <function> <function2>
<function> = add, delete, edit, list, log, toggle, buy, info
For <function> = add; <function2> = general, once, code, contribute/ctb, unique, session

!store inventory
Sends a message containing all the items the user has in their inventory

###########################
#   Adding General Items  #
###########################
Can be purchased multiple times, ideal for things such as push-ups, doing a speed drawing, etc.

!store add general <cost/default> <Item Name>

###############################
#   Adding Items With Codes   #
###############################
Used for items containing sensitive information like codes, will whisper the user the code so it doesn't get snatched up in chat!
A perfect example of something you would use this item type for, is steam codes.

!store add code <cost/default> <Item Code> <Item Name>
The <Item Code> must not have any spaces in it, or part of the code will be shown in the item name!!

Note: This part of the script is removed for YouTube streams, as there is no whisper function to handle sensitive information like codes. A solution is to use the once-off function for items with codes, and contact the people who purchased those items yourself, in a manner that suits you. A work-around using discord will be worked on soon.

######################
#   Once-Off Items   #
######################
Used for items that can only be bought once before being disabled. Ideal for items that are extremely rare.
In a future update, editors (depending on your permission settings) will be able to re-enable these items, to be bought again.

!store add once <cost/default> <ItemName>

########################
#   Contribute Items   #
########################
Once-off items, that the whole stream can work together to buy! Users choose how many points to put towards the item. Once the full price has been paid, the item will be disabled in the store, and reset to its original price.
Useful for things such as stream goals.

!store add contribute <cost/default> <ItemName>
OR
!store add ctb <cost/default> <ItemName>

####################
#   Unique Items   #
####################
Once-off items and general items put together! Unique items can be purchased an unlimited number of times, but only once per user. Useful for things such as twitter or instagram follows.

!store add unique <cost/default> <ItemName>

WARNING: If users change their name, they will be able to buy the unique item again

#####################
#   Session Items   #
#####################
Session items are almost the same as Once-Off items, except they automatically turn back on whenever you refresh the script tab or restart the chatbot

!store add session <cost/default> <ItemName>

#######################
#   Inventory Items   #     NEW!!
#######################
These items aren't intended to have any tangible reward. Rather, they function as "trophies", that users can purchase to show off (using the "!store inventory" command).
Otherwise, these items function as once-off items, and thus need to be created and/or repeatedly enabled per time you wish for the item to be bought.

!store add inventory <cost/default> <ItemName>
OR
!store add inv <cost/default> <ItemName>

####################
#  Future Updates  #
####################
These are not in any particular order, just things I would like to add someday. If you really want to see a particular update, let me know! 

- Make more messages customizable (ongoing)
- Switch codes from once-off design to single quantity items.
- Add overlay functionality
- Show top/all contributors to buying a "contribution" type item upon purchase of said item.
- Add "Reset" function, to allow unique items to be purchased by those whom have already purchases that item once, to restore contribute type items to their original price, or re-enable session type items
- Add "Organize" function, to fix item IDs, and fix any gaps

#############################################
#   Donations are never expected, but any   #
#    support definitely helps, and keeps    #
#     me able to make more free scripts!    #
#       https://streamlabs.com/xailran      # 
#############################################
#############################################
# Tag me in the Streamlabs Chatbot discord  #
#    if you have any questions or ideas!    #
#   https://discordapp.com/invite/J4QMG5m   #
#############################################