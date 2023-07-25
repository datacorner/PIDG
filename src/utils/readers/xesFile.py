import xmltodict    # MIT License
from json import dumps,loads
import pandas as pd

# Inspired by https://github.com/FrankBGao/read_xes/tree/master
DATATYPES = ['string',  'int', 'date', 'float', 'boolean', 'id']

class xesFile:
    def __init__(self):
        pass

    def __getEventDetails(self, one_event, case_name,data_types):
        one_event_attri = list(one_event.keys())
        one_event_dict = {}
        for i in data_types:
            if i in one_event_attri:
                if type(one_event[i]) == list:
                    for j in one_event[i]:
                        one_event_dict[j['@key']] = j['@value']
                else:
                    one_event_dict[one_event[i]['@key']] = one_event[i]['@value']
        one_event_dict['concept-name-attr'] = case_name
        return one_event_dict

    def __ExtractOneTrace(self, one_trace,data_types):
        one_trace_attri = list(one_trace.keys())
        one_trace_attri_dict = {}
        for i in data_types:
            if i in one_trace_attri:
                if type(one_trace[i]) == list:
                    for j in one_trace[i]:
                        one_trace_attri_dict[j['@key']] = j['@value']
                else:
                    one_trace_attri_dict[one_trace[i]['@key']] = one_trace[i]['@value']
        # for event seq
        one_trace_events = []
        if type(one_trace['event']) == dict:
            one_trace['event'] = [one_trace['event']]

        for i in one_trace['event']:
            inter_event = self.__getEventDetails(i, one_trace_attri_dict['concept:name'],data_types)
            one_trace_events.append(inter_event)
        return one_trace_attri_dict,one_trace_events

    def __extractAll(self, xml_string):
        """ This functions reads the XES file and extract all the events and attributes
        Args:
            xml_string (str): XML flow (XES)
        Returns:
            list: event list
            list: attributes
        """
        traces = loads(dumps(xmltodict.parse(xml_string)))['log']['trace']
        attributes_list = []
        event_list = []
        # reads the traces tags one by one and get all the events & attrs
        for trace in traces:
            trace_item = self.__ExtractOneTrace(trace, DATATYPES)
            attributes_list.append(trace_item[0]) # Attributes
            event_list = event_list + trace_item[1] # Event details
        return event_list, attributes_list
    
    def getEvents(self, xesfilename):
        """ Returns all the XES events in a DataFrame format

        Args:
            xesfilename (str): XES filename

        Returns:
            pd.DataFrame: events
        """
        xmldata = open(xesfilename, mode='r').read()
        events, attributes = self.__extractAll(xmldata)
        return pd.DataFrame(events)