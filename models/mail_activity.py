from odoo import api, models, fields, _


class MailActivity(models.Model):
    
    _inherit = 'mail.activity'
    
    signature = fields.Binary(string='Digital Signature')