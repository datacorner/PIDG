__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import xmltodict    # MIT License
from json import dumps,loads
import pandas as pd

# Inspired by https://github.com/FrankBGao/read_xes/tree/master
DATATYPES = ['string',  'int', 'date', 'float', 'boolean', 'id']

class xesFile:
    def __init__(self):
        self.__filename = ""
        self.__flatContent = pd.DataFrame()

    @property
    def filename(self):
        return self.__filename
    @filename.setter   
    def filename(self, value):
        self.__filename = value

    @property
    def flatContent(self):
        return self.__flatContent

    def __getEventDetails(self, event, id):
        """ returns all columns for one event (in a list)
        Args:
            event (_type_): event details
            id (_type_): trace id
        Returns:
            list: events details
        """
        one_event_attri = list(event.keys())
        one_event_dict = {}
        for i in DATATYPES:
            if i in one_event_attri:
                if type(event[i]) == list:
                    for j in event[i]:
                        one_event_dict[j['@key']] = j['@value']
                else:
                    one_event_dict[event[i]['@key']] = event[i]['@value']
        one_event_dict['concept-name-attr'] = id
        return one_event_dict

    def __ExtractOneTrace(self, trace_item):
        """ extract logs and attributes from 1 trace
        Args:
            trace_item (_type_): 1 trace (contains attrs + several logs)
        Returns:
            dict: trace attributes
            list: events
        """

        # Build atributes / trace
        attrs = list(trace_item.keys())
        attrs_dict = {}
        for i in DATATYPES:
            if i in attrs:
                if type(trace_item[i]) == list:
                    for j in trace_item[i]:
                        attrs_dict[j['@key']] = j['@value']
                else:
                    attrs_dict[trace_item[i]['@key']] = trace_item[i]['@value']
        # build events / trace
        events = []
        if type(trace_item['event']) == dict:
            trace_item['event'] = [trace_item['event']]

        for i in trace_item['event']:
            inter_event = self.__getEventDetails(i, attrs_dict['concept:name'])
            events.append(inter_event)
        return attrs_dict, events

    def __extractAll(self, xml):
        """ This functions reads the XES file and extract all the events and attributes
        Args:
            xml (str): XML flow (XES)
        Returns:
            list: event list
            list: attributes
        """
        traces = loads(dumps(xmltodict.parse(xml)))['log']['trace']
        attributes_list = []
        event_list = []
        # reads the traces tags one by one and get all the events & attrs
        for trace in traces:
            trace_item = self.__ExtractOneTrace(trace)
            attributes_list.append(trace_item[0]) # Attributes
            event_list = event_list + trace_item[1] # Event details
        return event_list, attributes_list
    
    def getEvents(self) -> bool:
        """ Returns all the XES events in a DataFrame format

        Args:
            xesfilename (str): XES filename

        Returns:
            bool: events
        """
        try:
            if (self.__filename == ""):
                raise Exception ("No XES file specified.")
            xmldata = open(self.__filename, mode='r').read()
            events, attributes = self.__extractAll(xmldata)
            self.__flatContent = pd.DataFrame(events)
            return True
        
        except Exception as e:
            print("xesFile.getEvents() Error: " + str(e))
            return False
