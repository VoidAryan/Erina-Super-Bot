from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors.rpcerrorlist import (
    ChannelPrivateError,
    PeerIdInvalidError,
    UserNotParticipantError
)
from telethon.utils import get_display_name
from telethon import *
from pymongo import MongoClient
from EmikoRobot import API_ID, API_HASH, TOKEN, DEV_USERS as OWNER_ID , telethn as tbot
from EmikoRobot.events import register
from EmikoRobot.modules.helper_funcs.requestModule import *
import logging
import os
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# IN_GRP = -1001415010098
bot = asst = tbot
# REQ_GO =  -1001509437008
on = tbot.on
auth = OWNER_ID # No more need

mongoDbSTR = os.environ.get("MONGO_DB_URI")
requestRegex = "#[rR][eE][qQ][uU][eE][sS][tT] (.*)"

'''Connecting To Database'''
mongo_client = MongoClient(mongoDbSTR)
db_bot = mongo_client['RequestTrackerBot']
collection_ID = db_bot['channelGroupID']


@tbot.on(events.NewMessage(pattern = requestRegex))
async def filter_requests(event):
    if event.fwd_from or event.post:
        return
    else:
        IN_GRP = f"-100{event.peer_id.channel_id}"

        documents = collection_ID.find()
        for document in documents:
            try:
                document[IN_GRP]
            except KeyError:
                continue
            else:
                REQ_GO = int(document[IN_GRP][0])
                IN_GRP = int(IN_GRP)

        #  await asst.send_message(IN_GRP,
            #                    f"**We are not taking any requests for some days.\n\nSorry for inconvenience 😶**",
            #                    buttons=[
            #                        [Button.url("💠 Channel 💠", url="https://t.me/AN1ME_HUB"),
            #                        Button.url("⚜️ Group ⚜️", url="https://t.me/an1me_hub_discussion")],
            #                        [Button.url("📜 Index 📜", url="https://t.me/index_animehub"),
            #                        Button.url("🎬 Movies 🎬", url="https://t.me/AN1ME_HUB_MOVIES")],
            #                        [Button.url("💌 AMV 💌", url="https://t.me/AnimeHub_Amv")]])
                if (event.reply_to_msg_id):
                    msg = (await event.get_reply_message()).message
                else:
                    msg = event.text
                try:
                    global user
                    sender = event.sender
                    if sender.bot:
                        return
                    if not sender.username:
                        user = f"[{get_display_name(sender)}](tg://user?id={event.sender_id})"
                    else:
                        user = "@" + str(sender.username)
                except BaseException:
                    user = f"[User](tg://user?id={event.sender_id})"
                chat_id = (str(event.chat_id)).replace("-100", "")
                username = ((await bot.get_entity(REQ_GO)).username)
                hel_ = "#request"
                if hel_ in msg:
                    global anim
                    anim = msg.replace(hel_, "")
                x = await asst.send_message(REQ_GO,
                                        f"**Request By {user}**\n\n{msg}",
                                        buttons=[
                                            [Button.url("Requested Message", url=f"https://t.me/c/{chat_id}/{event.message.id}")],
                                            [Button.inline("🚫 Reject", data="reqdelete"),
                                            Button.inline("Done ✅", data="isdone")],
                                            [Button.inline("⚠️ Unavailable ⚠️", data="unavl")]])
                btns = [
                    [Button.url("⏳ Request Status ⏳", url=f"https://t.me/{username}/{x.id}")]]
                await event.reply(f"**👋 Hello {user} !!**\n\n📍 Your Request for  `{anim}`  has been submitted to the admins.\n\n🚀 Your Request Will Be Uploaded In 48hours or less.\n📌 Please Note that Admins might be busy. So, this may take more time. \n\n**👇 See Your Request Status Here 👇**", buttons=btns)
                if not auth:
                    async for x in bot.iter_participants("@Anime_X-Clan", filter=ChannelParticipantsAdmins):
                        auth.append(x.id)

# For Adding group & channel ID in database for #request feature
@tbot.on(events.NewMessage(pattern = "/addrequest"))
async def addIDHandler(event):
    msg = event.text.split(" ")
    if len(msg) == 3:
        _, groupID, channelID = msg
        try:
            int(groupID)
            int(channelID)
        except ValueError:
            await event.respond(
                "<b>Group ID & Channel ID should be integer type😒.</b>",
                parse_mode = "html"
            )
        else:
            documents = collection_ID.find()
            for document in documents:
                try:
                    document[groupID]
                except KeyError:
                    pass
                else:
                    await event.respond(
                    "<b>Your Group ID already Added🤪.</b>",
                    parse_mode = "html"
                    )
                    break
                for record in document:
                    if record == "_id":
                        continue
                    else:
                        if document[record][0] == channelID:
                            return await event.respond(
                                "<b>Your Channel ID already Added🤪.</b>",
                                parse_mode = "html"
                            )
            else:
                try:
                    botSelfGroup = await tbot(GetParticipantRequest(int(groupID), 'me'))
                except TypeError:
                    try:
                        async for botSelfGroup in tbot.iter_participants(int(groupID), filter = ChannelParticipantsAdmins):
                            if not botSelfGroup.is_self:
                                return await event.respond(
                                    "<b>😁Add me in group and make me admin, then use /add.</b>",
                                    parse_mode = "html"
                                )
                    except (ValueError, PeerIdInvalidError):
                        return await event.respond(
                            "<b>😒Group ID is wrong.</b>",
                            parse_mode = "html"
                        )
                except (ValueError, PeerIdInvalidError):
                    return await event.respond(
                        "<b>😒Group ID is wrong.</b>",
                        parse_mode = "html"
                    )
                except ChannelPrivateError:
                    return await event.respond(
                        "<b>😁Add me in group and make me admin, then use /add.</b>",
                        parse_mode = "html"
                    )
                else:
                    partcpt = botSelfGroup.participant
                    try:
                        partcpt.promoted_by
                    except AttributeError:
                        return await event.respond(
                            "<b>🥲Make me admin in Group, Then add use /add.</b>",
                            parse_mode = "html"
                        )
                try:
                    botSelfChannel = await tbot(GetParticipantRequest(int(channelID), 'me'))
                except (ValueError, TypeError):
                    await event.respond(
                        "<b>😒Channel ID is wrong.</b>",
                        parse_mode = "html"
                    )
                except (ChannelPrivateError, UserNotParticipantError):
                    await event.respond(
                        "<b>😁Add me in Channel and make me admin, then use /add.</b>",
                        parse_mode = "html"
                    )
                else:
                    rights = botSelfChannel.participant.admin_rights
                    if not (rights.post_messages and rights.edit_messages and rights.delete_messages):
                        await event.respond(
                            "<b>🥲Make sure to give Permissions like Post Messages, Edit Messages & Delete Messages.</b>",
                            parse_mode = "html"
                        )
                    else:
                        collection_ID.insert_one(
                            {
                                groupID : [channelID, event.sender_id]
                            }
                        )
                        await event.respond(
                            "<b>Your Group and Channel has now been added SuccessFully🥳.</b>",
                            parse_mode = "html"
                        )
    else:
        await event.respond(
            "<b>Invalid Format😒\nSend Group ID & Channel ID in this format <code>/add GroupID ChannelID</code>.</b>",
            parse_mode = "html"
        )
    return

# For Removing group & channel ID from database
@tbot.on(events.NewMessage(pattern = "/removerequest"))
async def removeIDHandler(event):
    msg = event.text.split(" ")
    if len(msg) == 2:
        _, groupID = msg
        try:
            int(groupID)
        except ValueError:
            await event.respond(
                "<b>Group ID should be integer type😒.</b>",
                parse_mode = "html"
            )
        else:
            documents = collection_ID.find()
            for document in documents:
                try:
                    document[groupID]
                except KeyError:
                    continue
                else:
                    if document[groupID][1] == event.sender_id:
                        collection_ID.delete_one(document)
                        await event.respond(
                            "<b>Your Channel ID & Group ID has now been Deleted😢 from our Database.\nYou can add them again by using <code>/add GroupID ChannelID</code>.</b>",
                            parse_mode = "html"
                        )
                    else:
                        await event.respond(
                            "<b>😒You are not the one who added this Channel ID & Group ID.</b>",
                            parse_mode = "html"
                        )
                    break
            else:
                await event.respond(
                    "<b>Given Group ID is not found in our Database🤔.</b>",
                    parse_mode = "html"
                )
    else:
        await event.respond(
            "<b>Invalid Command😒\nUse <code>/remove GroupID</code></b>.",
            parse_mode = "html"
        )
    return

@tbot.on(events.callbackquery.CallbackQuery(data="reqdelete"))
async def delete_message(e):
    channelID = f"-100{e.original_update.peer.channel_id}"

    documents = collection_ID.find()
    for document in documents:
        for key in document:
            if key == "_id":
                continue
            else:
                if document[key][0] != channelID:
                    continue
                else:
                    groupID = key
                    async for x in tbot.iter_participants(int(channelID), filter=ChannelParticipantsAdmins):
                        if x.id == e.sender_id:
                            tx = await tbot.get_messages(e.chat_id, ids=e.message_id)
                            xx = tx.raw_text
                            btns = [
                                [Button.url("💠 Start Bot 💠", url="https://t.me/DakiSuperbot")]]
                        
                            await e.edit(f"**REJECTED**\n\n~~{xx}~~", buttons=[Button.inline("Request Rejected 🚫", data="ndone")])
                            await tbot.send_message(int(groupID), f"**⚠️ Request Rejected By Admin !!**\n\n~~{xx}~~", buttons=btns)
                            break
                    else:
                        await e.answer("Who TF are you? This is for admins only..", alert=True, cache_time=0)
    return
        
@tbot.on(events.callbackquery.CallbackQuery(data="unavl"))
async def delete_message(e):
    channelID = f"-100{e.original_update.peer.channel_id}"

    documents = collection_ID.find()
    for document in documents:
        for key in document:
            if key == "_id":
                continue
            else:
                if document[key][0] != channelID:
                    continue
                else:
                    groupID = key
                    async for x in tbot.iter_participants(int(channelID), filter=ChannelParticipantsAdmins):
                        if x.id == e.sender_id:
                            tx = await tbot.get_messages(e.chat_id, ids=e.message_id)
                            xx = tx.raw_text
                            btns = [
                                [Button.url("💠 Start Bot 💠", url="https://t.me/Erina_GroupBot")]]
                            await e.edit(f"**UNAVAILABLE**\n\n~~{xx}~~", buttons=[Button.inline("❗ Unavailable ❗", data="navl")])
                            await tbot.send_message(int(groupID), f"**⚠️ Request Unavailable ⚠️**\n\n~~{xx}~~", buttons=btns)
                            break
                    else:
                        await e.answer("Who TF are you? This is for admins only..", alert=True, cache_time=0)
    return
        
@tbot.on(events.callbackquery.CallbackQuery(data="isdone"))
async def isdone(e):
    channelID = f"-100{e.original_update.peer.channel_id}"

    documents = collection_ID.find()
    for document in documents:
        for key in document:
            if key == "_id":
                continue
            else:
                if document[key][0] != channelID:
                    continue
                else:
                    groupID = key

                    async for x in tbot.iter_participants(int(channelID), filter=ChannelParticipantsAdmins):
                        if x.id == e.sender_id:
                            tx = await tbot.get_messages(e.chat_id, ids=e.message_id)
                            xx = tx.raw_text
                            btns = [
                                [Button.url("💠 Start Bot 💠", url="https://t.me/Erina_GroupBot")]]
                            await e.edit(f"**COMPLETED**\n\n~~{xx}~~", buttons=[Button.inline("Request Completed ✅", data="donne")])
                            await tbot.send_message(int(groupID), f"**Request Completed**\n\n~~{xx}~~", buttons=btns)
                            break
                    else:
                        await e.answer("Who TF are you? This is for admins only..", alert=True, cache_time=0) 
    return
        
    
@tbot.on(events.callbackquery.CallbackQuery(data="donne"))
async def ans(e):
    await e.answer("This Request Is Completed... Checkout @Anime_X-Clan 💖", alert=True, cache_time=0)
        
@tbot.on(events.callbackquery.CallbackQuery(data="navl"))
async def ans(e):
    await e.answer("This Request Is Marked Unavailable By Admins", alert=True, cache_time=0)
        
        
@tbot.on(events.callbackquery.CallbackQuery(data="ndone"))
async def ans(e):
    await e.answer("This Request is unavailable... Ask Admins in @Anime_X-Clan for help. 💞", alert=True, cache_time=0)


__mod_name__ = "Requester"

__help__ = """
*Request Tracker Module Normally Created For Movies And Animes Channel To Manage Thier Users Requests.*
 ❍ /addrequest groupid channelid
 ❍ Example : /addrequest -100123456789 -1000987654321
 ❍ /removerequest groupid
 
 Created By @AjTimePyro
 """
