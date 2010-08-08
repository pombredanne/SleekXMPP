"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

from __future__ import with_statement
from .. thirdparty import statemachine
#TODO look for this installed separately before using local version
import types


class StateError(Exception):
    """Raised whenever a state transition was attempted but failed."""

class StateManager(object):
    """This wraps the 3rd party statemachine to do multi-state checking and simplify state access"""
    def __init__(self):
        self._machines = {}
        self._callbacks = {}
       
    def __getitem__(self, key):
        """Get the current state"""
        return self._machines[key].current_state()

    def setState(self, name, from_state, state, condition={}, use_func=True):
        """Set the state from specific states to a new state, optionally based on the condition of other states
        condition= {machine: (values,)}"""
        if type(from_state) != types.TupleType:
            from_state = (from_state,)
        if condition:
            for machine in condition:
                condition_states = condition[machine]
                if type(condition_states) != types.TupleType:
                    condition_states = (condition_states,)
                if not self._machines[machine].ensure(condition_states):
                    return False
        if use_func:
            callback = self._callbacks.get(name, {}).get((self._machines[name].current_state(), state))
        else:
            callback = None
        return self._machines[name].transition_any(from_state, state, func=callback)

    def add_machine(self, name, states):
        if name in self._machines:
            raise ValueError
        self._machines[name] = statemachine.StateMachine(states)
        self._callbacks[name] = {}

    def add_function(self, name, startstate, endstate, func):
        self._callbacks[name][(startstate, endstate)] = func

    def del_machine(self, name):
        pass

    def reset(self):
        for machine in self._machines:
            self._machines[machine].reset()
