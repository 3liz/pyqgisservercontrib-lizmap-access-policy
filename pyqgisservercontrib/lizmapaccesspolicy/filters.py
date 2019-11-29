""" Handle lizmap WPS access policy 

autoreload: yes

# Define access policies
policies:
    # Global policy
    - deny: all

    # Policy for groups admin and operator
    - allow:  'scripts:*'
      groups: 
        - admin
        - operator

    # Policy for group operator will apply  only for map 'france_parts' with
    # testsimplevalue processes
    - allow: 'pyqgiswps_test:testsimplevalue'
      groups: 
        - operator
      maps:  
        - 'france_parts'

# Include other policies
include_policies:
    - lizmap_policies/*/wpspolicy.yml

"""
import os
import sys
import logging
import yaml
import traceback
import functools

from itertools import chain

from tornado.web import HTTPError, RequestHandler
from yaml.nodes import SequenceNode
from typing import Mapping, TypeVar, Any
from pathlib import Path
from collections import namedtuple

from .watchfiles import watchfiles

LOGGER = logging.getLogger('SRVLOG')

# Define an abstract types
YAMLData = TypeVar('YAMLData')


class LizmapPolicyError(Exception):
    pass

PolicyRule = namedtuple("PolicyRule", ('allow','deny','groups','users','maps'))

def _to_list( arg ):
    """ Convert an argument to list
    """
    if isinstance(arg,list):
        return arg
    elif isinstance(arg,str):
        return arg.split(',')
    else:
        raise LizmapPolicyError("Expecting 'list' not %s" % type(s))


def new_PolicyRule( allow=None, deny=None, groups=[], users=[], maps=[] ):
    """ Construct a PolicyRule object
    """
    return PolicyRule( allow  = allow,
                      deny   = deny,
                      groups = _to_list(groups),
                      users  = _to_list(users),
                      maps   = _to_list(maps))

# Define the 'all' group
GROUP_ALL='g__all'

class PolicyManager:
    
    @classmethod
    def initialize( cls, configfile: str, exit_on_error: bool=True ) -> 'ACLManager':
        """ Create ACL manager
        """
        try:
            return PolicyManager(configfile)
        except Exception:
            LOGGER.error("Failed to load lizmap policy %s: %s")
            if exit_on_error:
                traceback.print_exc()
                sys.exit(1)
            else:
                raise

    def __init__(self, configfile: str ) -> None:
        self._autoreload = None
        self.load(configfile)

    def parse_policy( self, rootd: Path, config: YAMLData ) -> None:
        """
        """
        # Load rule from main config policies
        policies = [new_PolicyRule(**kw) for kw in config.get('policies',[])]

        # Load included policies
        for incl in config.get('include_policies',[]):
            for path in rootd.glob(incl):
                LOGGER.info("Policy: Opening policy rules: %s", path.as_posix())
                with path.open('r') as f:
                    acs = yaml.safe_load(f)
                # Add policies
                policies.extend( new_PolicyRule(**kw) for kw in acs )

        rules = { GROUP_ALL: [] }

        ### Create users/groups rule chain
        for ac in policies:
            if not ac.users and not ac.groups:
               rules[GROUP_ALL].append(ac)
               continue
            # Add user chain
            for k in chain( ('u__'+user for user in ac.users), ('g__'+group for group in ac.groups) ):
                r = rules.get(k,[])
                r.append(ac)
                rules[k] = r
 
        # Set policy rules
        self._rules = rules
        LOGGER.debug("# Lizmap Policy RULES %s", rules)

    def load( self, configfile: str) -> None:
        """ Load policy configuration
        """
        LOGGER.info("Policy: Reading Lizmap Policy configuration %s", configfile)
        with open(configfile,'r') as f:
            config = yaml.safe_load(f)
        
        self.parse_policy(Path(configfile).parent, config)

        # Configure auto reload
        if config.get('autoreload', False):
            if self._autoreload is None:
                check_time = config.get('autoreload_check_time', 3000)
                self._autoreload = watchfiles([configfile], 
                        lambda modified_files: self.load(configfile), 
                        check_time=check_time)
            if not self._autoreload.is_running():
                LOGGER.info("Policy: Enabling Lizmap Policy autoreload")
                self._autoreload.start()
        elif self._autoreload is not None and self._autoreload.is_running():
            LOGGER.info("Policy: Disabling Lizmap Policy autoreload")
            self._autoreload.stop()            

    def add_policy_for(self, name:str, handler: RequestHandler, request: 'HTTPRequest' ) -> None:
        """ Add policy for the given name
        """
        rules = self._rules.get(name)
        if not rules:
            return
        for rule in rules:
            maps = rule.maps
            # Rule apply only for map
            if maps:
                test = request.arguments.get('MAP')
                # No map defined forget that rule
                if not test: 
                    continue
                test = test[-1]
                if isinstance(test,bytes):
                    test = test.decode()
                test = Path(test)
                # Test rule against map
                if not any( test.match(m) for m in maps ):
                    continue
            # Add policy
            handler.accesspolicy.add_policy(deny=rule.deny,allow=rule.allow)

    def add_policy( self, handler: RequestHandler ) -> None:
        """ Check profile condition
        """
        request = handler.request
        user    = request.headers.get('X-Lizmap-User')
        groups  = request.headers.get('X-Lizmap-User-Groups')
        if user:   self.add_policy_for( 'u__'+user, handler, request )
        if groups:
            for group in groups.split(','):
                self.add_policy_for( 'g__'+group.strip(), handler, request )
        # Add global rules
        self.add_policy_for( GROUP_ALL, handler, request )

        LOGGER.debug("# Lizmap policy USER: %s", user)
        LOGGER.debug("# Lizmap policy GROUPS: %s", groups)
        LOGGER.debug("# Lizmap policy ALLOW %s", handler.accesspolicy._allow)
        LOGGER.debug("# Lizmap policy DENY  %s", handler.accesspolicy._deny)


def register_wpsfilters() -> None:
    """ Register filters for WPS
    """
    from pyqgiswps.filters import blockingfilter
    from pyqgiswps.config import get_env_config

    with_policy= get_env_config('lizmap','policy','QGSRV_LIZMAP_POLICY')
    if with_policy:
        mngr = PolicyManager.initialize(with_policy)
       
        @blockingfilter()
        def _filter( handler: RequestHandler ) -> None:
            mngr.add_policy( handler )

        return [_filter]
    
    return []


