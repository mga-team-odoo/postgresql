# -*- coding: utf-8 -*-
##############################################################################
#
#    postgresql module for OpenERP, PostgreSQL Management
#    Copyright (C) 2014 MIROUNGA (<http://www.mirounga.fr/>)
#              Christophe CHAUVET <christophe.chauvet@gmail.com>
#
#    This file is a part of postgresql
#
#    postgresql is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    postgresql is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.osv import fields
from openerp.tools.sql import drop_view_if_exists

import logging
logger = logging.getLogger(__name__)

class PgLocks(orm.Model):
    _name = 'postgres.lock'
    _description = 'Check locks on the database'
    _auto = False

    _columns = {
        'blocked_pid': fields.integer('Blocked PID', readonly=True, help='Blocked PID'),
        'blocked_user': fields.char('Blocked user', size=64, readonly=True, help='database user blocked'),
        'blocking_statement': fields.text('Blocking statement', readonly=True, help='Blocking statement query'),
        'blocking_duration': fields.char('Blocking duration', size=16, readonly=True, help='See the time elapsed since the query is blocked'),
        'blocking_pid': fields.integer('Blocking PID', readonly=True, help='Blocking PID'),
        'blocking_user': fields.char('Blocking user', size=64, readonly=True, help='database user blocking'),
        'blocked_statement': fields.text('Blocked statement', readonly=True, help='Blocked statement query'),
        'blocked_duration': fields.char('Blocked duration', size=16, readonly=True, help='See the time elapsed since the query is blocked'),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'postgres_lock')
        logger.info('Create postgres_lock report view')

        if cr._cnx.server_version >= 90200:
            cr.execute("""CREATE OR REPLACE VIEW postgres_lock AS
                           SELECT bl.pid                 AS id,
                                  bl.pid                 AS blocked_pid,
                                  a.usename              AS blocked_user,
                                  ka.query               AS blocking_statement,
                                  to_char(now() - ka.query_start, 'HH24:MI:SS')::varchar AS blocking_duration,
                                  kl.pid                 AS blocking_pid,
                                  ka.usename             AS blocking_user,
                                  a.query                AS blocked_statement,
                                  to_char(now() - a.query_start, 'HH24:MI:SS')::varchar  AS blocked_duration
                           FROM  pg_catalog.pg_locks         bl
                            JOIN pg_catalog.pg_stat_activity a  ON a.pid = bl.pid
                            LEFT JOIN pg_catalog.pg_locks         kl ON kl.transactionid = bl.transactionid AND kl.pid != bl.pid
                            LEFT JOIN pg_catalog.pg_stat_activity ka ON ka.pid = kl.pid
                           WHERE NOT bl.granted;""")
        else:
            cr.execute("""
                          CREATE OR REPLACE VIEW postgres_lock AS
                          SELECT bl.pid                 AS id,
                                 bl.pid                 AS blocked_pid,
                                 a.usename              AS blocked_user,
                                 ka.current_query       AS blocking_statement,
                                 to_char(now() - ka.query_start, 'HH24:MI:SS')::varchar AS blocking_duration,
                                 kl.pid                 AS blocking_pid,
                                 ka.usename             AS blocking_user,
                                 a.current_query        AS blocked_statement,
                                 to_char(now() - a.query_start, 'HH24:MI:SS')::varchar  AS blocked_duration
                            FROM pg_catalog.pg_locks         bl
                            JOIN pg_catalog.pg_stat_activity a  ON a.procpid = bl.pid
                            LEFT JOIN pg_catalog.pg_locks         kl ON kl.transactionid = bl.transactionid AND kl.pid != bl.pid
                            LEFT JOIN pg_catalog.pg_stat_activity ka ON ka.procpid = kl.pid
                           WHERE NOT bl.granted;""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
