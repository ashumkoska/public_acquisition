from odoo import api, models, fields, _


class CommissionMember(models.Model):
    
    _name = 'commission.member'
    _description = 'Commission Member'
    _rec_name = 'user_id'
    
    user_id = fields.Many2one('res.users', string='User', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', realted='user_id.partner_id')
    signature = fields.Binary(string='Signature', attachment=True)
    date = fields.Date(string='Date of Signing', readonly=True)
    activity_id = fields.Many2one('mail.activity', string='Related Activity', readonly=True)
    signed = fields.Boolean(string='Signed', compute='compute_signed', store=True)
    acq_plan_id = fields.Many2one('acquisition.plan', string='Acquisition Plan', ondelete='cascade')
    
    @api.multi
    @api.depends('signature')
    def compute_signed(self):
        for rec in self:
            signed = False
            if rec.signature:
                signed = True
            rec.signed = signed
            
    @api.multi
    def sign_acquisition_plan(self):
        return {
            'name': _('Sign Acquisition Plan'),
            'type': 'ir.actions.act_window',
            'res_model': 'sign.acquisition.plan',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': False,
            'context': {
                'default_member_id': self.id,
                'default_acq_plan_id': self.acq_plan_id.id,
            },
            'target': 'new'
        }
