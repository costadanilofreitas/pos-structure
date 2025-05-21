# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\reports\doc.py
"""__BEGINDOC__
= Reports component =
||Language:           || Python ||
||Executable module:  || reports.pypkg ||
||Multi-instance:     || no     ||
||Required libraries: || msgbus ||
||Required services:  || Persistence ||

This component is responsible for generating and formatting all sort of reports for the system.

Reports can be generated in many formats, depending on the report purpose. Printable reports are usually formatted in
plain text, suitable to be directly printed on a POS printer.[[BR]]
Some reports may be generated on a format suitable to be exported to other systems, such as the Dashboard (which uses XML reports).

The "kernel" implementation of this component has only the logic to load other Python scripts containing the real
reports implementation (represented as Python functions). This means that this component cannot generate any report by itself.

When starting up, the '''Reports''' component will load external Python scripts (defined in the component configuration) and look
for exported functions. Each "public" Python function is considered a report generation function and the name of the function defines
the name of the report.

Report functions can receive any number of parameters necessary for it to generate and format the report. The must return either a string
representing the formatted report or a 2-elements tuple, where the first element is the message-bus format (FM_*) and the second element
is the formatted report.[[BR]]
See bellow examples of valid report functions (stubs):
{{{
#!python
def cash(posid, business_period):
    '''Generates a CASH report for the given POS id and business period'''
    return "CASH REPORT
Pos ID: %s
Business Period: %s"%(posid, business_period)
def cashXml(posid, business_period):
    '''Generates a CASH XML for the given POS id and business period'''
    xml = '<Cash posid="%s" period="%s"/>'%(posid, business_period)
    return (FM_XML, xml)
}}}
The functions above define two reports, named "cash" and "cashXml" respectively. The second one (cashXml) returns an XML-formatted report.
Note that these are only stubs that don't return any useful data on purpose.

= Configuration model: =
  - Group '''Reports''' - component root configuration group
    - Key '''Modules''' (array) (1..n) - List of modules to load, containing report functions. E.g.: "sale_reports","manager_reports","dashboard"
    - Key '''!ServiceName''' (string) - Used to override default exported service name
    - Key '''Language''' (string) - Default language code to load on startup. Default: "en"
    - Key '''!TranslationsDir''' (string) - Directory from where the json translation files are loaded. Default: "{loader directory}/python/translations"

Please note that like all Python components, the "Process.Arguments" configuration key must be correctly defined in order to tell the python
interpreter how to start this component.
A typical process configuration for this component can be seem bellow:
{{{
#!xml
<group name="Process">
    <key name="Arguments">
        <array>
            <string>runpackage.py</string>
            <!-- this is where the external report modules should be -->
            <string>{HVDATADIR}/bundles/reports/python</string>
            <string>common.pypkg</string>
            <string>reports.pypkg</string>
        </array>
    </key>
    <key name="ExecutableModule">
        <string>python</string>
    </key>
</group>
}}}

= Services: =
== Reports/!ReportsGenerator ==
This is the service responsible to generate and format reports in server. The name of the service can be overriden by !ServiceName parameter

= Tokens: =
== TK_REPORT_GENERATE ==
Generates a formatted report.

'''Request:'''
||Format: || FM_PARAM ||
||Parameter 0:     || Report name (E.g.: "cash") ||
||Parameter 1..n:  || Report parameters (varies based on the report) ||
'''Response:'''
||Token:           || TK_SYS_ACK on success, TK_SYS_NAK otherwise ||
||Format:          || (varies based on the report) ||
||Data:            || Formatted report ||

= Events: =
This component does not send nor receive any events.

__ENDDOC__"""
pass