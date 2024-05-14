EnsureSConsVersion(3, 0)  # for Help() append

import os

Help('''=============================================================================
SConstruct for Cadence configurations:

Targets:
- compile
- compile_rtl
- sim_rtl / rtl
- sim_cell / cell
- sim_inst / inst

The simulation targets will automatically call the compile
targets as needed due to their dependencies.

Examples:
- scons -f SConstruct.cadence.py (runs every option by default)
- scons -f SConstruct.cadence.py compile
- scons -f SConstruct.cadence.py sim_cell --svconfig=1

To clean:
- scons -f SConstruct.cadence.py -c

Notable SCons concepts:
- Added a builder to the xrun tool for handling an all-in-one command (previously used in Makefile)
- Set XRUN_ALL_ARGS in the xrunEnv object, overriding the tool's default arguments
- If 'libmap' is found in the .sv filename, the tool appends '-libmap' flag
- Append custom, per-target additional arguments to XRUN_ALL_ARGS in xrunEnv.AllIn1() calls
- Dynamically select a dependency for the 'sim_rtl' target based on the --svconfig option value
=============================================================================''', append=True)  # Only works on newer installs of SCons
# Reference site_tools/site_init.py for help on --<options> when using an older version of SCons

##############
### Env Setup
xrunEnv = Environment(
    ENV={
        'PATH': os.environ['PATH'],
        'HOME': os.environ['HOME'],
    },
    TOOLS=['xrun'],
    SCANNERS=[svscan, fscan] + scanners,
    WORK='work',
    SVCONFIG=GetOption('svconfig'),
    XRUN_ALL_ARGS=['-compcnfg', '-exit'],
)

#################
### Simulate RTL
sim_rtl = xrunEnv.AllIn1(
    'simulate_rtl_cadence.log',
    [
        'libmap_rtl.sv' if xrunEnv['SVCONFIG'] != '' else 'libmap.sv',
        'configs.sv',
        'source_code_cadence.f',
    ],
    XRUN_ALL_ARGS=xrunEnv['XRUN_ALL_ARGS'] + ['-top rtl_config${SVCONFIG}'],
)
Alias('sim_rtl', sim_rtl)
Alias('rtl', sim_rtl)

##################
### Simulate Cell
sim_cell = xrunEnv.AllIn1(
    'simulate_cell_cadence.log',
    ['libmap_rtl.sv', 'configs.sv', 'source_code_cadence.f'],
    XRUN_ALL_ARGS=xrunEnv['XRUN_ALL_ARGS'] + ['-top cell_config${SVCONFIG}'],
)
Alias('sim_cell', sim_cell)
Alias('cell', sim_cell)

##################
### Simulate Inst
sim_inst = xrunEnv.AllIn1(
    'simulate_inst_cadence.log',
    ['libmap_rtl.sv', 'configs.sv', 'source_code_cadence.f'],
    XRUN_ALL_ARGS=xrunEnv['XRUN_ALL_ARGS'] + ['-top inst_config${SVCONFIG}'],
)
Alias('sim_inst', sim_inst)
Alias('inst', sim_inst)

#######################
### Additional cleanup
Clean([sim_rtl, sim_cell, sim_inst], Glob('*~'))