
def assert_debug(app):
    assert(app.debug == False)

"""
def set_trace(app):
    if app.debug:
        import pdb, sys

        # first method
        for attr in ('stdin', 'stdout', 'stderr'):
            setattr(sys, attr, getattr(sys, '__%s__' % attr))
        debugger = pdb.Pdb(stdin=sys.__stdin__,stdout=sys.__stdout__)
        debugger.set_trace(sys._getframe().f_back)

        # second method
        #for attr in ('stdin', 'stdout', 'stderr'):
        #    setattr(sys, attr, getattr(sys, '__%s__' % attr))
        #pdb.set_trace(sys._getframe().f_back)

"""

def set_trace():
    import pdb, sys

    # first method
    #for attr in ('stdin', 'stdout', 'stderr'):
    #    setattr(sys, attr, getattr(sys, '__%s__' % attr))
    #debugger = pdb.Pdb(stdin=sys.__stdin__,stdout=sys.__stdout__)
    #debugger.set_trace(sys._getframe().f_back)

    # second method
    #for attr in ('stdin', 'stdout', 'stderr'):
    #    setattr(sys, attr, getattr(sys, '__%s__' % attr))
    #pdb.set_trace(sys._getframe().f_back)

    # third method
    #setattr(sys, 'stdin', getattr(sys, '__stdin__' ))
    #setattr(sys, 'stdout', getattr(sys, '__stdout__' ))
    #setattr(sys, 'stderr', getattr(sys, '__stderr__' ))
    #logfile=open('/Users/kusno/pdb.log', 'w')

    # fourth method
    #pdb.Pdb(
    #        stdin=getattr(sys,'__stdin__'),
    #        stdout=getattr(sys,'__stdout__'),
    #        ).set_trace(sys._getframe().f_back)

    for attr in ('stdin', 'stdout', 'stderr'):
        setattr(sys, attr, getattr(sys, '__%s__' % attr))
    debugger = pdb.Pdb(stdin=sys.__stdin__,stdout=sys.__stdout__)
    debugger.set_trace(sys._getframe().f_back)



