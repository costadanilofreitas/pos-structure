# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\bohpump\doc.py
"""__BEGINDOC__
= MW:APP Data Pump Client component =
||Language:           || Python ||
||Executable module:  || datapumpcli.pypkg ||
||Multi-instance:     || No ||
||Required libraries: || msgbus, systools, cfgtools ||
||Required services:  || !AuditLogger, !StoreWideConfig ||

This component is responsible for acquiring the events logged by the MW:APP !AuditLogger component and to submit them to an external Web service, which will persist the information outside the store.
The data pump client component can be configured to work in conjunction with the MOD_DATAPUMP Apache 2 module, as illustrated on the scheme below.

{{{
 +-------------------+       +-------------------+
 |  Store's Network  |       |   Corporate       |
 |                   |       |        Server     |
 |  +-------------+  |       |                   |
 |  | AuditLogger |  |       |+-----------------+|
 |  |  Component  |  |       || Event log files ||
 |  +------+------+  |       |+--------^--------+|
 |         |         |       |         |         |
 |  +------v------+  |       |+--------+--------+|
 |  | DataPumpCli |  |       ||     Apache 2    ||
 |  |  Component  |  |       || W/ mod_datapump ||
 |  +------+------+  |       |+--------^--------+|
 +---------|---------+       +---------|---------+
           |                           |
           +------------//-------------+
}}}

Another configuration option is to setup a cloud storage system, such as Amazon S3/SimpleDB or Google Application Engine (GAE), to enable the storage of the event log files without worrying about availability, flexibility and scalability.
This scenario substitutes the need of a Corporate Server and a team to manage that server(s); however, it is subjected to additional charges. Please, before configuring anything, be sure to check the costs of those services, which can be provided on the following links:
  - Amazon S3: http://aws.amazon.com/s3/
  - Amazon SimpleDB: http://aws.amazon.com/simpledb/
  - GAE: http://code.google.com/appengine/docs/billing.html

The data pump client component configuration is flexible enough, in order to allow the setup of different instances for each set of events. In this way, it is possible to send different event types to different remote servers (or services).

The information sent is enveloped into a HTTP message with the following properties:
 - HTTP method: POST
 - Content type: application/x-www-form-urlencoded
 - Content fields:
   - storeId: The unique store identification;
   - eventType: The event type (e.g. PAID, VOID_LINE, VOID_ORDER, etc.);
   - eventPeriod: The business day when the event occurred in the format YYYYMMDD;
   - eventId: The event unique id within the event period of the store;
   - eventEncoded: If set to 1 (one), indicates that the event data is encoded; otherwise, the event data is a plain text XML document. Find further information on encoding below;
   - eventData: The event data to be persisted in the remote server;
   - authKey: An authentication key to ensure that the request is valid.

The '''authKey''' is formed by the hexadecimal representation of the MD5 hash of the following string:
   <String to be hashed> = (storeId + '|' + eventPeriod + '|' + eventId + '|' + secretKey)
Please refer to the Configuration Model section, later on this document, to find how the '''secretKey''' parameter is configured.

The event data encoding is used to save storage and traffic. It is based in two algorithms:
 - zlib: used to compress the original event buffer;
 - base64: used to encode the compressed buffer into a ASCII representation.

Any application that intends to read the event log persisted must:
 - Decode the event data buffer using base64 algorithm; and,
 - Decompress the buffer using zlib algorithm.
Below there is a sample decode function implemented in C using zlib and APR libraries.

{{{
/**
 * Decode (base64decode+decompress) an event data buffer.
 * @param  mp       memory pool for allocation
 * @param  evtdata  encoded event data
 * @param  szout    (output) size of the output decoded buffer
 * @return Decoded buffer or NULL in case of any errors
 */
static const char* decode_evtdata(apr_pool_t *mp, const char *evtdata, apr_size_t *szout) {
    int            ret=Z_OK;
    z_stream       strm;
    apr_size_t     szin=0;
    char          *outbase64=0x00;
    char          *output=0x00;
    apr_pool_t    *lmp=0x00;
    /* create a local memory pool */
    if(apr_pool_create(&lmp,0x00) || !lmp) {
        return(0x00);
    }
    /* first step: get base64 output buffer */
    for(;;) {
        szin=apr_base64_decode_len(evtdata);
        outbase64=apr_pcalloc(lmp,szin+1);
        szin=apr_base64_decode_binary((unsigned char*)outbase64, evtdata);
        if(!szin) {
            ret=Z_ERRNO;
        }
        (*szout)=*((int*)outbase64);
        output=apr_pcalloc(mp,(*szout)+1);
        break;
    }
    /* check for errors */
    if(ret) {
        if(lmp) {
            apr_pool_destroy(lmp);
            lmp=0x00;
        }
        return(0x00);
    }
    /* second step: decompress the buffer */
    for(;;) {
        strm.zalloc = Z_NULL;
        strm.zfree = Z_NULL;
        strm.opaque = Z_NULL;
        strm.avail_in = 0;
        strm.next_in = Z_NULL;
        ret = inflateInit(&strm);
        if(ret!=Z_OK) {
            inflateEnd(&strm);
            break;
        }
        strm.avail_in=szin-sizeof(int);
        strm.next_in=(Bytef*)(outbase64+sizeof(int));
        strm.avail_out=(*szout);
        strm.next_out=(Bytef*)output;
        ret=inflate(&strm,Z_NO_FLUSH);
        if(ret != Z_STREAM_END) {
            inflateEnd(&strm);
            break;
        }
        *szout=(*szout)-strm.avail_out;
        inflateEnd(&strm);
        ret=Z_OK;
        break;
    }
    if(lmp) {
        apr_pool_destroy(lmp);
        lmp=0x00;
    }
    return(output);
}
}}}

== The MW:APP Data Pump Apache module ==

The Data Pump Apache module is also part of this component. It is the server-side implementation and it is responsible for the persistence of the received event logs. If necessary, it also decodes the received events so they become easier to manipulate.
The Data Pump Apache module generates a file for each store and business period. The naming convention for the event log files is: YYYYDDMM_[storeid]_event.log.
The event log file format is based on SQLite3. Its structure consists on a single database table with the following fields:
 - !EventId {INTEGER}: Event log unique identification within the store and business period. This is also the primary key of the table;
 - !EventType {VARCHAR(30)}: Event log type (e.g.: PAID, VOID_ORDER, etc.);
 - !EventPeriod {INTEGER}: The business period when the event occurred (YYYYMMDD);
 - !EventData {VARCHAR}: The event data already decoded and ready to be used.

Data Pump Apache module installation instructions:
 1. Install the Apache WEB server. The instructions on how to do that can be found on the following address: http://httpd.apache.org/docs/2.0/install.html
 2. The Data pump module is distributed with the MW:APP binaries.
   The following library files available in the {MW:APP install folder}/bin folder are needed for the instalation:
    * libsystools
    * libzlib
    * libsqlite3
    * mod_datapump.so (mod_datapump.dll in Windows environments must be renamed to .so)
 3. Copy the mod_datapump.so file into the Apache modules folder (e.g. {Apache installation folder}/modules)
 4. Copy the above listed libraries into the Apache binaries folder (e.g. {Apache installation folder}/bin)
 5. Setup Apache configuration file http.conf inside {Apache installation folder}/conf folder as shown below:
 {{{
       LoadModule datapump_module modules/mod_datapump.so
       <IfModule datapump_module>
           EventsFolder    "{The folder for the event log files}"
           SecretKey       "{A secret key which must be equal to the one set in the Data Pump Client component configuration}"
       </IfModule>
       <Location /datapump>
           SetHandler datapump_module
           Options None
           Order allow,deny
           Allow from all
       </Location>
}}}
 6. Restart the Apache Web server.

= Configuration model: =
  - Group '''!DataPump''' - Component root configuration group.
    - Key '''serverURL''' (string) - Corporate Server URL. This can also be the Google Application URL, which may be used as a cloud storage.
    - Key '''retryWait''' (integer) - Time between each event log retry in milliseconds. If a HTTP error or any communication error occurs, it'll be used for the next retry.
    - Key '''throttle''' (integer) - Time between each event log send operation in milliseconds.
    - Key '''initialPeriod''' {string} - The very first initial period. Events older than that will not be submitted to the server. The excepted format is YYYYMMDD.
    - Key '''controlFilePath''' (string) - Full path and file name to be used as the control file. Each instance of this component must have its own control file.
    - Key '''secretKey''' - (string) - A secret key used to generate the request authentication key and validate the request.
    - Key '''responseLog''' {boolean} - Enables or disables the response body logging. For debug purposes.
    - Key '''eventFilter''' {array} (1..n) - The list of the Event Types to be submitted to the remote server. This is the filter used to determine which events should be sent to the server.
    - Key '''useAWSSimpleDB''' {boolean} - Enables or disables the use of the Amazon Web Services (AWS) SimpleDB for data storage.
    - Group '''AWSSimpleDB''' - This group is used to setup AWS-related configuration
      - Key '''accessKey''' - (string) - AWS account access key used in the request authentication.
      - Key '''secretKey''' - (string) - AWS account secret key used in the request authentication.

Please note that, like all Python components, the "Process.Arguments" configuration key must be correctly defined in order to tell the python interpreter how to start this component.
A typical process configuration for this component can be seen below:
{{{
#!xml
<group name="Process">
    <key name="Arguments">
        <array>
            <string>runpackage.py</string>
            <string>common.pypkg</string>
            <string>datapumpcli.pypkg</string>
        </array>
    </key>
    <key name="ExecutableModule">
        <string>python</string>
    </key>
</group>
}}}

= Service: =
== DataPumpCli/!DataPump ==
This is the service responsible for handling audit log events to be submitted to remote servers.

= Tokens: =
This service does not handle any token. The service is based on MW:APP events only.

= Events: =
== Input: ==
  - Subject: '''AUDITLOGGER''' - Event submitted by the !AuditLogger component, it carries all information about the event.
== Output: ==
No output events available for this component.

__ENDDOC__"""
pass