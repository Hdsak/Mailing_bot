import smtplib
from datetime import datetime


def finishing():
    while 1:
        print("Delivery finished, do you want to continue? [Yes/No] ")
        x = input().lower()
        if x == 'no':
            print("Auf wiedersehen")
            exit()
        elif x == 'yes':
            break
        else:
            print("Cant recognize what do you type")


def bot_settings():
    while 1:
        print("Input store name (type help for available stores) : ", end='')
        x = input()
        if x.lower() == 'agrees':
            store_name = 'agrees'
            break
        elif x.lower() == 'help':
            print("Available stores : Agrees")
    with open('accounts/account_{}.txt'.format(store_name), 'r') as account_file:
        attr_for_bot = ['email', 'password', 'host', 'port']
        bot_settings_dict = {attr_for_bot[i]: account_file.readline().strip() for i in range(4)}
        bot_settings_dict['store'] = store_name
        return bot_settings_dict


def get_clients(store_name):
    with open('recipients/recipients_{}.txt'.format(store_name), 'r') as recipients:
        return map(str.strip, recipients.readlines())


def email_content_former(store_name):
    with open('mails/letter_{}.html'.format(store_name), 'r',encoding='utf-8') as html_mail:
        mail = html_mail.read()
    return mail


def logs(recipient, store, code='', error_message=''):
    if not code:
        with open('logs/{0}_logs/log_{0}.txt'.format(store), 'a') as log:
            log.write("Delivery to {}, Time  {}\n"
                      .format(recipient, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    if code in [451, 471, 541, 551, 554]:
        with open('logs/{0}_logs/spam_error_log_{0}.txt'.format(store), 'a') as log:
            log.write("Spam error with recipient {}\nError code {}\nError message {}\nTime error {}"
                      .format(recipient, code, error_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    elif code == 250:
        with open('logs/{0}_logs/ok_log_{0}.txt'.format(store), 'a') as log:
            log.writelines("Message delivered to recipient {}, Time delivery {}\n"
                           .format(recipient, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    elif code:
        with open('logs/{0}_logs/error_log_{0}.txt'.format(store), 'a') as log:
            log.write("Error with recipient {}\nError code {}\nError message {}\n Time error {}"
                      .format(recipient, code, error_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def get_subject(store):
    with open('mails/mailing_{}.txt'.format(store), 'r', encoding='utf-8') as subject:
        return subject.read()


class Email_bot:
    def __init__(self):
        self.settings = bot_settings()
        self.server = smtplib.SMTP(host=self.settings['host'], port=self.settings['port'])
        self.email_content = email_content_former(self.settings['store'])
        self.recipients = get_clients(self.settings['store'])
        self.settings['subject'] = get_subject(self.settings['store'])
        self.headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Content-Disposition': 'inline',
            'Content-Transfer-Encoding': '8bit',
            'From': self.settings['email'],
            'Date': datetime.now().strftime('%a, %d %b %Y  %H:%M:%S %Z'),
            'X-Mailer': 'python',
            'Subject': self.settings['subject']
        }
        self.server.starttls()
        self.server.login(self.headers['From'], self.settings['password'])

    def message_sender(self, recipient):
        self.headers['To'] = recipient
        msg = ''
        for key, value in self.headers.items():
            msg += "%s: %s\n" % (key, value)

        # add contents
        msg += "\n%s\n" % self.email_content
        try:
            self.server.sendmail(self.headers['From'], self.headers['To'], msg.encode('utf-8'))
        except smtplib.SMTPResponseException as e:
            error_code = e.smtp_code
            error_message = e.smtp_error
            logs(self.headers['To'], self.settings['store'], error_code, error_message)
        else:
            logs(recipient, self.settings['store'], 250)
        logs(recipient, self.settings['store'])

    def start_spamming(self):
        for recipient in self.recipients:
            self.message_sender(recipient)
        self.server.quit()


def start():
    print("Hi that is email spamming bot")
    while 1:
        bot = Email_bot()
        print("Start logging...")
        bot.start_spamming()
        print("Logging finished")
        finishing()


if __name__ == "__main__":
    start()
