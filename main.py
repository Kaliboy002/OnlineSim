#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Virtual Number bot for Telegram
# Sends random virtual numbers to user
# Service: OnlineSim.io
# SourceCode (https://github.com/Kourva/OnlineSimBot)

import json
import random
import time
from typing import ClassVar, NoReturn, Any, Union
import telebot
from src import utils
from src.utils import User

# Initialize the bot token
bot: ClassVar[Any] = telebot.TeleBot(utils.get_token())
print(f"\33[1;36m::\33[m Bot is running with ID: {bot.get_me().id}")

# Required channel usernames
CHANNELS = ["@SHMMHS1", "@SHMMHS1"]

def is_user_member(user_id: int) -> bool:
    """
    Checks if the user is a member of all required channels.
    """
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            print(f"Error checking membership for channel {channel}: {e}")
            return False
    return True

@bot.message_handler(commands=["start", "restart"])
def start_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle start and restart commands in bot
    Prompts the user to join mandatory channels if not joined.
    """
    user_id = message.from_user.id

    # Check if the user has joined all required channels
    if is_user_member(user_id):
        # User has joined, send the /number command directly
        number_command_handler(message)
    else:
        # User has not joined, prompt them to join channels
        join_buttons = [
            [telebot.types.InlineKeyboardButton(text="Join Channel 1", url=f"https://t.me/{CHANNELS[0][1:]}")],
            [telebot.types.InlineKeyboardButton(text="Join Channel 2", url=f"https://t.me/{CHANNELS[1][1:]}")],
            [telebot.types.InlineKeyboardButton(text="Check Membership", callback_data="check_membership")]
        ]
        markup = telebot.types.InlineKeyboardMarkup(join_buttons)
        bot.send_message(
            chat_id=user_id,
            text="To use this bot, please join all required channels. After joining, click **Check Membership**.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def callback_check_membership(call: ClassVar[Any]) -> NoReturn:
    """
    Checks if the user has joined required channels when they click "Check Membership".
    """
    user_id = call.from_user.id

    if is_user_member(user_id):
        # User has joined all channels, execute the /number command
        bot.answer_callback_query(callback_query_id=call.id, text="Membership verified successfully!")
        number_command_handler(call.message)
    else:
        # User has not joined all channels, send prompt again
        bot.answer_callback_query(callback_query_id=call.id, text="Please join all channels to proceed.")
        start_command_handler(call.message)

@bot.message_handler(commands=["number"])
def number_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Handles the /number command by generating and sending a random virtual number.
    """
    user: ClassVar[Union[str, int]] = User(message.from_user)

    # Simulated example of sending a virtual number
    random_number = f"+1-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    bot.reply_to(
        message=message,
        text=f"Here is your virtual number: {random_number}"
    )

@bot.message_handler(commands=["help", "usage"])
def help_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle help commands in bot
    Shows help messages to users
    """
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    bot.reply_to(
        message=message,
        text=(
           "·ᴥ· Virtual Number Bot\n\n"
           "This bot is using API from onlinesim.io and fetches online and active numbers.\n"
           "Send /number to get a virtual number.\n"
           "For further assistance, please use the available commands."
        )
    )

# Run the bot




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


# Run the bot on polling mode
if __name__ == '__main__':
    try:
        bot.infinity_polling(
            skip_pending=True
        )
    except KeyboardInterrupt:
        raise SystemExit("\n\33[1;31m::\33[m Terminated by user")
