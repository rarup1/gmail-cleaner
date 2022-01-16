import imaplib
import email
import datetime
import time
import sys


# Config
EMAIL = "<YOUR EMAIL>"
PW = "<YOUR PASSWORD>"
FOLDER_TO_DELETE_FROM = '"[Google Mail]/All Mail"'
TRASH_FOLDER = '"[Google Mail]/Trash"'
METHOD_TO_USE = "delete_unread_promotions_not_important"
FILTER_DATE = "2021-12-31"  # delete emails up to this date

# All search methods will append the FILTER_DATE above
METHOD_SEARCH = {
    "delete_unread_promotions_not_important": "category:promotions NOT is: important in:unread",
    "delete_unread_promotions": "category:promotions in:unread",
    "delete_read_promotions": "category:promotions in:read",
    "delete_unread": "in:unread",
    "delete_unread_not_important": "NOT is: important in:unread",
}


def get_unix_timestamp(date_char=FILTER_DATE):
    dto = datetime.datetime.strptime(date_char, "%Y-%m-%d")
    return round(time.mktime(dto.timetuple()))


def delete_emails(method=METHOD_TO_USE):
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(EMAIL, PW)
    # print(imap.list())
    # 1 set search criteria
    imap.select(FOLDER_TO_DELETE_FROM)
    gmail_search = f'"{METHOD_SEARCH[method]} before:{get_unix_timestamp()}"'
    typ, [msg_ids] = imap.search(None, "X-GM-RAW", gmail_search)
    id_list = [msg_ids.decode("utf-8")][0].split()
    num_emails = len(id_list)

    if query_yes_no(
        f"Do you wish to proceed with deletion of {num_emails}?"
    ):
        if num_emails == 0:
            print("No emails matching search criteria")
        else:
            print("Number of emails to be deleted:", num_emails)
            if isinstance(msg_ids, bytes):
                msg_ids = msg_ids.decode()

            # 2. Bulk move to trash folder
            msg_ids = ",".join(msg_ids.split(" "))
            print("Moving to Trash using X-GM_LABELS.")
            imap.store(msg_ids, "+X-GM-LABELS", "\\Trash")

            # 3. Empty trash
            print("Emptying Trash")
            imap.select(TRASH_FOLDER)
            imap.store("1:*", "+FLAGS", "\\Deleted")  # Flag all Trash as Deleted
            imap.expunge()
    else:
        print(f"Skipping deletion of {num_emails} emails")

    print("Completed and logging out")
    imap.close()
    imap.logout()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


# run program with defaults set in config
if __name__ == "__main__":
    delete_emails()
