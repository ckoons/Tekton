from queue import Queue
from collections import defaultdict

# Global mailboxes - terminal_name -> mailbox_type -> Queue
mailboxes = defaultdict(lambda: {
    'prompt': Queue(maxsize=50),
    'new': Queue(maxsize=100),
    'keep': Queue(maxsize=50)
})

def put_message(terminal, mailbox_type, message):
    """Put message in mailbox. Drops oldest if full."""
    q = mailboxes[terminal][mailbox_type]
    if q.full():
        q.get()  # drop oldest
    q.put(message)

def get_messages(terminal, mailbox_type):
    """Get all messages without removing."""
    q = mailboxes[terminal][mailbox_type]
    items = []
    # Empty queue into list
    while not q.empty():
        items.append(q.get())
    # Put them back
    for item in items:
        q.put(item)
    return items

def pop_message(terminal, mailbox_type):
    """Get and remove one message."""
    q = mailboxes[terminal][mailbox_type]
    return q.get() if not q.empty() else None

def remove_terminal(terminal):
    """Terminal died, remove its mailboxes."""
    if terminal in mailboxes:
        del mailboxes[terminal]