#!/usr/bin/env python3
import hashlib
from imbox import Imbox
import os
import getpass
import socket

class JunkEmailCollector:
    # Init object for connecting to email account and getting junk folder
    def __init__(self, imap_server, email_address, junk_folder):
        self.imap_server = imap_server
        self.email_address = email_address
        self.password = getpass.getpass('Please enter your email password:')

        # Specify the junk folder on the account, usually 'Junk' or 'Spam'
        self.junk_folder = junk_folder

        # Create directory to save junk email
        email_parts = email_address.split('@')
        save_folder = "%s_%s" % (email_parts[0], email_parts[1])

        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
        self.save_folder = save_folder

    # Get all unread junk messages from account
    def get_junk(self):
        try:
            with Imbox(self.imap_server,
                username = self.email_address,
                password = self.password,
                ssl=True,
                ssl_context=None,
                starttls=False) as imbox:

                # Get all folders
                status, folders_with_additional_info = imbox.folders()
                # Load unread junk messages
                unread_junk = imbox.messages(unread = True, folder = self.junk_folder)

                # Get sha256 of each raw message and save raw msg
                for uid, msg in unread_junk:
                    raw_msg = msg.raw_email.encode("utf-8")
                    sha256 = hashlib.sha256(raw_msg).hexdigest()

                    with open(self.save_folder + "/%s.eml" % sha256, "wb") as eml:
                        eml.write(raw_msg)

                    # Print message info
                    print('\n' + msg.date)
                    print(msg.sent_from)
                    print(msg.subject)
                    print(sha256)

                    # Mark the message as read
                    imbox.mark_seen(uid)
        except socket.gaierror as e:
            print(f'Error connecting: {e} \n\tCheck your creds or imap server.')
            return
