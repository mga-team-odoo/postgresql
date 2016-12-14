# -*- coding: utf-8 -*-
##############################################################################
#
#    postgresql module for OpenERP, PostgreSQL Management
#    Copyright (C) 2013-2016 MIROUNGA (<http://www.mirounga.fr/>)
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

{
    'name': 'Postgresql',
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'description': """PostgreSQL Management

This module can show statistics on the database, and create new user with GRANT SELECT

!!! Before install this module, execute this query as a PostgreSQL SuperUSER

CREATE ROLE oerpadmin SUPERUSER;
GRANT oerpadmin TO openerp;
""",
    'author': 'MIROUNGA',
    'website': 'http://www.mirounga.fr/',
    'depends': ['base'],
    'images': [],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/activity_view.xml',
        'views/lock_view.xml',
        #'wizard/wizard.xml',
        #'report/report.xml',
    ],
    'demo': [],
    'test': [],
    #'external_dependancies': {'python': ['kombu'], 'bin': ['which']},
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
