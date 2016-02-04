#!/usr/bin/env python

import rospy

from multimaster_msgs_fkie.msg import MasterState

def master_changed(msg, cb_args):
    master_proxies, param_cache = cb_args
    master_proxies[msg.master.name] = rospy.MasterProxy(msg.master.uri)

    for name_from, master_from in master_proxies.items():
        for name_to, master_to in master_proxies.items():
            if name_to != name_from:
                rospy.logdebug("Getting params from...".format(name_from))
                params_from = master_from['/']
                rospy.logdebug("Got {} params.".format(len(params_from)))
                if '_' in params_from:
                    del params_from['_']
                if '/_' in params_from:
                    del params_from['/_']
                rospy.logdebug("Syncing params from {} to {}...".format(name_from, name_to))
                if param_cache.get(name_from, None) != params_from:
                    param_cache[name_from] = params_from
                    master_to['/_/'+name_from] = params_from
                    rospy.logdebug("Done syncing params from {} to {}.".format(name_from, name_to))
                else:
                    rospy.logdebug("Params have not changed from {} to {}.".format(name_from, name_to))


def main():
    rospy.init_node('param_sync')

    master_proxies = dict()
    param_cache = dict()

    sub = rospy.Subscriber('changes', MasterState, master_changed, callback_args=(master_proxies, param_cache))

    rospy.spin()

if __name__ == '__main__':
    main()

