## Standard library imports
import json
import random
import time
from typing import ClassVar, NoReturn, Any, Union, Set, Dict  # Add Dict for type hints
# Related third-party module imports
import telebot
from telebot import types  # Correctly import types here
import phonenumbers
import countryflag
# Local application module imports
from src import utils
from src.utils import User
from src.vneng import VNEngine
# Initialize the bot token
bot: ClassVar[Any] = telebot.TeleBot(utils.get_token())
print(f":: Bot is running with ID: {bot.get_me().id}")

# Define admin ID (replace with the actual admin user ID)
ADMIN_ID = 7046488481  # Replace with your admin's Telegram ID

# Initialize user storage
user_ids: Set[int] = set()
blocked_users: Set[int] = set()
referral_data: Dict[int, int] = {}  # {referrer_id: referral_count}
user_referrals: Dict[int, str] = {}  # {user_id: invite_link}

# Amount of invites needed to unlock OTP
INVITES_NEEDED = 2

@bot.message_handler(commands=["start", "restart"])
def start_command_handler(message):
    """
    Handles /start or /restart commands.
    Tracks referrals and sends welcome messages.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"

    # Extract referral information if available
    referrer_id = None
    if " " in message.text:
        try:
            referrer_id = int(message.text.split(" ")[1])
        except ValueError:
            pass

    # Add the new user to the user list
    if user_id not in user_ids:
        user_ids.add(user_id)

        # Notify admin about the new user
        bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🆕 New User Started the Bot:\n"
                f"Username: @{username}\n"
                f"User ID: {user_id}\n"
                f"Referred By: {referrer_id or 'No Referrer'}\n"
                f"Total Users: {len(user_ids)}"
            )
        )

        # Track referrals if referrer_id is valid
        if referrer_id and referrer_id in user_ids:
            referral_data[referrer_id] = referral_data.get(referrer_id, 0) + 1
            bot.send_message(
                chat_id=referrer_id,
                text=(
                    f"🎉 *You invited a new user* ➕ \n"
                    f"👥 *Total Invites*: {referral_data[referrer_id]}"
                )
            )

    # Generate and store the user's referral link
    invite_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    user_referrals[user_id] = invite_link

    # Create the channel join buttons
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Jᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟷⚡️", url="https://t.me/your_channel_1"),
        types.InlineKeyboardButton("Jᴏɪɴ ᴄʜᴀɴɴᴇʟ 2⚡️", url="https://t.me/your_channel_2"),
        types.InlineKeyboardButton("🔐𝗝𝗼𝗶𝗻𝗲𝗱", callback_data="check_numb")
    )

    # Send welcome message with the referral link
    bot.send_message(
        chat_id=user_id,
        text=(
            "⚠️ 𝙄𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩 𝙮𝙤𝙪 𝙝𝙖𝙫𝙚 𝙩𝙤 𝙟𝙤𝙞𝙣 𝙤𝙪𝙧 𝙩𝙚𝙡𝙚𝙜𝙧𝙖𝙢 𝙘𝙝𝙖𝙣𝙣𝙚𝙡𝙨.\n"
            "Hᴇʏ ᴜsᴇʀ, ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ Jᴏɪɴ ʙᴏᴛʜ ᴛʜᴇsᴇ ᴄʜᴀɴɴᴇʟs.\n\n"
            "ᴏᴛʜᴇʀᴡɪsᴇ, ᴛʜɪs ʙᴏᴛ ᴡɪʟʟ ɴᴏᴛ ᴡᴏʀᴋ. Iғ ʏᴏᴜ ʜᴀᴠᴇ 🔐𝗝𝗼𝗶𝗻𝗲𝗱 ᴛʜᴇ ᴄʜᴀɴɴᴇʟs, "
            "ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴛʜᴇ Jᴏɪɴᴇᴅ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴄᴏɴғɪʀᴍ ʏᴏᴜʀ ʙᴏᴛ ᴍᴇᴍʙᴇʀsʜɪᴘ.\n\n"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# Start the bot polling



@bot.callback_query_handler(func=lambda call: call.data == "check_numb")
def check_numb_callback(call):
    """
    Handles the callback for the '🔐 Joined' button.
    Displays the user's invite stats and referral link.
    """

    user_id = call.message.chat.id
    total_invites = referral_data.get(user_id, 0)
    invite_link = user_referrals.get(user_id, "Not Available")

    # Send photo with options and user's referral stats
    photo_url = "https://l.arzfun.com/hKNPI"
    description = (
        f"Hi, welcome! Please choose from the options below.\n\n"
        f"👥 Total Invites: {total_invites}\n"
        f"🔗 Your Invite Link: {invite_link}"
    )

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Free number", callback_data="check_number"),
        types.InlineKeyboardButton("VIP number", callback_data="vip_number")
    )

    bot.send_photo(
        chat_id=user_id,
        photo=photo_url,
        caption=description,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "vip_number")
def vip_number_callback(call):
    """
    Sends the VIP number options when 'VIP number' button is clicked.
    Shows a list of numbers the user can choose from.
    """

    # Create the inline keyboard with the number buttons
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    # Create a button for each individual number
    keyboard.add(
        types.InlineKeyboardButton("123", callback_data="123"),
        types.InlineKeyboardButton("435", callback_data="435"),
        types.InlineKeyboardButton("163", callback_data="163"),
        types.InlineKeyboardButton("8627", callback_data="8627"),
        types.InlineKeyboardButton("62718", callback_data="62718"),
        types.InlineKeyboardButton("100828", callback_data="100828"),
        types.InlineKeyboardButton("66", callback_data="66"),
        types.InlineKeyboardButton("6728", callback_data="6728"),
        types.InlineKeyboardButton("6182", callback_data="6182"),
        types.InlineKeyboardButton("8372", callback_data="8372")
    )

    # Send message with number selection options
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Please choose a VIP number:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data in ["123", "435", "163", "8627", "62718", "100828", "66", "6728", "6182", "8372"])
def number_buttons_callback(call):
    """
    Handles the callback for when any of the number buttons is clicked.
    Checks if the user has enough invites to unlock the number.
    """

    user_id = call.message.chat.id
    total_invites = referral_data.get(user_id, 0)
    number = call.data

    if total_invites >= INVITES_NEEDED:
        # User has enough invites to unlock the number
        bot.send_message(
            chat_id=user_id,
            text=f"You unlocked this number ({number})!\n\nClick below to get your OTP."
        )

        # Create InlineKeyboardMarkup with the 'Get OTP' button
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton("Get OTP", callback_data=f"get_otp_{number}"))

        # Send the message with the OTP button
        bot.send_message(
            chat_id=user_id,
            text="Click the button below to get your OTP.",
            reply_markup=keyboard
        )
    else:
        # User does not have enough invites
        bot.send_message(
            chat_id=user_id,
            text="❌ You do not have enough invites to unlock this number.\n"
                 f"You need {INVITES_NEEDED - total_invites} more invite(s) to proceed."
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_otp_"))
def get_otp_callback(call):
    """
    Handles the callback for the 'Get OTP' button.
    Sends a randomly generated 5-digit OTP when the button is clicked.
    """

    otp = random.randint(10000, 99999)
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Your OTP is: {otp}"
    )








@bot.message_handler(commands=["top"])
def top_referrers_handler(message):
    """
    Handles the /top command.
    Sends the top 10 users with the highest referrals.
    """

    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    if not referral_data:
        bot.reply_to(message, "No referrals data available.")
        return

    # Sort referral_data by referral count in descending order
    sorted_referrals = sorted(referral_data.items(), key=lambda x: x[1], reverse=True)
    
    # Get the top 10 users
    top_referrers = sorted_referrals[:10]

    # Build the message
    response = "🏆 *Top 10 Referrers:*\n\n"
    for i, (user_id, count) in enumerate(top_referrers, start=1):
        username = bot.get_chat(user_id).username or "N/A"
        response += f"{i}. @{username} (ID: {user_id}) - {count} Invites\n"

    bot.send_message(
        chat_id=ADMIN_ID,
        text=response,
        parse_mode="Markdown"
    )


@bot.message_handler(commands=["info"])
def user_info_handler(message):
    """
    Handles the /info command.
    Requests the admin to provide a user ID, then displays their referral data.
    """

    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    # Ask for user ID
    sent_message = bot.reply_to(message, "Please provide the User ID to view their information:")

    # Register next step handler
    bot.register_next_step_handler(sent_message, send_user_info)


def send_user_info(message):
    """
    Sends the specific user's information after receiving their ID.
    """

    try:
        user_id = int(message.text)

        if user_id not in user_ids:
            bot.reply_to(message, "❌ User not found.")
            return

        # Get user details
        total_invites = referral_data.get(user_id, 0)
        invite_link = user_referrals.get(user_id, "Not Available")
        username = bot.get_chat(user_id).username or "N/A"

        # Build the message
        response = (
            f"👤 *User Info:*\n"
            f"• Username: @{username}\n"
            f"• User ID: {user_id}\n"
            f"• Total Invites: {total_invites}\n"
            f"• Invite Link: {invite_link}\n"
        )

        bot.send_message(
            chat_id=ADMIN_ID,
            text=response,
            parse_mode="Markdown"
        )
    except ValueError:
        bot.reply_to(message, "❌ Invalid User ID. Please provide a valid numeric User ID.")






#start

# Additional functionality to handle adding, reducing, and resetting points for users
@bot.message_handler(commands=["add"])
def add_command_handler(message):
    """
    Handles the /add command sent by the admin.
    Displays buttons for managing user points.
    """
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    # Create buttons for the admin
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Add points for one user", callback_data="add_one_user"),
        types.InlineKeyboardButton("Add points for every user", callback_data="add_all_users"),
        types.InlineKeyboardButton("Reduce points for one user", callback_data="reduce_one_user"),
        types.InlineKeyboardButton("Reduce points for every user", callback_data="reduce_all_users"),
        types.InlineKeyboardButton("Reset points for one user", callback_data="reset_one_user"),
        types.InlineKeyboardButton("Reset points for every user", callback_data="reset_all_users"),
    )

    bot.send_message(
        chat_id=message.chat.id,
        text="Choose an option:",
        reply_markup=keyboard
    )



# Resetting points of a single user
@bot.callback_query_handler(func=lambda call: call.data == "reset_one_user")
def reset_one_user_callback(call):
    """
    Handles the button for resetting points of a single user.
    Prompts the admin to enter the user ID or username.
    """
    bot.send_message(chat_id=call.message.chat.id, text="Please send the user ID or username to reset points:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_reset_one_user)

def process_reset_one_user(message):
    """
    Processes the user ID or username entered by the admin.
    Resets the user's points to 0.
    """
    user_identifier = message.text
    user_id = int(user_identifier) if user_identifier.isdigit() else None

    if user_id and user_id in user_ids:
        referral_data[user_id] = 0
        bot.send_message(
            chat_id=user_id,
            text="❌ Your invite points have been reset to 0."
        )
        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ Reset points of user {user_id} to 0."
        )
    else:
        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❌ User ID/Username {user_identifier} not found."
        )

# Resetting points of all users
@bot.callback_query_handler(func=lambda call: call.data == "reset_all_users")
def reset_all_users_callback(call):
    """
    Handles the button for resetting points of all users.
    Resets all users' points to 0.
    """
    for user_id in user_ids:
        referral_data[user_id] = 0
        bot.send_message(
            chat_id=user_id,
            text="❌ Your invite points have been reset to 0."
        )

    bot.send_message(
        chat_id=ADMIN_ID,
        text="✅ Reset points of all users to 0."
    )





# Adding points to one user
@bot.callback_query_handler(func=lambda call: call.data == "add_one_user")
def add_one_user_callback(call):
    """
    Handles the button for adding points to a single user.
    Prompts the admin to enter the user ID or username.
    """

    bot.send_message(chat_id=call.message.chat.id, text="Please send the user ID or username:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_add_one_user)

def process_add_one_user(message):
    """
    Processes the user ID or username entered by the admin.
    Prompts for the amount of points to add.
    """

    user_identifier = message.text

    def process_points_amount(message):
        try:
            points = int(message.text)
            user_id = int(user_identifier) if user_identifier.isdigit() else None

            if user_id and user_id in user_ids:
                referral_data[user_id] = referral_data.get(user_id, 0) + points
                bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 {points} invite(s) have been added to your account!"
                )
                bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"✅ Added {points} invite(s) to user {user_id}."
                )
            else:
                bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"❌ User ID/Username {user_identifier} not found."
                )
        except ValueError:
            bot.send_message(chat_id=ADMIN_ID, text="❌ Invalid amount. Please try again.")

    bot.send_message(chat_id=ADMIN_ID, text="Enter the amount of invites to add:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, process_points_amount)

# Adding points to all users
@bot.callback_query_handler(func=lambda call: call.data == "add_all_users")
def add_all_users_callback(call):
    """
    Handles the button for adding points to all users.
    Prompts the admin to enter the amount of points to add.
    """

    bot.send_message(chat_id=call.message.chat.id, text="Enter the amount of invites to add to all users:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_add_all_users)

def process_add_all_users(message):
    """
    Processes the amount of points to add for all users.
    """

    try:
        points = int(message.text)
        for user_id in user_ids:
            referral_data[user_id] = referral_data.get(user_id, 0) + points
            bot.send_message(
                chat_id=user_id,
                text=f"🎉 {points} invite(s) have been added to your account!"
            )

        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ Added {points} invite(s) to all users."
        )
    except ValueError:
        bot.send_message(chat_id=ADMIN_ID, text="❌ Invalid amount. Please try again.")

# Reducing points from one user
@bot.callback_query_handler(func=lambda call: call.data == "reduce_one_user")
def reduce_one_user_callback(call):
    """
    Handles the button for reducing points from a single user.
    Prompts the admin to enter the user ID or username.
    """

    bot.send_message(chat_id=call.message.chat.id, text="Please send the user ID or username:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_reduce_one_user)

def process_reduce_one_user(message):
    """
    Processes the user ID or username entered by the admin.
    Prompts for the amount of points to reduce.
    """

    user_identifier = message.text

    def process_points_amount(message):
        try:
            points = int(message.text)
            user_id = int(user_identifier) if user_identifier.isdigit() else None

            if user_id and user_id in user_ids:
                referral_data[user_id] = max(referral_data.get(user_id, 0) - points, 0)
                bot.send_message(
                    chat_id=user_id,
                    text=f"❌ {points} invite(s) have been deducted from your account."
                )
                bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"✅ Deducted {points} invite(s) from user {user_id}."
                )
            else:
                bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"❌ User ID/Username {user_identifier} not found."
                )
        except ValueError:
            bot.send_message(chat_id=ADMIN_ID, text="❌ Invalid amount. Please try again.")

    bot.send_message(chat_id=ADMIN_ID, text="Enter the amount of invites to reduce:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, process_points_amount)

# Reducing points from all users
@bot.callback_query_handler(func=lambda call: call.data == "reduce_all_users")
def reduce_all_users_callback(call):
    """
    Handles the button for reducing points from all users.
    Prompts the admin to enter the amount of points to reduce.
    """

    bot.send_message(chat_id=call.message.chat.id, text="Enter the amount of invites to reduce from all users:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_reduce_all_users)

def process_reduce_all_users(message):
    """
    Processes the amount of points to reduce for all users.
    """

    try:
        points = int(message.text)
        for user_id in user_ids:
            referral_data[user_id] = max(referral_data.get(user_id, 0) - points, 0)
            bot.send_message(
                chat_id=user_id,
                text=f"❌ {points} invite(s) have been deducted from your account."
            )

        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ Deducted {points} invite(s) from all users."
        )
    except ValueError:
        bot.send_message(chat_id=ADMIN_ID, text="❌ Invalid amount. Please try again.")

# Existing code remains unchanged



# Start the bot



@bot.message_handler(commands=["statistics"])
def statistics_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle /statistics command for the admin.

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """
    # Check if the user is the admin
    if message.from_user.id == ADMIN_ID:
        # Send statistics about total users and blocked users
        bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"📊 Total Users Started the Bot: {len(user_ids)}\n"
                f"🚫 Total Blocked Users: {len(blocked_users)}"
            )
        )
    else:
        # Notify non-admin user that they don't have access
        bot.reply_to(message, "⚠️ You do not have permission to use this command.")





@bot.message_handler(commands=["broadcast"])
def broadcast_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle /broadcast command for the admin.

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """
    # Check if the user is the admin and if the command is used in a reply
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        broadcast_count = 0
        # Broadcast message or file to all users
        for user_id in user_ids:
            try:
                if user_id in blocked_users:
                    continue  # Skip blocked users

                if message.reply_to_message.text:
                    bot.send_message(chat_id=user_id, text=message.reply_to_message.text)
                elif message.reply_to_message.document:
                    bot.send_document(chat_id=user_id, document=message.reply_to_message.document.file_id)
                elif message.reply_to_message.photo:
                    bot.send_photo(chat_id=user_id, photo=message.reply_to_message.photo[-1].file_id,
                                   caption=message.reply_to_message.caption)
                elif message.reply_to_message.video:
                    bot.send_video(chat_id=user_id, video=message.reply_to_message.video.file_id,
                                   caption=message.reply_to_message.caption)
                elif message.reply_to_message.audio:
                    bot.send_audio(chat_id=user_id, audio=message.reply_to_message.audio.file_id)
                elif message.reply_to_message.voice:
                    bot.send_voice(chat_id=user_id, voice=message.reply_to_message.voice.file_id)
                # Add more media types as needed (e.g., animation, contact, location)

                broadcast_count += 1
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
        
        # Notify admin of the broadcast status
        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ Broadcast sent to {broadcast_count} users successfully."
        )
    else:
        bot.reply_to(message, "⚠️ Reply to a message with /broadcast to send it to all users.")

@bot.message_handler(commands=["number"])
def number_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle /number command and send a virtual number.

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """
    # Fetch user's data
    user: ClassVar[Union[str, int]] = User(message.from_user)

    # Check if the user joined the necessary channels before allowing the number command
    if not utils.has_joined_channels(message.from_user.id):
        bot.send_message(
            chat_id=message.chat.id,
            text="⚠️ Please join the required channels first to access this feature."
        )
        return

    # Simulate sending a virtual number
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    bot.send_message(
        chat_id=message.chat.id,
        text=(
            f"🌐 Here is your virtual number, {user.pn}!\n"
            "Your generated virtual number is +1234567890 (example).\n"
            "You can use this number for various purposes.\n\n"
            "If you'd like another number, just press the button again!"
        )
    )

# Callback handler for "Check" button to trigger /number command directly
@bot.callback_query_handler(func=lambda call: call.data == "check_number")
def check_number_callback(call: ClassVar[Any]) -> NoReturn:
    """
    Handle callback for "Check" button by running the /number command logic.

    Parameters:
        call (ClassVar[Any]): Incoming callback query.

    Returns:
        None (NoReturn)
    """
    # Directly call the /number command handler function
    number_command_handler(call.message)

@bot.message_handler(commands=["help", "usage"])
def help_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle help commands in bot
    Shows help messages to users

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """

    # Fetch user's data
    user: ClassVar[Union[str, int]] = User(message.from_user)

    # Send Help message
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    bot.reply_to(
        message=message,
        text=(
           "·ᴥ· Virtual Number Bot\n\n"
           "This bot is using API from onlinesim.io and fetches "
           "online and active numbers.\n"
           "All you need is sending few commands to the bot and it will "
           "find a random number for you.\n\n══════════════\n"
           "★ To get a new number you can simply send the /number command "
           "or you can use the inline button (Renew) to re-new your number.\n\n"
           "★ To get inbox messages use (inbox) inline button. This will show you "
           "the last 5 messages.\n\n"
           "★ You can also check the number's Telegram profile using the inline button "
           "(check phone number's profile).\n══════════════\n\n"
           "This is all you need to know about this bot!"
        )
    )

# Start polling












@bot.message_handler(commands=["number"])
def number_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle number commands in bot
    Finds and sends new virtual number to user

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """

    # Send waiting prompt
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    prompt: ClassVar[Any] = bot.reply_to(
        message=message,
        text=(
            "Getting a random number for you...\n\n"
            "⁀➴ Fetching online countries:"
        ),
    )

    # Initialize the Virtual Number engine
    engine: ClassVar[Any] = VNEngine()

    # Get the countries and shuffle them
    countries: List[Dict[str, str]] = engine.get_online_countries()
    random.shuffle(countries)

    # Update propt based on current status
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=prompt.message_id,
        text=(
            "Getting a random number for you...\n\n"
            "⁀➴ Fetching online countries:\n"
            f"Got {len(countries)} countries\n\n"
            "⁀➴ Testing active numbers:\n"
        ),
    )

    # Find online and active number
    for country in countries:
        # Get numbers in country
        numbers: List[Dict[str, str]] = engine.get_country_numbers(
            country=country['name']
        )
        
        # Format country name
        country_name: str = country["name"].replace("_", " ").title()
    
        # Check numbers for country and find first valid one
        for number in numbers:
            # Parse the country to find it's details
            parsed_number: ClassVar[Union[str, int]] = phonenumbers.parse(
                number=f"+{number[1]}"
            )

            # Format number to make it readable for user
            formatted_number: str = phonenumbers.format_number(
                numobj=parsed_number,
                num_format=phonenumbers.PhoneNumberFormat.NATIONAL
            )

            # Find flag emoji for number
            flag: str = countryflag.getflag(
                [
                    phonenumbers.region_code_for_country_code(
                        country_code=parsed_number.country_code
                    )
                ]
            )

            # Update prompt based on current status
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=prompt.message_id,
                text=(
                    "Getting a random number for you...\n\n"
                    "⁀➴ Fetching online countries:\n"
                    f"Got {len(countries)} countries\n\n"
                    "⁀➴ Testing active numbers:\n"
                    f"Trying {country_name} ({formatted_number})"
                ),
            ) 

            # Check if number is valid and it's inbox is active
            if engine.get_number_inbox(country['name'], number[1]):
                # Make keyboard markup for number
                Markup: ClassVar[Any] = telebot.util.quick_markup(
                    {
                        "𖥸 Inbox": {
                            "callback_data": f"msg&{country['name']}&{number[1]}"
                        },

                        "꩜ Renew": {
                            "callback_data": f"new_phone_number"
                        },

                        "Check phone number's profile": {
                            "url": f"tg://resolve?phone=+{number[1]}"
                        }
                    }, 
                    row_width=2
                )
                
                # Update prompt based on current status
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=prompt.message_id,
                    text=(
                        "Getting a random number for you...\n\n"
                        "⁀➴ Fetching online countries:\n"
                        f"Got {len(countries)} countries\n\n"
                        "⁀➴ Testing active numbers:\n"
                        f"Trying {country_name} ({formatted_number})\n\n"
                        f"{flag} Here is your number: +{number[1]}\n\n"
                        f"Last Update: {number[0]}"
                    ),
                    reply_markup=Markup
                )

                # Return the function
                return 1
    
    # Send failure message when no number found
    else:
        # Update prompt based on current status
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=prompt.message_id,
            text=(
                    "Getting a random number for you...\n\n"
                    "⁀➴ Fetching online countries:\n"
                    f"Got {len(countries)} countries\n\n"
                    "⁀➴ Testing active numbers:\n"
                    f"There is no online number for now!"
                ),
        ) 

        # Return the function
        return 0


@bot.callback_query_handler(func=lambda x:x.data.startswith("msg"))
def number_inbox_handler(call: ClassVar[Any]) -> NoReturn:
    """
    Callback query handler to handle inbox messages
    Sends last 5 messages in number's inbox

    Parameters:
        call (typing.ClassVar[Any]): incoming call object

    Returns:
        None (typing.NoReturn)
    """
    # Initialize the Virtual Number engine
    engine: ClassVar[Any] = VNEngine()

    # Get country name and number from call's data
    country: str
    number: str
    _, country, number = call.data.split("&")

    # Get all messages and select last 5 messages
    messages: List[Dict[str, str]] = engine.get_number_inbox(
        country=country, 
        number=number
    )[:5]

    # Send messages to user
    for message in messages:
        for key, value in message.items():
            bot.send_message(
                chat_id=call.message.chat.id,
                reply_to_message_id=call.message.message_id,
                text=(
                    f"⚯͛ Time: {key}\n\n"
                    f"{value.split('received from OnlineSIM.io')[0]}"
                )
            )

    # Answer callback query
    bot.answer_callback_query(
        callback_query_id=call.id,
        text=(
            "⁀➴ Here is your last 5 messages\n\n"
            "If you didn't get your message, try again after 1 minute!"
        ),
        show_alert=True
    )


@bot.callback_query_handler(func=lambda x:x.data == "new_phone_number")
def new_number_handler(call):
    """
    Callback query handler to re-new number
    Find new phone number and updates the message

    Parameters:
        call (typing.ClassVar[Any]): incoming call object

    Returns:
        None (typing.NoReturn)
    """
    # Get chat id and message id from call object
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Edit message based on current status
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            "Getting a random number for you...\n\n"
            "⁀➴ Fetching online countries:"
        ),
    )

    # Initialize the Virtual Number engine
    engine: ClassVar[Any] = VNEngine()

    # Get the countries and shuffle them
    countries: List[Dict[str, str]] = engine.get_online_countries()
    random.shuffle(countries)

    # Update prompt based on current status
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            "Getting a random number for you...\n\n"
            "⁀➴ Fetching online countries:\n"
            f"Got {len(countries)} countries\n\n"
            "⁀➴ Testing active numbers:\n"
        ),
    )

    # Find online and active number
    for country in countries:
        # Get numbers in country
        numbers: List[Dict[str, str]] = engine.get_country_numbers(
            country=country['name']
        )
        
        # Format country name
        country_name: str = country["name"].replace("_", " ").title()
    
        # Check numbers for country and find first valid one
        for number in numbers:
            # Parse the country to find it's details
            parsed_number: ClassVar[Union[str, int]] = phonenumbers.parse(
                number=f"+{number[1]}"
            )

            # Format number to make it readable for user
            formatted_number: str = phonenumbers.format_number(
                numobj=parsed_number,
                num_format=phonenumbers.PhoneNumberFormat.NATIONAL
            )

            # Find flag emoji for number
            flag: str = countryflag.getflag(
                [
                    phonenumbers.region_code_for_country_code(
                        country_code=parsed_number.country_code
                    )
                ]
            )

            # Update prompt based on current status
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    "Getting a random number for you...\n\n"
                    "⁀➴ Fetching online countries:\n"
                    f"Got {len(countries)} countries\n\n"
                    "⁀➴ Testing active numbers:\n"
                    f"Trying {country_name} ({formatted_number})"
                ),
            ) 

            # Check if number is valid and it's inbox is active
            if engine.get_number_inbox(country['name'], number[1]):
                # Make keyboard markup for number
                Markup: ClassVar[Any] = telebot.util.quick_markup(
                    {
                        "𖥸 Inbox": {
                            "callback_data": f"msg&{country['name']}&{number[1]}"
                        },

                        "꩜ Renew": {
                            "callback_data": f"new_phone_number"
                        },

                        "Check phone number's profile": {
                            "url": f"tg://resolve?phone=+{number[1]}"
                        }
                    }, 
                    row_width=2
                )
                
                # Update prompt based on current status
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=(
                        "Getting a random number for you...\n\n"
                        "⁀➴ Fetching online countries:\n"
                        f"Got {len(countries)} countries\n\n"
                        "⁀➴ Testing active numbers:\n"
                        f"Trying {country_name} ({formatted_number})\n\n"
                        f"{flag} Here is your number: +{number[1]}\n\n"
                        f"Last Update: {number[0]}"
                    ),
                    reply_markup=Markup
                )

                # Answer callback query
                bot.answer_callback_query(
                    callback_query_id=call.id,
                    text="⁀➴ Your request updated",
                    show_alert=False
                )

                # Return the function
                return 1
    
    # Send failure message when no number found
    else:
        # Update prompt based on current status
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=(
                    "Getting a random number for you...\n\n"
                    "⁀➴ Fetching online countries:\n"
                    f"Got {len(countries)} countries\n\n"
                    "⁀➴ Testing active numbers:\n"
                    f"There is no online number for now!"
                ),
        ) 

        # Return the function
        return 0


# Run the bot in polling mode with enhanced error handling
if __name__ == '__main__':
    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,  # Skip any pending updates for faster start-up
                timeout=10,  # Timeout for long polling
                long_polling_timeout=5  # Telegram's server timeout
            )
        except KeyboardInterrupt:
            print("\n\33[1;31m::\33[m Bot terminated by user")
            raise SystemExit
        except Exception as e:
            # Log the error and restart polling
            print(f"\n\33[1;31m::\33[m An error occurred: {e}")
            print("Restarting bot in 5 seconds...")
            time.sleep(5)  # Delay before restarting to avoid rapid retries

