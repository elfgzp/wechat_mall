# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    display_pic = fields.Html('图片', compute='_compute_display_pic')

    def _compute_display_pic(self):
        for each_record in self:
            if each_record.pic:
                each_record.display_pic = """
                    <img src="{pic}" style="max-width:100px;">
                    """.format(pic=each_record.static_link())
            else:
                each_record.display_pic = False

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = domain if domain else []
        if not self.env.user._is_superuser():
            domain += [('create_uid', '=', self.env.uid)]
        return super(IrAttachment, self).search_read(domain=domain, fields=fields, offset=offset,
                                                     limit=limit, order=order)

    @api.model
    def search_count(self, args):
        if not self.env.user._is_superuser():
            args += [('create_uid', '=', self.env.uid)]
        return super(IrAttachment, self).search_count(args)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args if args else []
        if not self.env.user._is_superuser():
            args += [('create_uid', '=', self.env.uid)]
        return super(IrAttachment, self).name_search(name=name, args=args, operator=operator, limit=limit)

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
