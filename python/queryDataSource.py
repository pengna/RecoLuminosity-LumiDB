import array,coral
from RecoLuminosity.LumiDB import CommonUtil,nameDealer

def hltFromOldLumi(session,runnumber):
    '''
    select count(distinct pathname) from hlt where runnum=:runnum
    select cmslsnum,pathname,inputcount,acceptcount,prescale from hlt where runnum=:runnum order by cmslsnum,pathname
    [pathnames,databuffer]
    databuffer: {cmslsnum:[inputcountBlob,acceptcountBlob,prescaleBlob]}
    '''
    try:
        databuffer={}
        session.transaction().start(True)
        lumischema=session.nominalSchema()
        npath=0
        qHandle=lumischema.newQuery()
        qHandle.addToTableList( nameDealer.hltTableName() )
        qHandle.addToOutputList('COUNT(DISTINCT PATHNAME)','npath')
        qCondition=coral.AttributeList()
        qCondition.extend('runnum','unsigned int')
        qCondition['runnum'].setData(int(runnumber))
        qResult=coral.AttributeList()
        qResult.extend('npath','unsigned int')
        qHandle.defineOutput(qResult)
        qHandle.setCondition('RUNNUM=:runnum',qCondition)
        cursor=qHandle.execute()
        while cursor.next():
            npath=cursor.currentRow()['npath'].data()
        del qHandle
        #print 'npath ',npath

        qHandle=lumischema.newQuery()
        qHandle.addToTableList( nameDealer.hltTableName() )
        qHandle.addToOutputList('CMSLSNUM','cmslsnum')
        qHandle.addToOutputList('PATHNAME','pathname')
        qHandle.addToOutputList('INPUTCOUNT','inputcount')
        qHandle.addToOutputList('ACCEPTCOUNT','acceptcount')
        qHandle.addToOutputList('PRESCALE','prescale')
        qCondition=coral.AttributeList()
        qCondition.extend('runnum','unsigned int')
        qCondition['runnum'].setData(int(runnumber))
        qResult=coral.AttributeList()
        qResult.extend('cmslsnum','unsigned int')
        qResult.extend('pathname','string')
        qResult.extend('inputcount','unsigned int')
        qResult.extend('acceptcount','unsigned int')
        qResult.extend('prescale','unsigned int')
        qHandle.defineOutput(qResult)
        qHandle.setCondition('RUNNUM=:runnum',qCondition)
        qHandle.addToOrderList('cmslsnum')
        qHandle.addToOrderList('pathname')
        cursor=qHandle.execute()
        pathnameList=[]
        inputcountArray=array.array('l')
        acceptcountArray=array.array('l')
        prescaleArray=array.array('l')
        ipath=0
        pathnames=''
        while cursor.next():
            cmslsnum=cursor.currentRow()['cmslsnum'].data()
            pathname=cursor.currentRow()['pathname'].data()
            ipath+=1
            inputcount=cursor.currentRow()['inputcount'].data()
            acceptcount=cursor.currentRow()['acceptcount'].data()
            prescale=cursor.currentRow()['prescale'].data()
            pathnameList.append(pathname)
            inputcountArray.append(inputcount)
            acceptcountArray.append(acceptcount)
            prescaleArray.append(prescale)
            if ipath==npath:
                if cmslsnum==1:
                    pathnames=','.join(pathnameList)
                inputcountBlob=CommonUtil.packArraytoBlob(inputcountArray)
                acceptcountBlob=CommonUtil.packArraytoBlob(acceptcountArray)
                prescaleBlob=CommonUtil.packArraytoBlob(prescaleArray)
                databuffer[cmslsnum]=[inputcountBlob,acceptcountBlob,prescaleBlob]
                pathnameList=[]
                inputcountArray=array.array('l')
                acceptcountArray=array.array('l')
                prescaleArray=array.array('l')
                ipath=0
        del qHandle
        session.transaction().commit()
        #print 'pathnames ',pathnames
        return [pathnames,databuffer]
    except :
        raise 

def trgFromOldLumi(session,runnumber):
    '''
    select bitnum,bitname from trg where runnum=:runnumber and cmslsnum=1 order by bitnum
    select cmslsnum,deadtime,trgcount,prescale from trg where bitnum=:bitnum and runnum=:runnumber 
    input: runnumber
    output: [bitnames,{cmslsnum,[deadtime,bitzerocount,bitzerpoprescale,trgcountBlob,trgprescaleBlob]}]
    '''
    session.transaction().start(True)
    lumischema=session.nominalSchema()
    qHandle=lumischema.newQuery()
    try:
        qHandle=lumischema.newQuery()
        qHandle.addToTableList(nameDealer.trgTableName())
        qHandle.addToOutputList('BITNUM','bitnum')
        qHandle.addToOutputList('BITNAME','bitname')
        qCondition=coral.AttributeList()
        qCondition.extend('runnum','unsigned int')
        qCondition['runnum'].setData(int(runnumber))
        qCondition.extend('cmslsnum','unsigned int')
        qCondition['cmslsnum'].setData(int(1))
        qResult=coral.AttributeList()
        qResult.extend('bitnum','unsigned int')
        qResult.extend('bitname','string')
        qHandle.defineOutput(qResult)
        qHandle.setCondition('RUNNUM=:runnum AND CMSLSNUM=:cmslsnum',qCondition)
        qHandle.addToOrderList('BITNUM')
        cursor=qHandle.execute()
        bitnums=[]
        bitnameList=[]
        while cursor.next():
            bitnum=cursor.currentRow()['bitnum'].data()
            bitname=cursor.currentRow()['bitname'].data()
            bitnums.append(bitnum)
            bitnameList.append(bitname)
        del qHandle
        bitnames=','.join(bitnameList)
        databuffer={}
        nbits=len(bitnums)
        qHandle=lumischema.newQuery()
        qHandle.addToTableList(nameDealer.trgTableName())
        qHandle.addToOutputList('CMSLSNUM','cmslsnum')
        qHandle.addToOutputList('BITNUM','bitnum')
        qHandle.addToOutputList('DEADTIME','deadtime')
        qHandle.addToOutputList('TRGCOUNT','trgcount')
        qHandle.addToOutputList('PRESCALE','prescale')
        qCondition=coral.AttributeList()
        qCondition.extend('runnum','unsigned int')
        qCondition['runnum'].setData(int(runnumber))
        qResult=coral.AttributeList()
        qResult.extend('cmslsnum','unsigned int')
        qResult.extend('bitnum','unsigned int')
        qResult.extend('deadtime','unsigned long long')
        qResult.extend('trgcount','unsigned int')
        qResult.extend('prescale','unsigned int')
        qHandle.defineOutput(qResult)
        qHandle.setCondition('RUNNUM=:runnum',qCondition)
        qHandle.addToOrderList('CMSLSNUM')
        qHandle.addToOrderList('BITNUM')
        cursor=qHandle.execute()
        trgcountArray=array.array('l')
        prescaleArray=array.array('l')
        while cursor.next():
            cmslsnum=cursor.currentRow()['cmslsnum'].data()
            bitnum=cursor.currentRow()['bitnum'].data()
            deadtime=cursor.currentRow()['deadtime'].data()
            trgcount=cursor.currentRow()['trgcount'].data()
            prescale=cursor.currentRow()['prescale'].data()
            if not databuffer.has_key(cmslsnum):
                databuffer[cmslsnum]=[]
                databuffer[cmslsnum].append(deadtime)
            if bitnum==0:
                databuffer[cmslsnum].append(trgcount)
                databuffer[cmslsnum].append(prescale)
            trgcountArray.append(trgcount)
            prescaleArray.append(prescale)
            if bitnum==nbits-1:
                trgcountBlob=CommonUtil.packArraytoBlob(trgcountArray)
                prescaleBlob=CommonUtil.packArraytoBlob(prescaleArray)
                databuffer[cmslsnum].append(trgcountBlob)
                databuffer[cmslsnum].append(prescaleBlob)
                trgcountArray=array.array('l')
                prescaleArray=array.array('l')
        del qHandle            
        session.transaction().commit()
        return [bitnames,databuffer]
    except:
        del qHandle
        raise

def trgFromWBM(session,runnumber):
    '''
    '''
    pass

def trgFromGT(session,runnumber):
    '''
    select counts,lsnr,algobit from cms_gt_mon.gt_mon_trig_algo_view where runnr=:runnumber order by lsnr,algobit
    select counts,lsnr,techbit from cms_gt_mon.gt_mon_trig_tech_view where runnr=:runnumber order by lsnr,techbit
    select counts,lsnr from cms_gt_mon.gt_mon_trig_dead_view where runnr=:runnumber and deadcounter=:countername order by lsnr
    select algo_index,alias from cms_gt.gt_run_algo_view where runnumber=:runnumber order by algo_index
    select techtrig_index,name from cms_gt.gt_run_tech_view where runnumber=:runnumber order by techtrig_index
    select prescale_factor_algo_000,prescale_factor_algo_001..._127 from cms_gt.gt_run_presc_algo_view where runnr=:runnumber and prescale_index=0;
    select prescale_factor_tt_000,prescale_factor_tt_001..._63 from cms_gt.gt_run_presc_tech_view where runnr=:runnumber and prescale_index=0;
    '''
    pass

def trgFromOldGT(session,runnumber):
    '''
    input: runnumber
    if complementalOnly is True:
       select deadfrac from 
    else:
    output: [bitnameclob,{cmslsnum:[deadtime,bitzerocount,bitzeroprescale,trgcountBlob,trgprescaleBlob]}]
    select counts,lsnr,algobit from cms_gt_mon.gt_mon_trig_algo_view where runnr=:runnumber order by lsnr,algobit
    select counts,lsnr,techbit from cms_gt_mon.gt_mon_trig_tech_view where runnr=:runnumber order by lsnr,techbit
    select counts,lsnr from cms_gt_mon.gt_mon_trig_dead_view where runnr=:runnumber and deadcounter=:countername order by lsnr
    select algo_index,alias from cms_gt.gt_run_algo_view where runnumber=:runnumber order by algo_index
    select techtrig_index,name from cms_gt.gt_run_tech_view where runnumber=:runnumber order by techtrig_index
    select prescale_factor_algo_000,prescale_factor_algo_001..._127 from cms_gt.gt_run_presc_algo_view where runnr=:runnumber and prescale_index=0;
    select prescale_factor_tt_000,prescale_factor_tt_001..._63 from cms_gt.gt_run_presc_tech_view where runnr=:runnumber and prescale_index=0;
    '''
    pass
    #bitnames=''
    #databuffer={} #{cmslsnum:[deadtime,bitzerocount,bitzeroprescale,trgcountBlob,trgprescaleBlob]}
    #qHandle=schema.newQuery()
    #try:
        
    #except:
    #    del qHandle
    #    raise 

def hltFromRuninfoV2(session,runnumber):
    '''
    input:
    output: [datasource,pathnameclob,{cmslsnum:[inputcountBlob,acceptcountBlob,prescaleBlob]}]
    select count(distinct PATHNAME) as npath from HLT_SUPERVISOR_LUMISECTIONS_V2 where runnr=:runnumber and lsnumber=1;
    select l.pathname,l.lsnumber,l.l1pass,l.paccept,m.psvalue from hlt_supervisor_lumisections_v2 l,hlt_supervisor_scalar_map m where l.runnr=m.runnr and l.psindex=m.psindex and l.pathname=m.pathname and l.runnr=:runnumber order by l.lsnumber
    
    '''
    pass

def hltFromRuninfoV3(session,runnumber):
    '''
    input:
    output: [datasource,pathnameclob,{cmslsnum:[inputcountBlob,acceptcountBlob,prescaleBlob]}]
    select count(distinct PATHNAME) as npath from HLT_SUPERVISOR_LUMISECTIONS_V2 where runnr=:runnumber and lsnumber=1;
    select l.pathname,l.lsnumber,l.l1pass,l.paccept,m.psvalue from hlt_supervisor_lumisections_v2 l,hlt_supervisor_scalar_map m where l.runnr=m.runnr and l.psindex=m.psindex and l.pathname=m.pathname and l.runnr=:runnumber order by l.lsnumber
    
    '''
    pass

def hltconf(schema,hltkey):
    '''
    select paths.pathid,paths.name,stringparamvalues.value from stringparamvalues,paths,parameters,superidparameterassoc,modules,moduletemplates,pathmoduleassoc,configurationpathassoc,configurations where parameters.paramid=stringparamvalues.paramid and  superidparameterassoc.paramid=parameters.paramid and modules.superid=superidparameterassoc.superid and moduletemplates.superid=modules.templateid and pathmoduleassoc.moduleid=modules.superid and paths.pathid=pathmoduleassoc.pathid and configurationpathassoc.pathid=paths.pathid and configurations.configid=configurationpathassoc.configid and moduletemplates.name='HLTLevel1GTSeed' and parameters.name='L1SeedsLogicalExpression' and configurations.configid=1905; 

    '''
    pass

def runsummary(session,schemaname,runnumber,complementalOnly=False):
    '''
    x select string_value from cms_runinfo.runsession_parameter where runnumber=:runnumber and name='CMS.TRG:TSC_KEY';
    x select distinct(string_value) from cms_runinfo.runsession_parameter where runnumber=:runnumber and name='CMS.SCAL:AMODEtag'
    x select distinct(string_value),session_id from cms_runinfo.runsession_parameter where runnumber=:runnumber and name='CMS.SCAL:EGEV' order by SESSION_ID
    
    select string_value from cms_runinfo.runsession_parameter where runnumber=:runnumber and name='CMS.LVL0:SEQ_NAME'
    select string_value from cms_runinfo.runsession_parameter where runnumber=:runnumber and name='CMS.LVL0:HLT_KEY_DESCRIPTION';
    select string_value from cms_runinfo.runsession_parameter where runnumber=:runnumber and name='CMS.SCAL:FILLN' and rownum<=1;
    select time from cms_runinfo.runsession_parameter where runnumber=:runnumber and name='CMS.LVL0:START_TIME_T';
    select time from cms_runinfo.runsession_parameter where runnumber=:runnumber and name='CMS.LVL0:STOP_TIME_T';
    input:
    output:[l1key,amodetag,egev,hltkey,fillnum,sequence,starttime,stoptime]
    if complementalOnly:
       [l1key,amodetag,egev]
    '''
    runsessionparameterTable=''
    result=[]
    l1key=''
    amodetag=''
    egev=''
    hltkey=''
    fillnum=''
    sequence=''
    starttime=''
    stoptime=''
    try:
        session.transaction().start(True)
        runinfoschema=session.schema(schemaname)
        l1keyQuery=runinfoschema.newQuery()
        l1keyQuery.addToTableList('RUNSESSION_PARAMETER')
        l1keyOutput=coral.AttributeList()
        l1keyOutput.extend('l1key','string')
        l1keyCondition=coral.AttributeList()
        l1keyCondition.extend('name','string')
        l1keyCondition.extend('runnumber','unsigned int')
        l1keyCondition['name'].setData('CMS.TRG:TSC_KEY')
        l1keyCondition['runnumber'].setData(int(runnumber))
        l1keyQuery.addToOutputList('STRING_VALUE')
        l1keyQuery.setCondition('NAME=:name AND RUNNUMBER=:runnumber',l1keyCondition)
        l1keyQuery.defineOutput(l1keyOutput)
        cursor=l1keyQuery.execute()
        while cursor.next():
            l1key=cursor.currentRow()['l1key'].data()
        del l1keyQuery
        result.append(l1key)
        
        amodetagQuery=runinfoschema.newQuery()
        amodetagQuery.addToTableList('RUNSESSION_PARAMETER')
        amodetagOutput=coral.AttributeList()
        amodetagOutput.extend('amodetag','string')
        amodetagCondition=coral.AttributeList()
        amodetagCondition.extend('name','string')
        amodetagCondition.extend('runnumber','unsigned int')
        amodetagCondition['name'].setData('CMS.SCAL:AMODEtag')
        amodetagCondition['runnumber'].setData(int(runnumber))
        amodetagQuery.addToOutputList('distinct(STRING_VALUE)')
        amodetagQuery.setCondition('NAME=:name AND RUNNUMBER=:runnumber',amodetagCondition)
        amodetagQuery.limitReturnedRows(1)
        amodetagQuery.defineOutput(amodetagOutput)
        cursor=amodetagQuery.execute()
        while cursor.next():
            amodetag=cursor.currentRow()['amodetag'].data()
        del amodetagQuery
        result.append(amodetag)
        
        egevQuery=runinfoschema.newQuery()
        egevQuery.addToTableList('RUNSESSION_PARAMETER')
        egevOutput=coral.AttributeList()
        egevOutput.extend('egev','string')
        egevCondition=coral.AttributeList()
        egevCondition.extend('name','string')
        egevCondition.extend('runnumber','unsigned int')
        egevCondition['name'].setData('CMS.SCAL:EGEV')
        egevCondition['runnumber'].setData(int(runnumber))
        egevQuery.addToOutputList('distinct(STRING_VALUE)')
        egevQuery.addToOutputList('SESSION_ID')
        egevQuery.setCondition('NAME=:name AND RUNNUMBER=:runnumber',egevCondition)
        egevQuery.defineOutput(egevOutput)
        egevQuery.addToOrderList('SESSION_ID')
        cursor=egevQuery.execute()
        while cursor.next():
            egev=cursor.currentRow()['egev'].data()
        del egevQuery
        result.append(egev)
        
        if not complementalOnly:
            seqQuery=runinfoschema.newQuery()
            seqQuery.addToTableList('RUNSESSION_PARAMETER')
            seqOutput=coral.AttributeList()
            seqOutput.extend('seq','string')
            seqCondition=coral.AttributeList()
            seqCondition.extend('name','string')
            seqCondition.extend('runnumber','unsigned int')
            seqCondition['name'].setData('CMS.LVL0:SEQ_NAME')
            seqCondition['runnumber'].setData(int(runnumber))
            seqQuery.addToOutputList('STRING_VALUE')
            seqQuery.setCondition('NAME=:name AND RUNNUMBER=:runnumber',seqCondition)
            seqQuery.defineOutput(seqOutput)
            cursor=seqQuery.execute()
            while cursor.next():
                sequence=cursor.currentRow()['seq'].data()
            del seqQuery
            result.append(sequence)

            hltkeyQuery=runinfoschema.newQuery()
            hltkeyQuery.addToTableList('RUNSESSION_PARAMETER')
            hltkeyOutput=coral.AttributeList()
            hltkeyOutput.extend('hltkey','string')
            hltkeyCondition=coral.AttributeList()
            hltkeyCondition.extend('name','string')
            hltkeyCondition.extend('runnumber','unsigned int')
            hltkeyCondition['name'].setData('CMS.LVL0:HLT_KEY_DESCRIPTION')
            hltkeyCondition['runnumber'].setData(int(runnumber))
            hltkeyQuery.addToOutputList('STRING_VALUE')
            hltkeyQuery.setCondition('NAME=:name AND RUNNUMBER=:runnumber',hltkeyCondition)
            #hltkeyQuery.limitReturnedRows(1)
            hltkeyQuery.defineOutput(hltkeyOutput)
            cursor=hltkeyQuery.execute()
            while cursor.next():
                hltkey=cursor.currentRow()['hltkey'].data()
                del hltkeyQuery
            result.append(hltkey)

            fillnumQuery=runinfoschema.newQuery()
            fillnumQuery.addToTableList('RUNSESSION_PARAMETER')
            fillnumOutput=coral.AttributeList()
            fillnumOutput.extend('fillnum','string')
            fillnumCondition=coral.AttributeList()
            fillnumCondition.extend('name','string')
            fillnumCondition.extend('runnumber','unsigned int')
            fillnumCondition['name'].setData('CMS.SCAL:FILLN')
            fillnumCondition['runnumber'].setData(int(runnumber))
            fillnumQuery.addToOutputList('STRING_VALUE')
            fillnumQuery.setCondition('NAME=:name AND RUNNUMBER=:runnumber',fillnumCondition)
            fillnumQuery.limitReturnedRows(1)
            fillnumQuery.defineOutput(fillnumOutput)
            cursor=fillnumQuery.execute()
            while cursor.next():
                fillnum=cursor.currentRow()['fillnum'].data()
            del fillnumQuery
            result.append(fillnum)

            starttimeQuery=runinfoschema.newQuery()
            starttimeQuery.addToTableList('RUNSESSION_PARAMETER')
            starttimeOutput=coral.AttributeList()
            starttimeOutput.extend('starttime','time stamp')
            starttimeCondition=coral.AttributeList()
            starttimeCondition.extend('name','string')
            starttimeCondition.extend('runnumber','unsigned int')
            starttimeCondition['name'].setData('CMS.LVL0:START_TIME_T')
            starttimeCondition['runnumber'].setData(int(runnumber))
            starttimeQuery.addToOutputList('TIME')
            starttimeQuery.setCondition('NAME=:name AND RUNNUMBER=:runnumber',starttimeCondition)
            starttimeQuery.defineOutput(starttimeOutput)
            cursor=starttimeQuery.execute()
            while cursor.next():
                starttime=cursor.currentRow()['starttime'].data()
            del starttimeQuery
            result.append(starttime)

            stoptimeQuery=runinfoschema.newQuery()
            stoptimeQuery.addToTableList('RUNSESSION_PARAMETER')
            stoptimeOutput=coral.AttributeList()
            stoptimeOutput.extend('stoptime','time stamp')
            stoptimeCondition=coral.AttributeList()
            stoptimeCondition.extend('name','string')
            stoptimeCondition.extend('runnumber','unsigned int')
            stoptimeCondition['name'].setData('CMS.LVL0:STOP_TIME_T')
            stoptimeCondition['runnumber'].setData(int(runnumber))
            stoptimeQuery.addToOutputList('TIME')
            stoptimeQuery.setCondition('NAME=:name AND RUNNUMBER=:runnumber',stoptimeCondition)
            stoptimeQuery.defineOutput(stoptimeOutput)
            cursor=stoptimeQuery.execute()
            while cursor.next():
                stoptime=cursor.currentRow()['stoptime'].data()
            del stoptimeQuery
            result.append(stoptime)
            session.transaction().commit()
        else:
            session.transaction().commit()
        print result
        return result
    except:
        raise
    
if __name__ == "__main__":
    from RecoLuminosity.LumiDB import sessionManager
    #svc=sessionManager.sessionManager('oracle://cms_orcoff_prep/cms_lumi_dev_offline',authpath='/afs/cern.ch/user/x/xiezhen',debugON=False)
    #session=svc.openSession(isReadOnly=True,cpp2sqltype=[('unsigned int','NUMBER(10)'),('unsigned long long','NUMBER(20)')])
    #lsresult=trgFromOldLumi(session,135735)
    #print lsresult
    #lshltresult=hltFromOldLumi(session,135735)
    #print lshltresult
    svc=sessionManager.sessionManager('oracle://cms_orcoff_prod/cms_runinfo',authpath='/afs/cern.ch/user/x/xiezhen',debugON=False)
    session=svc.openSession(isReadOnly=True,cpp2sqltype=[('unsigned int','NUMBER(10)'),('unsigned long long','NUMBER(20)')])
    runsummary(session,'CMS_RUNINFO',135735,complementalOnly=True)
    del session