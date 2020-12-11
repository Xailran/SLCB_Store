#####################
#   Store Script    #
#####################

Description: Allow your viewers to spend points to buy items or perks that you create! 
Made By: Xailran
Website: https://www.twitch.tv/xailran

#############################
#         Versions          #
#############################
1.1.2 - Commands can now be sent as whispers. Added toggle for allowing items to be bought through whispers.
1.1.1 - Fixed user cooldowns to actually be used!
1.1.0 - Added !store toggle and !store help functions
1.0.2.1 - Minor text changes
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

	ALL VIEWERS
!store buy <#>
Purchase item # in the store

!store info <#>
Outputs ItemName, ItemType, and cost of the chosen id

!store
Shows how many items are currently in the store, and points to !store info and buy

!store help <function>

<function> = add, log, toggle, buy, info

###########################
#   Adding General Items  #
###########################
Can be purchased multiple times, ideal for things such as instagram follows, push-ups, etc.

!store add general <cost/default> <Item Name>

###############################
#   Adding Items With Codes   #
###############################
Used for items containing sensitive information like codes, will whisper the user the code so it doesn't get snatched up in chat!

!store add steam <cost/default> <code> <Item Name>
The <code> must not have any spaces in it, or part of the code will be shown in the item name!!

############################
#   Other Once-Off Items   #
############################
Used for items that can only be bought once before being disabled. Ideal for items that are extremely rare.
In a future update, editors (depending on your permission settings) will be able to re-enable these items, to be bought again.

!store add once <cost/default> <ItemName>

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