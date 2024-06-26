EnsureSConsVersion(3, 0)  # for Help() append

import os

Help('''
=============================================================================
SConstruct for Synopsys configurations:

Targets:
- compile
- compile_rtl
- sim_rtl / rtl
- sim_cell / cell
- sim_inst / inst

The simulation targets will automatically call the compile
targets as needed due to their dependencies.

Examples:
scons -f SConstruct.synopsys.py (runs every option by default)
scons -f SConstruct.synopsys.py compile
scons -f SConstruct.synopsys.py sim_cell --svconfig=1

To clean:
scons -f SConstruct.synopsys.py -c

Notable SCons concepts:
- We set VLOGAN_ARGS and VCS_ARGS in our vcsEnv object, overriding the tool's default
- We tweaked the tool so that if it finds 'libmap' in the .sv filename,
  it will append it with the '-libmap' flag
- We removed the -work parts of the commands from the tool builders
- We added to 'Clean' so SCons can remove the extra libraries generated
- We append a custom, per-target additional argument to VCS_ARGS in
  each of the vcsEnv.Sim() calls. Anything passed in after the target and
  source lists overwrites the defaults in the tool and the vcsEnv object
- We dynamically select a dependency for the 'sim_rtl' target based on
  the value passed in with the --svconfig option
=============================================================================
''', append=True)  # Only works on newer install of SCons
# reference site_tools/site_init.py for help on --<options> if using
# older version of SCons

##############
### Env Setup
vcsEnv = Environment(
    ENV={
        'PATH': os.environ['PATH'],
        'HOME': os.environ['HOME'],
    },
    TOOLS=['vcs'],
    SCANNERS=[svscan, fscan] + scanners,
    WORK='work',
    SVCONFIG=GetOption('svconfig'),
    VLOGAN_ARGS=['-full64', '-diag libconfig', '-sverilog'],
    VCS_ARGS=['-full64', '-diag libconfig', '-debug_access', '-ucli -i run_vcs.do'],
)

############
### Compile
com = vcsEnv.Com('compile_synopsys.log', ['libmap.sv', 'source_code.f'])
Alias('compile', com)
Clean(com, ['rtlLib', 'gateLib'])

#####################
### Compile RTL Only
com_rtl = vcsEnv.Com('compile_rtl_synopsys.log', ['libmap_rtl.sv', 'source_code.f'])
Alias('compile_rtl', com_rtl)
Clean(com_rtl, [Glob('*Lib')])

#################
### Simulate RTL
sim_rtl = vcsEnv.Sim(
    'simulate_rtl_synopsys.log',
    [com_rtl if vcsEnv['SVCONFIG'] != '' else com],
    VCS_ARGS=vcsEnv['VCS_ARGS'] + ['rtl_config${SVCONFIG}']
)
Alias('sim_rtl', sim_rtl)
Alias('rtl', sim_rtl)

##################
### Simulate Cell
sim_cell = vcsEnv.Sim(
    'simulate_cell_synopsys.log',
    [com_rtl],
    VCS_ARGS=vcsEnv['VCS_ARGS'] + ['cell_config${SVCONFIG}']
)
Alias('sim_cell', sim_cell)
Alias('cell', sim_cell)

##################
### Simulate Inst
sim_inst = vcsEnv.Sim(
    'simulate_inst_synopsys.log',
    [com_rtl],
    VCS_ARGS=vcsEnv['VCS_ARGS'] + ['cell_config${SVCONFIG}']
)
Alias('sim_inst', sim_inst)
Alias('inst', sim_inst)

#######################
### Additional cleanup
Clean([sim_rtl, sim_cell, sim_inst], ['ucli.key'])
Clean([com, com_rtl, sim_rtl, sim_cell, sim_inst], [Glob('*~')])