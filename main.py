# Standard library imports
import json
import random
import time
from typing import ClassVar, NoReturn, Any, Union, List, Dict

# Related third-party module imports
import telebot
import phonenumbers
import countryflag
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Local application module imports
from src import utils
from src.utils import User
from src.vneng import VNEngine

# Initialize the bot token
bot: ClassVar[Any] = telebot.TeleBot(utils.get_token())
print(f"\33[1;36m::\33[m Bot is running with ID: {bot.get_me().id}")
# Replace 'yourchannel' with the actual channel username
REQUIRED_CHANNEL = "SHMMHS1"

# List to hold user IDs
user_ids: List[int] = []  # This should be persistent, consider using a database or file to store it
total_users: int = 0  # Counter for total users who have started the bot

# Define your admin user ID here
ADMIN_USER_ID = 7046488481  # Replace with the actual admin ID

# Dictionary to hold user referrals
user_referrals: Dict[int, List[int]] = {}  # This stores user ids that referred other users

@bot.message_handler(commands=["start", "restart"])
def start_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle start commands in bot
    Shows welcome messages to users or prompts them to join the required channel.

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """

    global total_users  # Use the global counter

    # Check if the user is a member of the required channel
    user_status = bot.get_chat_member(chat_id=f"@{REQUIRED_CHANNEL}", user_id=message.from_user.id).status
    if user_status not in ["member", "administrator", "creator"]:
        # If the user is not a member, prompt them to join
        markup = InlineKeyboardMarkup()
        join_button = InlineKeyboardButton("Join Channel", url=f"https://t.me/{REQUIRED_CHANNEL}")
        check_button = InlineKeyboardButton("Check", callback_data="check_membership")
        markup.add(join_button, check_button)

        bot.send_message(
            chat_id=message.chat.id,
            text="🚨 To use this bot, please join our channel.",
            reply_markup=markup
        )
        return  # Stop further processing if not joined

    # If the user is a member, proceed with the welcome message
    user: ClassVar[Union[str, int]] = User(message.from_user)
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    bot.reply_to(
        message=message,
        text=(
            f"⁀➴ Hello {user.pn}\n"
            "Welcome to Virtual Number Bot\n\n"
            "Send /help to get help message\n"
            "Send /number to get a virtual number"
        )
    )

    # Store user ID for broadcasting later
    if message.from_user.id not in user_ids:
        user_ids.append(message.from_user.id)
        total_users += 1  # Increment the total user count

        # Notify admin of the new user starting the bot
        notify_admin(message.from_user.id, message.from_user.username, total_users)

    # Handle referral link
    referrer_id = message.text.split('start=')[1] if 'start=' in message.text else None
    if referrer_id:
        referrer_id = int(referrer_id)
        if referrer_id not in user_referrals:
            user_referrals[referrer_id] = []
        user_referrals[referrer_id].append(message.from_user.id)

# Function to notify admin about new user
def notify_admin(user_id: int, username: str, total_users: int):
    """
    Sends a notification to the admin when a new user starts the bot.

    Parameters:
        user_id (int): The ID of the user.
        username (str): The username of the user.
        total_users (int): The total count of users.

    Returns:
        None
    """
    notification_message = (
        f"👤 New User Started the Bot:\n"
        f"User ID: {user_id}\n"
        f"Username: @{username}\n\n"
        f"Total Users Started: {total_users}"
    )
    bot.send_message(ADMIN_USER_ID, notification_message)

# Callback handler to check membership status
@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def callback_check_membership(call):
    user_status = bot.get_chat_member(chat_id=f"@{REQUIRED_CHANNEL}", user_id=call.from_user.id).status
    if user_status in ["member", "administrator", "creator"]:
        bot.answer_callback_query(call.id, "✅ Membership confirmed!")
        # Resend the /start command to proceed
        start_command_handler(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ You haven't joined the channel. Please join and try again.")

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
           "This bot is using api from onlinesim.io and fetches "
           "online and active number.\n"
           "All you need is sending few commands to bot and it will "
           "find a random number for you.\n\n══════════════\n"
           "★ To get new number you can simply send /number command "
           "or you can use inline button (Renew) to re-new your number.\n\n"
           "★ To get inbox messages use (inbox) inline button. this will show you "
           "last 5 messages.\n\n"
           "★ You can also check number's telegram profile using inline button "
           "(check phone number's profile)\n══════════════\n\n"
           "This is all you need to know about this bot!"
        )
    )

@bot.message_handler(commands=["broadcast"], func=lambda message: message.reply_to_message is not None)
def broadcast_message_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle the broadcast command for admins.
    Sends a message or media to all users.

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """
    # Check if the sender is an admin
    if message.from_user.id != ADMIN_USER_ID:  # Replace with actual admin ID
        bot.reply_to(message, "❌ You do not have permission to use this command.")
        return

    # Get the message to broadcast
    reply_message = message.reply_to_message

    # Send the message or file to all users
    try:
        for user_id in user_ids:
            if reply_message.text:
                bot.send_message(user_id, reply_message.text)
            elif reply_message.photo:
                bot.send_photo(user_id, reply_message.photo[-1].file_id, caption=reply_message.caption)
            elif reply_message.video:
                bot.send_video(user_id, reply_message.video.file_id, caption=reply_message.caption)
            elif reply_message.audio:
                bot.send_audio(user_id, reply_message.audio.file_id, caption=reply_message.caption)
            elif reply_message.document:
                bot.send_document(user_id, reply_message.document.file_id, caption=reply_message.caption)
            elif reply_message.voice:
                bot.send_voice(user_id, reply_message.voice.file_id, caption=reply_message.caption)
            elif reply_message.sticker:
                bot.send_sticker(user_id, reply_message.sticker.file_id)
            # Add more media types as needed
    except Exception as e:
        print(f"Failed to send message to user {user_id}: {e}")

    bot.reply_to(message, "✅ Broadcast message sent to all users.")

@bot.message_handler(commands=["invite"])
def invite_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Handle the /invite command to show the number of invited users and generate a referral link.
    """
    user_id = message.from_user.id

    # Get the number of users referred by this user
    ref_count = len(user_referrals.get(user_id, []))

    # Generate a referral link
    referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    # Send the response to the user
    bot.reply_to(
        message,
        f"👥 You have invited {ref_count} users using your referral link.\n"
        f"Your referral link: {referral_link}"
    )

# Start polling to handle messages



# Start polling to handle messages


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

    # Update prompt based on current status
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

#hi
@bot.message_handler(commands=["numberss"])
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

    # Update prompt based on current status
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





# Run the bot on polling mode
if __name__ == '__main__':
    try:
        bot.infinity_polling(
            skip_pending=True
        )
    except KeyboardInterrupt:
        raise SystemExit("\n\33[1;31m::\33[m Terminated by user")
