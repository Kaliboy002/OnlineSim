import telebot
from telebot import types
import json

# Initialize bot with token
bot = telebot.TeleBot("YOUR_BOT_TOKEN")

# Admin ID (replace with your actual admin ID)
ADMIN_ID = 123456789  # Replace with your actual admin ID

# Store users and blocked users in memory (you can replace this with a database for persistence)
user_ids = set()  # Set to store user IDs who have started the bot
blocked_users = set()  # Set to store user IDs who have blocked the bot
joined_channels = set()  # Set to store user IDs who have joined required channels

# Required channels to check
CHANNELS = ["@your_channel_1", "@your_channel_2"]  # Replace with your channels

# Helper function to check if the user has joined required channels
def has_joined_channels(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator"]:
                return False  # User has not joined or is not a member
        except Exception as e:
            print(f"Error checking membership for {user_id}: {e}")
            return False  # Return False if there's any error
    return True  # User has joined all required channels

@bot.message_handler(commands=["start", "restart"])
def start_command_handler(message):
    """
    Function to handle /start command and show a welcome message
    """
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"

    # Check if the user is already in user_ids
    if user_id not in user_ids:
        user_ids.add(user_id)
        # Notify admin about the new user
        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🆕 New User Started the Bot:\nUsername: @{username}\nUser ID: {user_id}\nTotal Users: {len(user_ids)}"
        )
    
    # Create inline keyboard with buttons to check channels and get number
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("Channel 1", url="https://t.me/your_channel_1"),
        types.InlineKeyboardButton("Channel 2", url="https://t.me/your_channel_2")
    )
    keyboard.add(types.InlineKeyboardButton("Check", callback_data="check_number"))

    # Send a welcome message
    bot.send_message(
        chat_id=message.chat.id,
        text=f"⁀➴ Hello @{username}\nWelcome to Virtual Number Bot\nPlease join our channels first and then click 'Check' to proceed.",
        reply_markup=keyboard
    )

@bot.message_handler(commands=["broadcast"])
def broadcast_command_handler(message):
    """
    Function to handle /broadcast command for the admin.
    """
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        broadcast_count = 0
        # Broadcast the message or media to all users
        for user_id in user_ids:
            try:
                if user_id in blocked_users:
                    continue  # Skip blocked users

                # Send the message or media depending on the type of the reply
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
                broadcast_count += 1
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
        
        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ Broadcast sent to {broadcast_count} users successfully."
        )
    else:
        bot.reply_to(message, "⚠️ Please reply to a message with /broadcast to send it to all users.")

@bot.message_handler(commands=["statistics"])
def statistics_command_handler(message):
    """
    Function to handle /statistics command for the admin.
    """
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"📊 Total Users Started the Bot: {len(user_ids)}\n"
                f"🚫 Total Blocked Users: {len(blocked_users)}"
            )
        )
    else:
        bot.reply_to(message, "⚠️ You do not have permission to use this command.")

@bot.callback_query_handler(func=lambda call: call.data == "check_number")
def check_number_callback(call):
    """
    Function to check if the user has joined the channels before proceeding.
    """
    user_id = call.from_user.id

    if user_id not in joined_channels:
        if not has_joined_channels(user_id):
            bot.answer_callback_query(call.id, text="Please join the channels first and then click 'Check'.")
            bot.send_message(chat_id=user_id, text="⚠️ You must join the required channels to proceed.")
            return  # Stop further processing if the user hasn't joined the channels

        # Mark the user as joined the channels
        joined_channels.add(user_id)
        bot.answer_callback_query(call.id, text="You have successfully joined the channels! Now you can proceed.")
        bot.send_message(chat_id=user_id, text="✅ You have joined the channels! You can now proceed with the bot.")
    else:
        bot.send_message(chat_id=user_id, text="✅ You have already joined the channels!")

@bot.message_handler(commands=["help"])
def help_command_handler(message):
    """
    Function to provide help information to users.
    """
    bot.send_message(
        chat_id=message.chat.id,
        text=(
            "Welcome to the Virtual Number Bot!\n\n"
            "To get started, use the /start command. Make sure to join the channels first.\n"
            "Once you've joined, click the 'Check' button to proceed with getting your virtual number."
        )
    )

# Start polling
bot.polling()














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


# Run the bot on polling mode
if __name__ == '__main__':
    try:
        bot.infinity_polling(
            skip_pending=True
        )
    except KeyboardInterrupt:
        raise SystemExit("\n\33[1;31m::\33[m Terminated by user")
