import urllib, json, ssl
import sys, datetime, getpass
import urllib2 as req

# Defines the entry point into the script
def main(argv=None):

    # disable ssl certificate validation
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    # Prompt for server hostname
    serverHost = raw_input('Enter ArcGIS for Server fully qualified domain name: ')

    # Prompt for admin username
    adminUsername = raw_input('Enter administrator username: ')

    # Prompt for admin password (getpass commented so it will work in my testing environment)
    adminPassword = getpass.getpass(prompt='Enter administrator password: ')

    scanResults = []
    defineScanInfo()
    serverUrl = checkHTTPS(serverHost, scanResults, adminUsername, adminPassword)
    token = generateToken(adminUsername,adminPassword,serverUrl + '/admin/generateToken')
    if token == 'Failed':
        print 'Unable to complete scan'
        sys.exit(0)
    checkStdQry(serverUrl,token,scanResults)
    checkToken(serverUrl + '/tokens/generateToken',scanResults)
    checkToken(serverUrl + '/admin/generateToken',scanResults)
    checkRest(serverUrl,token,scanResults)
    checkPSA(serverUrl,token,scanResults)
    checkSystem(serverUrl,token,scanResults)
    checkWA(serverUrl,token,scanResults)
    serviceList = getServices(serverUrl,token)
    checkFeatureSvc(serverUrl,token,serviceList,scanResults)
    checkMapSvc(serverUrl,token,serviceList,scanResults)
    scanReportHTML(serverHost,scanResults)

# Establish a sorted list object to pass parameters in order.
class SortedDict(dict):
    def __repr__(self):
        keys = sorted(self.keys())
        result = ("{!r}: {!r}".format(k, self[k]) for k in keys)
        return "{{{}}}".format(", ".join(result))

    __str__ = __repr__

# Function to generate token
def generateToken(username,password,tokenUrl):
    params = SortedDict({'username':username,
              'password':password,
              'client':'requestip',
			  'expiration': 30,
              'f':'json'})

    try:
        response = urllib.urlopen(tokenUrl,urllib.urlencode(params),proxies={}).read()
        
        genToken = json.loads(response)
        if 'token' in genToken.keys():
            return genToken.get('token')
        else:
            print 'Invalid administrator username or password'
            return 'Failed'
    except Exception, e:
        print '\n Unable to generate token - ' + str(e)
        return 'Failed'

# Check if HTTP and/or HTTPS is supported
def checkHTTPS(hostname, scanResults, username, password):
    
    try:
        sURI = 'http://' + hostname + ':6080/arcgis/admin/generateToken?f=json'
        response = urllib.urlopen(sURI,proxies={}).read()

        sslInfo = json.loads(response)
        if 'ssl' in sslInfo.keys():
            https = sslInfo['ssl']['supportsSSL']
            if (https):
                serverUrl = 'https://' + hostname + ':6443/arcgis'
            else:
                serverUrl = 'http://' + hostname + ':6080/arcgis'
                scanResults.append({'id':'SS01','level':'Critical','test':'Web communication','result':scanInfo['SS01']})

            return serverUrl
        else:
            print 'Error accessing ArcGIS for Server on ' + hostname
            sys.exit(1)
    except Exception, e:
        print '\n Error accessing ArcGIS for Server on ' + hostname + ' \n checkHTTPS failed ' + str(e)
        sys.exit(1)

# Check if standardized queries are enabled
def checkStdQry(serverUrl,token,scanResults):
    try:
        params = {'token':token}
        reqUrl = serverUrl + '/admin/system/properties?f=json'
        response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
        sysProps = json.loads(response.read())
        if 'standardizedQueries' in sysProps.keys():
            if str(sysProps.get('standardizedQueries')).lower() == 'false':
                scanResults.append({'id':'SS02','level':'Critical','test':'Standardized queries','result':scanInfo['SS02']})
    except:
        print 'Error checking Server system properties'

# Check if GET requests and POST requests with credentials as query paramter are allowed for token requests
def checkToken(tokenUrl,scanResults):
    try:
        reqUrl = tokenUrl + '?username=test&password=test&f=json'
        response = urllib.urlopen(reqUrl, proxies={})
        tokenResponse = json.loads(response.read())
        if 'error' in tokenResponse.keys():
            if tokenResponse['error'].get('code') != 405:
                scanResults.append({'id':'SS03','level':'Critical','test':'Token requests','result':tokenUrl + '<br>' + scanInfo['SS03']})
        elif 'ssl' not in tokenResponse.keys():
            scanResults.append({'id':'SS03','level':'Critical','test':'Token requests','result':tokenUrl + '<br>' + scanInfo['SS03']})
        params = {'client':'requestip','f':'json'}
        reqUrl = tokenUrl + '?username=test&password=test'
        response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
        tokenResponse = json.loads(response.read())
        if 'error' in tokenResponse.keys():
            if 'request should not contain' not in str(tokenResponse['error'].get('details')):
                scanResults.append({'id':'SS04','level':'Critical','test':'Token requests','result':tokenUrl + '<br>' + scanInfo['SS04']})
        elif 'messages' in tokenResponse.keys():
            if 'request should not contain' not in str(tokenResponse.get('messages')):
                scanResults.append({'id':'SS04','level':'Critical','test':'Token requests','result':tokenUrl + '<br>' + scanInfo['SS04']})
        else:
            scanResults.append({'id':'SS04','level':'Critical','test':'Token requests','result':tokenUrl + '<br>' + scanInfo['SS04']})
    except:
        print 'Error checking token requests - ' + tokenUrl

# Check if services directory is disabled and restrictions on cross-domain requests
def checkRest(serverUrl,token,scanResults):
    try:
        params = {'token':token,'f':'json'}
        reqUrl = serverUrl + '/admin/system/handlers/rest/servicesdirectory'
        response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
        restProps = json.loads(response.read())
        if str(restProps['enabled']).lower() == 'true':
            scanResults.append({'id':'SS07','level':'Important','test':'Rest services directory','result':scanInfo['SS07']})
        if restProps['allowedOrigins'] == '*':
            scanResults.append({'id':'SS08','level':'Important','test':'Cross-domain requests','result':scanInfo['SS08']})
    except:
        print 'Error checking services directory properties'

# Check if PSA account is disabled
def checkPSA(serverUrl,token,scanResults):
    try:
        params = {'token':token,'f':'json'}
        reqUrl = serverUrl + '/admin/security/psa'
        response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
        psaProps = json.loads(response.read())
        if str(psaProps['disabled']).lower() == 'false':
            scanResults.append({'id':'SS11','level':'Recommended','test':'PSA account status','result':scanInfo['SS11']})
    except:
        print 'Error obtaining PSA account status'

# Check if System folder has any permissions assigned to it
def checkSystem(serverUrl,token,scanResults):
    try:
        params = {'token':token,'f':'json'}
        reqUrl = serverUrl + '/admin/services/System/permissions'
        response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
        sysPerm = json.loads(response.read())
        if not sysPerm.get('permissions') == []:
            accessList = []
            for users in sysPerm['permissions']:
                accessList.append(str(users['principal']))
            scanResults.append({'id':'SS06','level':'Critical','test':'System folder permissions','result':'Open to roles: ' +
                                ', '.join(str(user) for user in accessList) + '<br>' + scanInfo['SS06']})
    except:
        print 'Error accessing System folder permissions'

# Check if web adaptor is registered over HTTPS
def checkWA(serverUrl,token,scanResults):
    try:
        params = {'token':token,'f':'json'}
        reqUrl = serverUrl + '/admin/system/webadaptors'
        response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
        waProps = json.loads(response.read())
        if 'webAdaptors' in waProps.keys():
            for wa in waProps['webAdaptors']:
                if wa['httpPort'] != -1:
                    scanResults.append({'id':'SS10','level':'Recommended','test':'Web adaptor registration','result':scanInfo['SS10']})
                    break
        else:
            print 'Error accessing web adaptor information'
    except:
        print 'Error accessing web adaptor information'

# Generate list of map services in all folders pulled from the admin/services page
def getServices(serverUrl,token):
    serviceList = []
    try:
        params = {'token':token,'f':'json'}
        reqUrl = serverUrl + '/admin/services'
        response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
        restRoot = json.loads(response.read())
        # Return services in root folder
        for services in restRoot['services']:
            if services['type'] == 'MapServer':
                serviceList.append(services['serviceName'])
        # Return services in subfolders
        for folder in restRoot['folders']:
            params = {'token':token,'f':'json'}
            request = urllib2.Request(serverUrl + '/admin/services/' + folder, urllib.urlencode(params))
            response = urllib2.urlopen(request)
            for services in json.loads(response.read())['services']:
                if services['type'] == 'MapServer':
                    serviceList.append(services['folderName'] + '/' + services['serviceName'])
        return serviceList
    except:
        return 'Error'

# Return list of feature services along with capabilities and xssPreventionEnabled property
def checkFeatureSvc(serverUrl,token,serviceList,scanResults):
    featureList = {}
    try:
        for service in serviceList:
            params = {'token':token,'f':'json'}
            reqUrl = serverUrl + '/admin/services/' + service + '.MapServer'
            response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
            svcParams = json.loads(response.read())
            if 'extensions' in svcParams.keys():
                for ext in svcParams['extensions']:
                    if ext['typeName'] == 'FeatureServer' and ext['enabled'] == 'true':
                        featureList[service] = [ext['capabilities'],ext['properties']['xssPreventionEnabled']]
        if len(featureList) > 0:
            for feature in featureList:
                if not str(featureList[feature][1]).lower() == 'true':
                    scanResults.append({'id':'SS05','level':'Critical','test':'Web content filtering','result':'Feature service: ' + feature +
                                        '<br>' + scanInfo['SS05']})
                featurePerm = checkPerm(serverUrl, token, feature)
                if featurePerm == 'Open':
                    featureOps = featureList[feature][0].split(',')
                    if 'Delete' in featureOps or 'Update' in featureOps:
                        scanResults.append({'id':'SS12','level':'Recommended','test':'Feature service operations','result':'Feature service: ' +
                                            feature + '<br>' + scanInfo['SS12']})
    except:
        print 'Error checking feature services'

# Check permissions on a service - return 'Open' if not secured
def checkPerm(serverUrl, token, service):
    try:
        params = {'token':token,'f':'json'}
        reqUrl = serverUrl + '/admin/services/' + service + '.MapServer/permissions'
        response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
        svcPerm = json.loads(response.read())
        if 'permissions' in svcPerm.keys():
            for principal in svcPerm['permissions']:
                if principal['principal'] == 'esriEveryone':
                    return 'Open'
            return 'Secured'
        else:
            return 'Error'
    except:
        return 'Error'

# Return list of map services with dynamic workspace enabled
def checkMapSvc(serverUrl,token,serviceList,scanResults):
    dynamicLyr = []
    try:
        for service in serviceList:
            params = {'token':token,'f':'json'}
            reqUrl = serverUrl + '/admin/services/' + service + '.MapServer'
            response = urllib.urlopen(reqUrl, urllib.urlencode(params), proxies={})
            svcParams = json.loads(response.read())
            if 'properties' in svcParams.keys():
                if 'enableDynamicLayers' in svcParams['properties'].keys():
                    if svcParams['properties']['enableDynamicLayers'] == 'true':
                        dynamicLyr.append(service)
        if len(dynamicLyr) > 0 and dynamicLyr != 'Error':
            for service in dynamicLyr:
                scanResults.append({'id':'SS09','level':'Important','test':'Dynamic workspace','result':'Map service: ' +
                                    service + '<br>' + scanInfo['SS09']})
    except:
        print 'Error checking map services'

# Output scan results to HTML format
def scanReportHTML(serverHost,scanResults):
    outputFile = 'serverScanReport_' + serverHost.split('.')[0] + '_' + str(datetime.datetime.now().date()) + '.html'
    with open(outputFile, 'w') as htmlOut:
        htmlOut.write('<html><body>\n')
        htmlOut.write('<h1>ArcGIS for Server Security Scan Report - ' + str(datetime.datetime.now().date()) + '</h1>\n')
        htmlOut.write('<h2>' + serverHost + '</h2>\n')
        if len(scanResults) == 0:
            htmlOut.write('<h3>No security items were discovered that need to be reviewed.</h3>\n')
            htmlOut.write('</body></html>')
        else:
            htmlOut.write('<h3>Potential security items to review</h3>\n')
            htmlOut.write('<table cellpadding="5">\n')
            htmlOut.write('<tr><th align="left"><u>Id</u></th>'
                          '<th align="left"><u>Severity</u></th>'
                          '<th align="left"><u>Property Tested</u></th>'
                          '<th align="left"><u>Scan Results</u></th></tr>\n')
            for scan in sorted(scanResults, key=lambda x:(x['level'],x['test'])):
                htmlOut.write('<tr valign="top"><td width="5%">' + scan['id'] + '</td>'
                              '<td width="10%">' + scan['level'] + '</td>'
                              '<td width="15%">' + scan['test'] + '</td>'
                              '<td width="70%">' + scan['result'] + '</td></tr>\n')
            htmlOut.write('</table></body></html>')
        htmlOut.close()
    print 'Server scan completed - ' + str(len(scanResults)) + ' security items noted'
    print 'Scan results written to ' + outputFile

# Function to define scan result information
def defineScanInfo():
    global scanInfo
    scanInfo = {}
    # HTTPS
    scanInfo['SS01'] = 'HTTPS is not enabled for ArcGIS Server. To prevent the interception of any communication, it is ' \
                       'recommended that you configure ArcGIS Server and ArcGIS Web Adaptor (if installed) to enforce ' \
                       'SSL encryption.'
    # standardized queries
    scanInfo['SS02'] = 'Enforcing standardized queries is disabled. To provide protection against SQL injection attacks, it is ' \
                       'critical that this option be enabled.'
    # token requests via GET
    scanInfo['SS03'] = 'Generate token requests via GET are supported.  When generating tokens via GET, a user\'s credentials ' \
                       'are sent as part of the url and can be captured and exposed through browser history or network logs. This should be ' \
                       'disabled unless required by other applications.'
    # token requests via POST with credentials in query parameter
    scanInfo['SS04'] = 'Generate token requests via POST with credentials in the query parameter are supported. When generating tokens, a ' \
                       'user\'s credentials could be provided as part of the url and may be exposed through browser history or in network ' \
                       'logs. This should be disabled unless required by other applications.'
    # web content filtering
    scanInfo['SS05'] = 'The filter web content property for this feature service is disabled.  This allows a user to enter any text ' \
                       'into the input fields and exposes it to potential cross-site scripting (XSS) attacks.  Unless unsupported HTML entities or ' \
                       'attributes are required, this property should be enabled.'
    # System folder permissions
    scanInfo['SS06'] = 'Non-default permissions are applied to the System folder in Server Manager. By default, only administrators and ' \
                       'publishers should have access to the services in the System folder.'
    # disable services directory
    scanInfo['SS07'] = 'The Rest services directory is accessible through a web browser. Unless being actively used to search for ' \
                       'and find services by users, this ' \
                       'should be disabled to reduce the chance that your services can be browsed, found in a web search, ' \
                       'or queried through HTML forms. This also provides further protection against cross-site scripting (XSS) attacks.'
    # cross-domain requests
    scanInfo['SS08'] = 'Cross-domain requests are unrestricted. To reduce the possibility of an unknown application ' \
                       'sending malicious commands to your web services, it is recommended to restrict the use of your services ' \
                       'to applications hosted only in domains that you trust.'
    # dynamic workspace
    scanInfo['SS09'] = 'Dynamic workspace is enabled for this map service.  To prevent a malicious party from obtaining the ' \
                       'workspace ID and potentially gaining access, this should be disabled.'
    # web adaptor registration
    scanInfo['SS10'] = 'One or more web adaptors are registered over HTTP. To allow Server Manager to successfully redirect to ' \
                       'HTTPS, all web adaptors should be registered over HTTPS.'
    # disable PSA account
    scanInfo['SS11'] = 'The primary site administrator account is enabled. It is recommended that you disable this account to ' \
                       'ensure that there is not another way to administer ArcGIS Server other than the group or role ' \
                       'that has been specified in your identity store.'
    # open feature service with update/delete operations
    scanInfo['SS12'] = 'This feature service has the update and/or delete operations enabled and is open to anonymous access.  This ' \
                       'allows the feature service data to be changed and/or deleted without authentication.'

# Script start
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
