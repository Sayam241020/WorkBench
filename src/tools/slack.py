import pandas as pd
from langchain.tools import tool
import os

from src.data_generation.data_generation_utils import HARDCODED_CURRENT_TIME

# Ensure file exists or create a dummy one
SLACK_MESSAGES_PATH = "data/processed/slack_messages.csv"
if not os.path.exists(SLACK_MESSAGES_PATH):
    os.makedirs(os.path.dirname(SLACK_MESSAGES_PATH), exist_ok=True)
    df = pd.DataFrame(columns=["message_id", "channel", "user", "sender", "body", "sent_datetime"])
    df.to_csv(SLACK_MESSAGES_PATH, index=False)

SLACK_MESSAGES = pd.read_csv(SLACK_MESSAGES_PATH, dtype=str)

def reset_state():
    """
    Resets the Slack messages to the original state.
    """
    global SLACK_MESSAGES
    SLACK_MESSAGES = pd.read_csv(SLACK_MESSAGES_PATH, dtype=str)

@tool("slack.send_message", return_direct=False)
def send_message(channel=None, user=None, body=None):
    """
    Sends a message to a Slack channel or direct message to a user.

    Parameters
    ----------
    channel : str, optional
        Name of the channel (e.g. 'general')
    user : str, optional
        Name of the user (e.g. 'john')
    body : str
        The body of the message.
    """
    global SLACK_MESSAGES
    if not body:
        return "Message body not provided."
    if not channel and not user:
        return "Channel or user not provided."
    
    msg_id = "1" if SLACK_MESSAGES.empty else str(int(SLACK_MESSAGES["message_id"].max()) + 1)
    sent_datetime = HARDCODED_CURRENT_TIME.strftime("%Y-%m-%d %H:%M:%S")
    sender = "me"
    
    SLACK_MESSAGES.loc[len(SLACK_MESSAGES)] = [
        msg_id,
        channel if channel else "",
        user if user else "",
        sender,
        body,
        sent_datetime
    ]
    return "Message sent successfully."

@tool("slack.read_last_message", return_direct=False)
def read_last_message(channel=None, user=None):
    """
    Reads the last message from a channel or a direct message conversation.

    Parameters
    ----------
    channel : str, optional
        Name of the channel
    user : str, optional
        Name of the user
    """
    if not channel and not user:
        return "Channel or user not provided."
    
    if channel:
        msgs = SLACK_MESSAGES[SLACK_MESSAGES["channel"] == channel]
    else:
        msgs = SLACK_MESSAGES[(SLACK_MESSAGES["user"] == user) | (SLACK_MESSAGES["sender"] == user)]
    
    if len(msgs) == 0:
        return "No messages found."
    
    msgs = msgs.sort_values("sent_datetime", ascending=False)
    last_msg = msgs.iloc[0].to_dict()
    return {"sender": last_msg["sender"], "body": last_msg["body"], "sent_datetime": last_msg["sent_datetime"]}

@tool("slack.search_messages", return_direct=False)
def search_messages(query=""):
    """
    Searches for messages containing the given query string.

    Parameters
    ----------
    query : str
        The text to search for
    """
    query_words = query.lower().split()
    
    def filter_msgs(row):
        return all(word in str(row['body']).lower() for word in query_words)
    
    filtered = SLACK_MESSAGES.apply(filter_msgs, axis=1)
    results = SLACK_MESSAGES[filtered].sort_values("sent_datetime", ascending=False).to_dict(orient="records")
    
    if len(results):
        return results[:5]
    return "No messages found."
