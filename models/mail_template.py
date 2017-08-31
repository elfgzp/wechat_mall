# -*- coding: utf-8 -*-

import datetime

import logging
from odoo import models, fields, api, exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class SpeMailTemplate(models.Model):
    _inherit = "mail.template"

    @api.multi
    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, background=True):
        email_values = email_values or {}
        if background:
            email_values['mail_template_id'] = self.id
            context = dict(self._context or {})
            email_values['context'] = context
            self.env['ir.cron'].sudo().create({
                'name': self.name,
                'user_id': self.env.uid,
                'model': self._name,
                'function': '_send_mail',
                'active': True,
                'priority': 0,
                'numbercall': 1,
                'nextcall': (datetime.datetime.utcnow() + datetime.timedelta(seconds=3)).strftime(DATETIME_FORMAT),
                'interval_type': 'minutes',
                'args': repr([res_id, force_send, raise_exception, email_values])
            })
        else:
            return super(SpeMailTemplate, self).send_mail(res_id, force_send, raise_exception, email_values)

    @api.multi
    def _send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
        mail_template_id = email_values.pop('mail_template_id')
        context = email_values.pop('context')
        mail_template = self.with_context(context).sudo().env['mail.template'].browse(mail_template_id)
        logging.info(u">>> mail to {} is sending".format(context.get("email_to") or ""))
        try:
            return super(SpeMailTemplate, mail_template).send_mail(res_id, force_send, raise_exception, email_values)
        except MailDeliveryException as e:
            logging.error(e)
        except Exception as e:
            logging.error(e)
