# -*- coding: utf-8 -*-
##############################################################################
#
# postgresql module for OpenERP, PostgreSQL Management
# Copyright (C) 2013-2016 MIROUNGA (<http://www.mirounga.fr/>)
#           Christophe CHAUVET <christophe.chauvet@gmail.com>
#
# This file is a part of postgresql
#
# postgresql is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# postgresql is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields

# from openerp.osv import orm
# from openerp.osv import fields
from openerp.tools.sql import drop_view_if_exists

import logging
logger = logging.getLogger(__name__)


class PgActivity(models.Model):
    _name = 'postgres.activity'
    _description = 'Display activity for this database'
    _auto = False
    _order = 'start_query desc'

    name = fields.Char(
        'DB Name', size=64, readonly=True, help='Name of the database')
    pid = fields.Integer(
        'PID', readonly=True, help='PID of the process')
    dbuser = fields.Char(
        'DB User', size=64, readonly=True,
        help='Name of the database user connected')
    appname = fields.Char(
        'Application Name', size=64, readonly=True,
        help='Name of the application')
    hostip = fields.Char(
        'IP Address', size=64, readonly=True,
        help='IP connect to this database')
    hostname = fields.Char(
        'Hostname', size=64, readonly=True,
        help='Hostname connect to this database')
    start_backend = fields.Datetime(
        'Backend Start', readonly=True,
        help='Timestamp when backend start')
    start_transaction = fields.Datetime(
        'Transaction Start', readonly=True,
        help='Timestamp when transation start')
    start_query = fields.Datetime(
        'Query Start', readonly=True,
        help='Timestamp when the current query was started')
    query = fields.Text(
        'Current query', readonly=True,
        help='Current query execute')

    def init(self, cr):
        logger.info('PostgreSQL Server Version %s' % cr._cnx.server_version)
        drop_view_if_exists(cr, 'postgres_activity')
        logger.info('Create postgres_activity report view')
        s_ver = cr._cnx.server_version
        pid_field = s_ver >= 90200 and 'pid' or 'procpid'
        query_field = s_ver >= 90200 and 'query' or 'current_query'
        cr.execute("""
 CREATE OR REPLACE VIEW postgres_activity AS
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
        """ + query_field + """ as query
   FROM pg_stat_activity
  WHERE """ + pid_field + """ != pg_backend_pid()
    AND datname = current_database()""")

    @api.multi
    def disconnect(self):
        """
        Execute pg_terminate_backend(), to disconnect properly the client
        ids containt directly the list of sessions to disconnect
        """
        self.ensure_one()
        self.env.cr.execute('SET ROLE TO oerpadmin')
        self.env.cr.execute("""SELECT pg_terminate_backend(%s)""", (self.id,))
        self.env.cr.execute("""RESET ROLE""")
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
