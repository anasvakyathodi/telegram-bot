import os,requests,time
from datetime import date
from dotenv import load_dotenv

# get env variables
load_dotenv('./.env')
token = os.getenv('TOKEN')
endpoint = os.getenv('ENDPOINT')

#  telegram bot class
class TelegramBot:
    # variable initialization
    def __init__(self,token,endpoint):
        self.token = token
        self.endpoint = endpoint
        self.last_message = None
        self.time_table = {
            'Mon':['Distributed Databases','Research Methodology & IPR','Advanced Computer Architecture','Advanced Algorithm','English for RPW','Intelligent System','Library','Library'],
            'Tue':['Advanced Computer Architecture','Distributed Databases','Research Methodology & IPR','Advanced Algorithm','English for RPW','Intelligent System','Distributed Databases Lab'],
            'Wed':['Intelligent System','Advanced Algorithm','Research Methodology & IPR','Distributed Databases','English for RPW','Library','Distributed Databases Lab'],
            'Thu':['Advanced Computer Architecture','Library','Research Methodology & IPR','Advanced Algorithm','English for RPW','Library'],
            'Fri':['Library','Advanced Computer Architecture','Distributed Databases','Intelligent System','Advanced Algorithm Lab'],
            'Sat':['Library'],
            'Sun':['Holiday']
        }

    # get last message 
    def get_last_message(self):
        url = self.endpoint + 'bot' + self.token + '/getUpdates'
        res = requests.get(url)
        if len(res.json()['result'])>0:
            self.last_message = dict(res.json()['result'][-1])
        return

    # reply dictionary
    def message_reply(self,msg,usr):
        switch={
        'hi':'Hello {}'.format(usr),
        'hello':'Hi {}'.format(usr),
        'how are you':'Iam good, What about you?',
        'iam good':'Great',
        'good':'Great',
        '/start':'How Can I Help You?',
        'sing a song for me':'Oops!! May be later!',
        'good morning':'Good Morning',
        'good afternoon':'Good Afternoon',
        'good night':'Good Night',
        'bye':'See You',
        '/today':'today',
        '/yesterday':'yesterday',
        '/this_week':'this_week',
        '/this_month':'this_month',
        '/this_year':'this_year',
        '/time_table':'time_table'
        }
        res = switch.get(msg.lower(),"Sorry I didn't get it!")
        return res

    # send message
    def send_message(self,user_id,message):
        url = self.endpoint + 'bot' + self.token + '/sendMessage'
        payload = {
            'chat_id':user_id,
            'text':message,
            'parse_mode':'HTML'
        }
        requests.post(url,payload)
        return

    # bot actions
    def bot_actions(self):
        self.get_last_message()
        last_update_id = self.last_message['update_id']
        time.sleep(1)
        while True:
            self.get_last_message()
            curr_update_id = self.last_message['update_id']
            if self.last_message != None:
                if last_update_id != curr_update_id:
                    user_text = self.last_message['message']['text']
                    user_name = self.last_message['message']['from']['first_name']
                    user_id = self.last_message['message']['from']['id']
                    reply = self.message_reply(user_text,user_name)
                    if(reply in ['all','today','yesterday','this_week','this_month','this_year']):
                        data = requests.request('GET','https://anz-academy-server.herokuapp.com/notifications')
                        data = data.json()['data'][::-1]
                        for dt in data:       
                            msg = """<b><i>{date}</i></b>
                            <b>{message}</b>
                            Link: <a href="{link}">Click here</a>""".format(date=dt['date'],message=dt['message'],link=dt['link'])
                            given_date = time.strptime(dt['date'],"%d %B, %Y")
                            today = date.today()
                            diff = today - date(given_date.tm_year,given_date.tm_mon,given_date.tm_mday)
                            if reply == 'today' and diff.days == 0:
                                self.send_message(user_id,msg)
                            elif reply == 'yesterday' and diff.days == 1:
                                self.send_message(user_id,msg)
                            elif reply == 'this_week' and diff.days <= 7:
                                self.send_message(user_id,msg)
                            elif reply == 'this_month' and diff.days <= 30:
                                self.send_message(user_id,msg)
                            elif reply == 'this_year' and diff.days <= 365:
                                self.send_message(user_id,msg)   
                            time.sleep(1)

                        print('{} : {}'.format(user_name,user_text))
                        print('{} : {}'.format('bot','data sent!'))
                        last_update_id += 1                                          
                    
                    elif reply == 'time_table':
                        today = date.today()
                        today = today.weekday()
                        days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
                        msg = """<b>Today's Periods</b>

"""
                        count = 1
                        today_schedules = self.time_table[days[today]]
                        for sub in today_schedules:
                            msg += """{}- {}
""".format(count,sub)
                            count += 1
                        self.send_message(user_id,msg)
                        last_update_id += 1
                        print('{} : {}'.format(user_name,user_text))
                        print('{} : {}'.format('bot','timetable sent!'))

                    else:
                        self.send_message(user_id,reply)
                        last_update_id += 1
                        print('{} : {}'.format(user_name,user_text))
                        print('{} : {}'.format('bot',reply))
            else:
                print('No Message Here')
            time.sleep(1)
    
# telegram instance
tg_bot = TelegramBot(token,endpoint)
tg_bot.bot_actions()