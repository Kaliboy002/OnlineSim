## Standard library import
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
user_button_clicks: Dict[int, int] = {}  # {user_id: button_click_count}

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

        # Track referrals only if referrer_id is valid and not affecting other functionalities
        if referrer_id and referrer_id in user_ids:
            referral_data[referrer_id] = referral_data.get(referrer_id, 0) + 1
            bot.send_message(
                chat_id=referrer_id,
                text=(
                    f"🎉 You have referred a new user!\n"
                    f"👥 Total Referrals: {referral_data[referrer_id]}"
                )
            )

    # Generate and store the user's referral link
    invite_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    user_referrals[user_id] = invite_link

    # Create the channel join buttons
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Join Channel 1", url="https://t.me/your_channel_1"),
        types.InlineKeyboardButton("Join Channel 2", url="https://t.me/your_channel_2"),
        types.InlineKeyboardButton("🔐 Joined", callback_data="check_numb")
    )

    # Send welcome message with the referral link
    bot.send_message(
        chat_id=user_id,
        text=(
            "⚠️ To use this bot, you must join our Telegram channels.\n\n"
            "Here is your unique invite link:\n"
            f"`{invite_link}`\n\n"
            "Share this link with friends to earn rewards!\n\n"
            "Once you've joined the channels, click the 🔐 Joined button to confirm your membership."
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

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
        types.InlineKeyboardButton("Free number", callback_data="free_number"),
        types.InlineKeyboardButton("VIP number", callback_data="vip_number")
    )

    bot.send_photo(
        chat_id=user_id,
        photo=photo_url,
        caption=description,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "free_number")
def free_number_callback(call):
    """
    Sends free number options when 'Free number' button is clicked.
    """
    bot.send_message(
        chat_id=call.message.chat.id,
        text="🔓 Free numbers are now available! Enjoy using them."
    )

@bot.callback_query_handler(func=lambda call: call.data == "vip_number")
def vip_number_callback(call):
    """
    Sends a message for the VIP number option.
    """
    bot.send_message(
        chat_id=call.message.chat.id,
        text="⚡ VIP numbers are free for now! Use them without restrictions."
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("number_"))
def number_buttons_callback(call):
    """
    Handles the callback for when any of the number buttons is clicked.
    If user has enough invites, sends OTP code; otherwise, shows an error message.
    """
    user_id = call.message.chat.id
    total_invites = referral_data.get(user_id, 0)

    # Check if the user has enough invites
    if total_invites >= 2:
        otp_code = random.randint(10000, 99999)
        bot.send_message(
            chat_id=user_id,
            text=f"🎉 You unlocked the OTP!\n\nYour OTP code is: {otp_code}"
        )
    else:
        bot.send_message(
            chat_id=user_id,
            text="❌ You do not have enough invites to get the OTP. Please invite more users to unlock this feature."
        )



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

