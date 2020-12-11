#####################
#   Store Script    #
#####################

Description: Allow your viewers to spend points to buy items or perks that you create! 
Made By: Xailran
Website: https://www.twitch.tv/xailran

#############################
#         Versions          #
#############################
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

!store log <x>
Shows last <x> purchases (user, time of purchase, item)
Default <x> is 10

	ALL VIEWERS
!store buy <#>
Purchase item # in the store

!store info <#>
Outputs ItemName, ItemType, and cost of the chosen id

!store
Shows how many items are currently in the store, all available parameters

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
These are not in any particular order, these are just things I would like to add someday.

- Change !store info failed responses to follow whisper setting
- Add [!store enable/disable <#>], to enable/disable an item within the store.
- If enough people want it, I can add a toggle for "only when live" for each function (add, buy, log, info, !store), rather than just the one toggle. The UI is already quite large, hence why I haven't added it already.
- Add [!store help <x>] to provide help with specific parameters in a whisper. Eg. buy or add
- Add overlay functionality
- Add sound functionality
- Add cuztomizable cooldown for general items. (As in, each general item can have its own cooldown, or follow the default)
- Add Discord functionality
- Add Mixer/YT functionality

ONCE UPDATED TO 2.0.0! (Switching to using a JSON file, rather than multiple txts)
- Add [!store convert <#>] command, so that all data can be transferred across without any loss

#############################################
# Tag me in the Streamlabs Chatbot discord  #
#    if you have any questions or ideas!    #
#   https://discordapp.com/invite/J4QMG5m   #
#############################################