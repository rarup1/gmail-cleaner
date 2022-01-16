import imaplib
import email
import datetime 
import time 

# Your configuration
EMAIL = "<ENTER GMAIL EMAIL>"
PW = "<ENTER GMAIL PASSWORD>" # will require an application password generated in gmail
FOLDER_TO_DELETE_FROM = '"[Google Mail]/All Mail"'
TRASH_FOLDER = '"[Google Mail]/Trash"'
METHOD_TO_USE = 'delete_unread_promotions_not_important'
DELETE = 'N' # set to 'Y' to perform deletion
FILTER_DATE = '2021-12-31' # filter emails up to this date

# Dictionary of search methods to pick from in METHOD_TO_USE
METHOD_SEARCH = {
    'delete_unread_promotions_not_important': 'category:promotions NOT is: important in:unread',
    'delete_unread_promotions': 'category:promotions in:unread',
    'delete_read_promotions': 'category:promotions in:read',
    'delete_unread': 'in:unread',
    'delete_unread_not_important': 'NOT is: important in:unread'
}

def get_unix_timestamp(date_char=FILTER_DATE):
    dto = datetime.datetime.strptime(date_char, '%Y-%m-%d')
    return round(time.mktime(dto.timetuple()))

def delete_emails(method=METHOD_TO_USE, delete_flag=DELETE):
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(EMAIL, PW)
    # print(imap.list())
    # 1 set search criteria
    imap.select(FOLDER_TO_DELETE_FROM)
    gmail_search = f'"{METHOD_SEARCH[method]} before:{get_unix_timestamp()}"'
    typ, [msg_ids] = imap.search(None, 'X-GM-RAW', gmail_search)
    id_list = [msg_ids.decode("utf-8")][0].split()

    if delete_flag == 'Y':
        if len(id_list) == 0:
            print("No emails matching search criteria")
        else:
            print("Number of emails to be deleted:", len(id_list))
            if isinstance(msg_ids, bytes):
                msg_ids = msg_ids.decode()

            # 2. Bulk move to trash folder
            msg_ids = ','.join(msg_ids.split(' '))
            print("Moving to Trash using X-GM_LABELS.")
            imap.store(msg_ids, '+X-GM-LABELS', '\\Trash')

            # 3. Empty trash
            print("Emptying Trash and expunge...")
            imap.select(TRASH_FOLDER)
            imap.store("1:*", '+FLAGS', '\\Deleted')  # Flag all Trash as Deleted
            imap.expunge()
    else:
        print(f"Skipping deletion of {len(id_list)} emails")

    print("Completed and logging out")
    imap.close()
    imap.logout()

# run program with defaults set in config
if __name__ == "__main__":
    delete_emails()
