# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def default_get(self, fields_list):
        default_fields = super(IrAttachment, self).default_get(fields_list)
        default_fields['public'] = True
        return default_fields

    def static_link(self):
        self.ensure_one()
        return '{base_url}/web/content?' \
               'model=ir.attachment&' \
               'field=datas&' \
               'id={attachment_id}&' \
               'download=true&' \
               'filename_field=datas_fname'.format(
            base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            attachment_id=self.id
        ).replace('\n', '').replace(' ', '')

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        return super(IrAttachment, self).check_access_rights(operation=operation, raise_exception=raise_exception)
