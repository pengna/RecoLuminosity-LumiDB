#!/usr/bin/env python
VERSION='1.00'
import os,sys
import coral
from RecoLuminosity.LumiDB import argparse,nameDealer,selectionParser,hltTrgSeedMapper

class constants(object):
    def __init__(self):
        self.LUMIUNIT='E27cm^-2'
        self.NORM=16400
        self.LUMIVERSION='0001'
        self.BEAMMODE='stable' #possible choices stable,quiet,either
        self.VERBOSE=False
def deliveredLumiForRun(dbsession,c,runnum):
    #
    #select sum(INSTLUMI) from lumisummary where runnum=124025 and lumiversion='0001';
    #apply norm factor on the query result 
    #unit E27cm^-2 
    #
    if c.VERBOSE:
        print 'deliveredLumiForRun : norm : ',c.NORM,' : run : ',runnum
    delivered=0.0
    try:
        dbsession.transaction().start(True)
        schema=dbsession.nominalSchema()
        query=schema.tableHandle(nameDealer.lumisummaryTableName()).newQuery()
        query.addToOutputList("sum(INSTLUMI)","totallumi")
        queryBind=coral.AttributeList()
        queryBind.extend("runnum","unsigned int")
        queryBind.extend("lumiversion","string")
        queryBind["runnum"].setData(int(runnum))
        queryBind["lumiversion"].setData(c.LUMIVERSION)
        result=coral.AttributeList()
        result.extend("totallumi","float")
        query.defineOutput(result)
        query.setCondition("RUNNUM =:runnum AND LUMIVERSION =:lumiversion",queryBind)
        cursor=query.execute()
        while cursor.next():
            delivered=cursor.currentRow()['totallumi'].data()*c.NORM
        del query
        dbsession.transaction().commit()
        print "Delivered Luminosity for Run "+str(runnum)+" (beam "+c.BEAMMODE+"): "+str(delivered)+c.LUMIUNIT
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession

    
def deliveredLumiForRange(dbsession,c,inputfile):
    #
    #in this case,only take run numbers from theinput file
    #
    if c.VERBOSE:
        print 'deliveredLumiForRange : norm : ',c.NORM,' : inputfile : ',inputfile
    
    f=open(inputfile,'r')
    content=f.read()
    s=selectionParser.selectionParser(content)
    for run in s.runs():
        deliveredLumiForRun(dbsession,c,run)
    
def recordedLumiForRun(dbsession,c,runnum):
    if c.VERBOSE:
        print 'recordedLumiForRun : run : ',runnum,' : norm : ',c.NORM,' : LUMIVERSION : ',c.LUMIVERSION
    #
    #LS_length=25e-9*numorbit*3564(sec)
    #LS deadfraction=deadtimecount/(numorbit*3564) 
    #select distinct lumisummary.instlumi*trg.deadtime/(lumisummary.numorbit*3564) as deadfraction from trg,lumisummary where trg.runnum=124025 and lumisummary.runnum=124025 and lumisummary.lumiversion='0001' and lumisummary.cmslsnum=1 and trg.cmsluminum=1;
    #
    #let oracle do everything!
    #
    #select sum( lumisummary.instlumi*(1-trg.deadtime/(lumisummary.numorbit*3564))) as recorded from trg,lumisummary where trg.runnum=124025 and lumisummary.runnum=124025 and lumisummary.lumiversion='0001' and lumisummary.cmslsnum=trg.cmsluminum and lumisummary.cmsalive=1 and trg.bitnum=0;
    #multiply query result by norm factor, attach unit
    #7.368e-5*16400.0=1.2083520000000001
    recorded=0.0
    try:
        dbsession.transaction().start(True)
        schema=dbsession.nominalSchema()
        query=schema.newQuery()
        query.addToTableList(nameDealer.lumisummaryTableName(),'lumisummary')
        query.addToTableList(nameDealer.trgTableName(),'trg')
        queryCondition=coral.AttributeList()
        queryCondition.extend("runnumber","unsigned int")
        queryCondition.extend("lumiversion","string")
        queryCondition.extend("alive","bool")
        queryCondition.extend("bitnum","unsigned int")
        queryCondition["runnumber"].setData(int(runnum))
        queryCondition["lumiversion"].setData(c.LUMIVERSION)
        queryCondition["alive"].setData(True)
        queryCondition["bitnum"].setData(0)
        query.setCondition("trg.RUNNUM =:runnumber AND lumisummary.RUNNUM=:runnumber and lumisummary.LUMIVERSION =:lumiversion AND lumisummary.CMSLSNUM=trg.CMSLUMINUM AND lumisummary.cmsalive =:alive AND trg.BITNUM=:bitnum",queryCondition)
        query.addToOutputList("sum(lumisummary.INSTLUMI*(1-trg.DEADTIME/(lumisummary.numorbit*3564)))","recorded")
        result=coral.AttributeList()
        result.extend("recorded","float")
        query.defineOutput(result)
        cursor=query.execute()
        while cursor.next():
            recorded=cursor.currentRow()["recorded"].data()*c.NORM
        del query
        dbsession.transaction().commit()
        print "Recorded Luminosity for Run "+str(runnum)+" : "+str(recorded)+c.LUMIUNIT
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession
    
def recordedLumiForRange(dbsession,c,inputfile):
    if c.VERBOSE:
        print 'recordedLumi : inputfile : ',inputfile,' : norm : ',c.NORM,' : LUMIVERSION : ',c.LUMIVERSION
    f=open(inputfile,'r')
    content=f.read()
    s=selectionParser.selectionParser(content)
    runsandLSStr=s.runsandlsStr()
    runsandLS=s.runsandls()
    if c.VERBOSE:
        print 'recordedLumi : selected runs and LS ',runsandLS
    recorded={}
    try:
        dbsession.transaction().start(True)
        schema=dbsession.nominalSchema()
        query=schema.newQuery()
        query.addToTableList(nameDealer.lumisummaryTableName(),'lumisummary')
        query.addToTableList(nameDealer.trgTableName(),'trg')
        for runnumstr,LSlistStr in runsandLSStr.items():
            query.addToOutputList("sum(lumisummary.INSTLUMI*(1-trg.DEADTIME/(lumisummary.numorbit*3564)))","recorded")
            result=coral.AttributeList()
            result.extend("recorded","float")
            query.defineOutput(result)
            queryCondition=coral.AttributeList()
            queryCondition.extend("runnumber","unsigned int")
            queryCondition.extend("lumiversion","string")
            queryCondition.extend("alive","bool")
            queryCondition.extend("bitnum","unsigned int")
            realLSlist=runsandLS[int(runnumstr)]

            queryCondition["runnumber"].setData(int(runnumstr))
            queryCondition["lumiversion"].setData(c.LUMIVERSION)
            queryCondition["alive"].setData(True)
            queryCondition["bitnum"].setData(0)
            for l in realLSlist:
                queryCondition.extend(str(l),"unsigned int")
                queryCondition[str(l)].setData(int(l))
            o=[':'+x for x in LSlistStr]
            inClause='('+','.join(o)+')'
            query.setCondition("trg.RUNNUM =:runnumber AND lumisummary.RUNNUM=:runnumber and lumisummary.LUMIVERSION =:lumiversion AND lumisummary.CMSLSNUM=trg.CMSLUMINUM AND lumisummary.cmsalive =:alive AND trg.BITNUM=:bitnum AND lumisummary.CMSLSNUM in "+inClause,queryCondition)
            cursor=query.execute()
            while cursor.next():
                recorded[int(runnumstr)]=cursor.currentRow()['recorded'].data()
        del query
        dbsession.transaction().commit()
        for run,recd in  recorded.items():
            print "Recorded Luminosity for Run "+str(run)+" : "+str(recd*c.NORM)+c.LUMIUNIT
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession
        
    
def effectiveLumiForRun(dbsession,c,runnum,hltpath=''):
    if c.VERBOSE:
        if len(hltpath)==0:
            hltpath='All'
        print 'effectiveLumiForRun : runnum : ',runnum,' : hltpath : ',hltpath,' : norm : ',c.NORM,' : LUMIVERSION : ',c.LUMIVERSION
    #
    #select TRGHLTMAP.HLTPATHNAME,TRGHLTMAP.L1SEED from TRGHLTMAP,CMSRUNSUMMARY where TRGHLTMAP.HLTKEY=CMSRUNSUMMARY.HLTKEY and CMSRUNSUMMARY.RUNNUM=124025;
    #loop over all the selected HLTPath,seed 
    #select PRESCALE from HLT where RUNNUM=124025 and PATHNAME='HLT_EgammaSuperClusterOnly_L1R' order by cmsluminum;
    #select PRESCALE,DEADTIME from trg where runnum=124025 and bitname='L1_SingleMu0' order by cmsluminum;
    #select deadtime from trg where runnum=124025 and 
    #select lumisummary.instlumi from lumisummary,trg where lumisummary.runnum=124025 and trg.runnum=124025 and lumisummary.cmslsnum=trg.cmsluminum and lumisummary.cmsalive=1 and trg.bitnum=0 order by trg.cmsluminum
    hltprescale=0
    l1prescale=0
    
    try:
        collectedseeds=[]
        filteredbits=[]
        dbsession.transaction().start(True)
        schema=dbsession.nominalSchema()
        query=schema.newQuery()
        query.addToTableList(nameDealer.cmsrunsummaryTableName(),'cmsrunsummary')
        query.addToTableList(nameDealer.trghltMapTableName(),'trghltmap')
        queryCondition=coral.AttributeList()
        queryCondition.extend("runnumber","unsigned int")
        queryCondition["runnumber"].setData(int(runnum))
        query.setCondition("trghltmap.HLTKEY=cmsrunsummary.HLTKEY AND cmsrunsummary.RUNNUM=:runnumber",queryCondition)
        query.addToOutputList("trghltmap.HLTPATHNAME","hltpathname")
        query.addToOutputList("trghltmap.L1SEED","l1seed")
        result=coral.AttributeList()
        result.extend("hltpathname","string")
        result.extend("l1seed","string")
        query.defineOutput(result)
        cursor=query.execute()
        while cursor.next():
            hltpathname=cursor.currentRow()["hltpathname"].data()
            l1seed=cursor.currentRow()["l1seed"].data()
            collectedseeds.append((hltpathname,l1seed))
        del query
        for ip in collectedseeds:
            l1bitname=hltTrgSeedMapper.findUniqueSeed(ip[0],ip[1])
            if l1bitname:
                filteredbits.append((ip[0],l1bitname))
        dbsession.transaction().commit()
        print "filtered result : ",filteredbits
        
        #print "Recorded Luminosity for Run "+str(runnum)+" : "+str(recorded)+c.LUMIUNIT
    except Exception,e:
        print str(e)
        dbsession.transaction().rollback()
        del dbsession
        
def effectiveLumiForRange(dbsession,c,inputfile,hltpath=''):
    if c.VERBOSE:
        print 'effectiveLumiForRange : inputfile : ',inputfile,' : hltpath : ',hltpath,' : norm : ',c.NORM,' : LUMIVERSION : ',c.LUMIVERSION


def main():
    c=constants()
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),description="Lumi Calculations")
    # add required arguments
    parser.add_argument('-c',dest='connect',action='store',required=True,help='connect string to lumiDB')
    # add optional arguments
    parser.add_argument('-P',dest='authpath',action='store',help='path to authentication file')
    parser.add_argument('-n',dest='normfactor',action='store',help='normalization factor')
    parser.add_argument('-r',dest='runnumber',action='store',help='run number')
    parser.add_argument('-i',dest='inputfile',action='store',help='lumi range selection file, optional for recorded and effective actions, not taken by delivered action')
    parser.add_argument('-b',dest='beammode',action='store',help='beam mode, optional for delivered action, default "stable", choices "stable","quiet","either"')
    parser.add_argument('-lumiversion',dest='lumiversion',action='store',help='lumi data version, optional for all, default 0001')
    parser.add_argument('-hltpath',dest='hltpath',action='store',help='specific hltpath to calculate the effective luminosity, default to All')
    parser.add_argument('action',choices=['delivered','recorded','effective'],help='lumi calculation types')
    parser.add_argument('--verbose',dest='verbose',action='store_true',help='verbose')
    parser.add_argument('--debug',dest='debug',action='store_true',help='debug')
    # parse arguments
    args=parser.parse_args()
    connectstring=args.connect
    runnumber=0
    svc = coral.ConnectionService()
    isverbose=False
    if args.debug :
        msg=coral.MessageStream('')
        msg.setMsgVerbosity(coral.message_Level_Debug)
        c.VERBOSE=True
    hpath=''
    ifilename=''
    beammode='stable'
    if args.verbose :
        c.VERBOSE=True
    if args.authpath and len(args.authpath)!=0:
        os.environ['CORAL_AUTH_PATH']=args.authpath
    if args.normfactor:
        c.NORM=args.normfactor
    if args.lumiversion:
        c.LUMIVERSION=args.lumiversion
    if args.beammode:
        c.BEAMMODE=args.beammode
    if args.inputfile and len(args.inputfile)!=0:
        ifilename=args.inputfile
    if args.runnumber :
        runnumber=args.runnumber
    if len(ifilename)==0 and runnumber==0:
        raise "must specify either a run (-r) or an input run selection file (-i)"
    session=svc.connect(connectstring,accessMode=coral.access_Update)
    session.typeConverter().setCppTypeForSqlType("unsigned int","NUMBER(10)")
    session.typeConverter().setCppTypeForSqlType("unsigned long long","NUMBER(20)")
    if args.action == 'delivered':
        if runnumber!=0:
            deliveredLumiForRun(session,c,runnumber)
        else:
            deliveredLumiForRange(session,c,ifilename);
    if args.action == 'recorded':
        if runnumber!=0:
            recordedLumiForRun(session,c,runnumber)
        else:
            recordedLumiForRange(session,c,ifilename)
    if args.action == 'effective':
        if args.hltpath and len(args.hltpath)!=0:
            hpath=args.hltpath
        if runnumber!=0:
            effectiveLumiForRun(session,c,runnumber,hpath)
        else:
            effectiveLumiForRange(session,c,ifilename,hpath)
    del session
    del svc
if __name__=='__main__':
    main()
    