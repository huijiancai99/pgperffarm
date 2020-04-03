import os

from utils.logging import log
from utils.misc import run_cmd
from rrdtool import fetch

COLLECTD_CONFIG = '/tmp/.collectd.conf'
COLLECTD_PIDFILE = '/tmp/.collectd.pid'
RESULT_FOLDER = '/var/lib/collectd/rrd/ubuntu/cpu-0/'
RESULT_CONTENT = [
            'idle',
            'interrupt',
            'nice',
            'softirq',
            'steal',
            'system',
            'user',
            'wait'
            ]



class CollectdCollector(object):
    """
    Collect basic system and database statistics using collectd.
    """

    def __init__(self, outdir, dbname, bin_path):
        self._bin_path = bin_path

        # Hard code all possible places a packager might install collectd.
        self._env = os.environ
        self._env['PATH'] = ':'.join(['/usr/sbin/', '/sbin/', self._env['PATH']])

        # Assume collectd.conf.in file to be in the same directory as this
        # file.
        cwd = os.path.dirname(os.path.realpath(__file__))

        modules = (
            'LoadPlugin aggregation\n'
            'LoadPlugin contextswitch\n'
            'LoadPlugin cpu\n'
            'LoadPlugin csv\n'
            'LoadPlugin disk\n'
            'LoadPlugin interface\n'
            'LoadPlugin memory\n'
            'LoadPlugin postgresql\n'
            'LoadPlugin processes\n'
            'LoadPlugin swap\n'
        )

        system = os.popen("uname").readlines()[0].split()[0]

        if system == 'Linux':
            modules += (
                'LoadPlugin ipc\n'
                'LoadPlugin vmem\n'
            )

        outdir = '%s/stats' % outdir
        config_template = open('%s/collectd.conf.in' % cwd, 'r')
        config = open(COLLECTD_CONFIG, 'w')
        config.write(config_template.read() % {'database': dbname,
                                               'datadir': outdir,
                                               'modules': modules,
                                               'pguser': self._env['USER']})
        config.close()
        config_template.close()

        # TODO: Use collectd to test config act exit appropriately.

    def start(self):
        log("starting collectd")
        cmd = 'collectd -C %s -P %s' % (COLLECTD_CONFIG, COLLECTD_PIDFILE)
        r = run_cmd(cmd.split(' '), env=self._env)
        return r[1]

    def stop(self):
        log("stopping collectd")
        try:
            pidfile = open(COLLECTD_PIDFILE, 'r')
            pid = pidfile.read().strip()
            run_cmd(['kill', pid])
        except FileNotFoundError:
            log('collectd pid not found - processes may still be running')

    def result(self):
        result_keyset = ['cpu_' + x for x in RESULT_CONTENT]
        r = dict.fromkeys(result_keyset, 'nan')
        for content in RESULT_CONTENT:
            filename = RESULT_FOLDER + 'cpu-' + content + '.rrd'
            temp = fetch(filename, 'AVERAGE')
            valid = [x[0] for x in temp[2] if x[0] != None]
            r['cpu_' + content] = sum(valid) / len(valid)
        return r


def run_collector(in_queue, out_queue, dbname, bin_path, outdir, interval=1.0):
    pass
