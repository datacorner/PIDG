SELECT logId, 
LOG.sessionnumber AS SessionID, 
stageName, 
result,
LOG.startdatetime AS resourceStartTime, 
BPAResource.name AS ResourceName,
actionname, 
stageType, 
pagename, 
attributexml,
IIF(processname IS NULL, 'VBO', 'PROC') as OBJECT_TYPE, 
IIF(processname IS NULL, objectname, processname) as OBJECT_NAME
FROM $tablelog AS LOG, BPASession, BPAResource
WHERE LOG.sessionnumber IN 
(SELECT distinct sessionnumber  
            FROM $tablelog 
		    WHERE processname = '$processname'
            AND $delta)
AND LOG.sessionnumber = BPASession.sessionnumber
AND BPAResource.resourceid = BPASession.runningresourceid
AND stagetype NOT IN($stagetypefilters)
AND $onlybpprocess