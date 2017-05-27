# Event types:

# Tick - Generated by Data Handler and added to queue

# Signal - Generated by strategy module. Fed through to portfolio module which calls risk.

# Order - Generated by portfolio & handled by execution module

# Fill - Generated by execution module & handled by portfolio


from datetime import datetime
import collections


class event:
    
    def __init__(self, event_type):
        self.type = event_type
        self.time = datetime.utcnow()
        


class event_queue:
    
    def __init__(self):
        self.queue = collections.deque()
        
    def add_to_queue(self, event):
        self.queue.append(event)
    
    def handle_next(self):
        if self.queue:
            event = self.queue.popleft()
            if event == None:
                pass
            elif event.type == 'tick':
                #Call strategy
                print('Tick Event Popped')
            elif event.type == 'signal':
                #Call risk
                print('Signal Event Popped')
            elif event.type == 'trade':
                #Call portfolio
                print('Trade Event Popped')
            elif event.type == 'order':
                #Call execution
                print('Order Event Popped')
            elif event.type == 'fill':
                #Wait in execution function until response received
                #Call portfolio
                print('Fill Event Popped')
        else:
            print('Queue is empty')

