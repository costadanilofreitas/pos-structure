# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\doc.py
"""__BEGINDOC__
= Python Scripts component =
||Language:           || Python ||
||Executable module:  || pyscripts.pypkg ||
||Multi-instance:     || no ||
||Required libraries: || msgbus, cfgtools ||
||Required services:  || none ||

This component is responsible for running all sorts of Python scripts in the system.

The "kernel" implementation of this component has only the logic to load other Python scripts and allow those scripts to register
call-back functions for events.

When starting up, this component will load external Python scripts (defined in the component configuration) and look
for an exported function called '''main''' and, if that function is present, it will be called with no arguments, so that module can perform
its initialization routines.

The most notable function of this component is to execute POS action with specific business logics.

= Configuration model: =
  - Group '''!PythonScripts''' - component root configuration group
    - Key '''Modules''' (array) (1..n) - List of modules to load. E.g.: "posactions","poslisteners"

Please note that like all Python components, the "Process.Arguments" configuration key must be correctly defined in order to tell the python
interpreter how to start this component.
A typical process configuration for this component can be seem bellow:
{{{
#!xml
<group name="Process">
    <key name="Arguments">
        <array>
            <string>runpackage.py</string>
            <!-- this is where the external modules should be -->
            <string>{HVDATADIR}/bundles/pyscripts/python</string>
            <string>common.pypkg</string>
            <string>pyscripts.pypkg</string>
        </array>
    </key>
    <key name="ExecutableModule">
        <string>python</string>
    </key>
</group>
}}}

= Services: =
== Scripts/!PythonScripts ==
This is the service responsible to execute Python scripts.

= Tokens: =
This component does not handle any special message token.

= Events: =
This component does not send nor receive any events.[[BR]]
Please note that external modules loaded by this component may (and probably will) listen to many system events in order to implement their
business rules. A good example is the '''posactions''' modules, which listens to the '''POS_ACTION''' synchronous event to execute POS actions.
__ENDDOC__"""
pass