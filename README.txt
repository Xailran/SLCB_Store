#####################
#   Store Script    #
#####################

Description: Allow your viewers to spend points to buy items or perks that you create! 
Made By: Xailran
Website: https://www.twitch.tv/xailran

#############################
#         Versions          #
#############################
1.3.0 - (Public Build 2) - Added [!store delete] function. Altered file saving system so that the delete function could be added, and for a bug fix. Rather than just increasing the item ID by 1 for every new item, the script will search for the lowest positive integer that it can set the item ID to.
1.2.0 - Added Mixer and YouTube functionality
1.1.2 - Commands can now be sent as whispers. Added toggle for allowing items to be bought through whispers.
1.1.1 - Fixed user cooldowns to actually be used!
1.1.0 - Added [!store toggle] and [!store help] functions
1.0.2.1 - (Public Build 1) - Minor text changes
1.0.2 - Fixed store log to actually use permissions.
1.0.1 - Minor bug fixes and text changes
1.0.0 - Initial Release

#####################
#       Usage       #
#####################
	EDITOR ONLY
!store add <ItemType> <cost/default> <Item Name>
Adds a purchasable item for viewers. See below for specifics
Default cost changes for each item type, changeable in UI

!store log <#>
Shows last <x> purchases (user, time of purchase, item)
Default <#> is 10

!store toggle <#>
Disables or enables an item, depending on its current setting.
WARNING: Items with codes are automatically disabled on purchase. Enabling them again could result in giving away a dodgy code!

	STREAMER ONLY
!store delete <#>
Deletes an item permanently, allowing its item ID to be used by the next new item. The command needs to be entered twice as a safeguard, in case a mistake is made.
WARNING: Once you delete an item, there is no going back! Make sure you are absolutely sure before using this command!!

	ALL VIEWERS
!store buy <#>
Purchase item # in the store

!store info <#>
Outputs ItemName, ItemType, and cost of the chosen id

!store
Shows how many items are currently in the store, and points to !store info and buy

!store help <function>

<function> = add, delete, log, toggle, buy, info

###########################
#   Adding General Items  #
###########################
Can be purchased multiple times, ideal for things such as instagram follows, push-ups, etc.

!store add general <cost/default> <Item Name>

###############################
#   Adding Items With Codes   #
###############################
Used for items containing sensitive information like codes, will whisper the user the code so it doesn't get snatched up in chat!

!store add code <cost/default> <code> <Item Name>
The <code> must not have any spaces in it, or part of the code will be shown in the item name!!

Note: This part of the script is removed for YouTube streams, as there is no whisper function to handle sensitive information like codes. A work-around is to use the once-off function for items with codes, and contact the people who purchased those items yourself, in a manner that suits you.

######################
#   Once-Off Items   #
######################
Used for items that can only be bought once before being disabled. Ideal for items that are extremely rare.
In a future update, editors (depending on your permission settings) will be able to re-enable these items, to be bought again.

!store add once <cost/default> <ItemName>

####################
#   Unique Items   #   COMING SOON
####################
Once-off items and general items put together! Unique items can be purchased an unlimited number of times, but only once per user. Useful for things such as twitter or instagram follows.

!store add unique <cost/default> <ItemName>

####################
#  Future Updates  #
####################
These are not in any particular order, just things I would like to add someday.

- Change !store info failed responses to follow whisper setting
- Make more messages customizable
- If enough people want it, I can add a toggle for "only when live" for each non-mod function (buy, help, info), rather than just the one toggle. The UI is already quite large, hence why I haven't added it already.
- Add overlay functionality
- Add sound functionality
- Add cuztomizable cooldown for general items. (As in, each general item can have its own cooldown, or follow the default)
- Add Discord functionality
- Add Mixer/YT functionality
- Add [!store add unique <cost/default> <ItemName>]. The unique itemtype will be like general, where it can be bought multiple times, but only once per user. This is useful for items such as twitter follows, adding on snapchat, etc.

2.0.0 update will be when data switches from being stored in a txt to a JSON
- Add [!store convert <#>] command, so that all data can be transferred across without any loss


#############################################
# Tag me in the Streamlabs Chatbot discord  #
#    if you have any questions or ideas!    #
#   https://discordapp.com/invite/J4QMG5m   #
#############################################