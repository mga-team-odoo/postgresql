# -*- coding: utf-8 -*-
##############################################################################
#
#    postgresql module for OpenERP, PostgreSQL Management
#    Copyright (C) 2013 MIROUNGA (<http://www.mirounga.fr/>)
#              Christophe CHAUVET <christophe.chauvet@mirounga.fr>
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
logger = logging.getLogger('postgresql')


class PgActivity(orm.Model):
    _name = 'postgres.activity'
    _description = 'Display activity for this database'
    _auto = False
    _order = 'start_query desc'

    _columns = {
        'name': fields.char('DB Name', size=64, readonly=True, help='Name of the database'),
        'pid': fields.integer('PID', readonly=True, help='PID of the process'),
        'dbuser': fields.char('DB User', size=64, readonly=True, help='Name of the database user connected'),
        'appname': fields.char('Application Name', size=64, readonly=True, help='Name of the application'),
        'hostip': fields.char('IP Address', size=64, readonly=True, help='IP connect to this database'),
        'hostname': fields.char('Hostname', size=64, readonly=True, help='Hostname connect to this database'),
        'start_backend': fields.datetime('Backend Start', readonly=True, help='Timestamp when backend start'),
        'start_transaction': fields.datetime('Transaction Start', readonly=True, help='Timestamp when transation start'),
        'start_query': fields.datetime('Query Start', readonly=True, help='Timestamp when the current query was started'),
        'query': fields.text('Current query', readonly=True, help='Current query execute'),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'postgres_activity')
        logger.info('Create postgresq_activity view for %s' % cr._cnx.server_version)
        pid_field = cr._cnx.server_version >= 90200 and 'pid' or 'procpid'
        cr.execute("""CREATE OR REPLACE VIEW postgres_activity AS
                      SELECT """ + pid_field + """ AS id,
                             datname AS "name",
                             """ + pid_field + """ AS pid,
                             usename as dbuser,
                             application_name as appname,
                             host(client_addr) as hostip,
                             client_hostname as hostname,
                             TO_CHAR(backend_start, 'YYYY-MM-DD HH24:MI:SS') as start_backend,
                             TO_CHAR(xact_start, 'YYYY-MM-DD HH24:MI:SS') as start_transaction,
                             TO_CHAR(query_start, 'YYYY-MM-DD HH24:MI:SS') as start_query,
                             current_query as query
                        FROM pg_stat_activity
                       WHERE procpid != pg_backend_pid()
                         AND datname = current_database()""")

    def disconnect(self, cr, uid, ids, context=None):
        """
        Execute pg_terminate_backend(), to disconnect properly the client
        ids containt directly the list of sessions to disconnect
        """
        cr.execute('SET ROLE TO oerpadmin')
        for id in ids:
            cr.execute("""SELECT pg_terminate_backend(%s)""", (id,))
        cr.execute("""RESET ROLE""")
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
