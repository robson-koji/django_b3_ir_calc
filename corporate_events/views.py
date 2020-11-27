from django.shortcuts import render
from .models import CorporateEvent
from collections import defaultdict

class CorporateEventView():
    dict_conversion_events = {}
    dict_deconversion_events = {}

    def __init__(self):
        self.dict_ce = defaultdict(list)
        self.corporate_events = CorporateEvent.objects.all()
        conversion_events = CorporateEvent.objects.filter(asset_code_new__isnull=False).values_list('asset_code_old', 'asset_code_new')
        self.dict_conversion_events = {ce[0]:ce[1] for ce in conversion_events}
        self.dict_deconversion_events = {ce[1]:ce[0] for ce in conversion_events}

        for ce in self.corporate_events:
            self.dict_ce[ce.date_ex].append( {'stock': str(ce.asset), 'event': ce.event,
                                'date_ex':  ce.date_ex,'group_valid': ce.group_valid,
                                'operator': ce.operator,
                                'qtt_operation': ce.qtt_operation,
                                'asset_code_old': ce.asset_code_old,
                                'asset_code_new': ce.asset_code_new})

    def check_event(self, line_dt):
        list_of_events = []
        for date_event in self.dict_ce:
            # Apply event only after the event date.
            # Checks against all trading data, or today.
            if date_event <= line_dt:
                list_of_events.append([self.dict_ce[date_event], date_event, len(self.dict_ce.keys())])
                #return (self.dict_ce[date_event], date_event, len(self.dict_ce.keys()))
        return list_of_events
        # return [(None, None, None)]

    def delete_event(self, event_date):
        try:
            del self.dict_ce[event_date]
        except:
            import pdb; pdb.set_trace()
