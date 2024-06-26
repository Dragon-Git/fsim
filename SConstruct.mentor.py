EnsureSConsVersion(3, 0) # for Help() append

import os

Help('''
=============================================================================
SConstruct for Mentor configurations:

Targets:
- compile
- compile_rtl
- sim_rtl / rtl
- sim_cell / cell
- sim_inst / inst

The simulation targets will automatically call the compile
targets as needed due to their dependencies.

Examples:
scons -f SConstruct.mentor.py (runs every option by default)
scons -f SConstruct.mentor.py compile
scons -f SConstruct.mentor.py sim_cell --svconfig=1

To clean:
scons -f SConstruct.mentor.py -c

Notable SCons concepts:
- We set VSIM_ARGS in our vsimEnv object, overriding the tool's default
- We tweaked the tool so that if it finds 'libmap' in the .sv filename,
it will append it with the '-libmap' flag
- We added to 'Clean' so SCons can remove the extra libraries generated
- We append a custom, per-target additional argument to VSIM_ARGS in
each of the vsimEnv.Sim() calls. Anything passed in after the target and
source lists overwrites the defaults in the tool and the vsimEnv object
- We dynamically select a dependency for the 'sim_rtl' target based on
the value passed in with the --svconfig option
=============================================================================
''', append=True) # Only works on newer install of SCons
# reference site_tools/site_init.py for help on --<options> if using
# older version of SCons

##############
### Env Setup
vsimEnv = Environment(
    ENV={
        'PATH': os.environ['PATH']
    },
    TOOLS=['vsim'],
    SCANNERS=[svscan, fscan] + scanners,
    WORK='work',
    SVCONFIG=GetOption('svconfig'),
    VSIM_ARGS=['-c', '-do run_all.sim'],
)

############
### Compile
com = vsimEnv.Com('compile_mentor.log', ['libmap.sv', 'source_code.f'])
Alias('compile', com)
Clean(com, ['rtlLib', 'gateLib'])

#####################
### Compile RTL Only
com_rtl = vsimEnv.Com('compile_rtl_mentor.log', ['libmap_rtl.sv', 'source_code.f'])
Alias('compile_rtl', com_rtl)
Clean(com_rtl, [Glob('*Lib')])

#################
### Simulate RTL
sim_rtl = vsimEnv.Sim(
'simulate_rtl_mentor.log',
[com_rtl if vsimEnv['SVCONFIG'] != '' else com],
VSIM_ARGS=vsimEnv['VSIM_ARGS'] + ['rtl_config${SVCONFIG}']
)
Alias('sim_rtl', sim_rtl)
Alias('rtl', sim_rtl)

##################
### Simulate Cell
sim_cell = vsimEnv.Sim(
'simulate_cell_mentor.log',
[com_rtl],
VSIM_ARGS=vsimEnv['VSIM_ARGS'] + ['cell_config${SVCONFIG}']
)
Alias('sim_cell', sim_cell)
Alias('cell', sim_cell)

##################
### Simulate Inst
sim_inst = vsimEnv.Sim(
'simulate_inst_mentor.log',
[com_rtl],
VSIM_ARGS=vsimEnv['VSIM_ARGS'] + ['cell_config${SVCONFIG}']
)
Alias('sim_inst', sim_inst)
Alias('inst', sim_inst)

#######################
### Additional cleanup
Clean([sim_rtl, sim_cell, sim_inst], ['transcript'])
Clean([com, com_rtl, sim_rtl, sim_cell, sim_inst], [Glob('*~')])