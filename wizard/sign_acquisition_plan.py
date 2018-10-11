from datetime import date
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class SignAcquisitionPlan(models.TransientModel):
    
    _name = 'sign.acquisition.plan'
    _description = 'Sign Acquisition Plan'
    
    member_id = fields.Many2one('commission.member', string='Commission Member', readonly=True)
    acq_plan_id = fields.Many2one('acquisition.plan', string='Acquisition Plan', readonly=True)
    signature = fields.Binary(string='Signature')
    
    @api.one
    def sign_acquisition_plan(self):
        # TODO: uncomment after testing
        #if not self.signature or (self.signature and self.env.uid != self.member_id.user_id.id):
        #    raise UserError(_('The user %s should sign this document!' % (self.member_id.user_id.name)))
        
        self.member_id.write({
            'signature': self.signature,
            'date': date.today(),
            'signed': True
        })
        self.member_id.activity_id.action_done()
        
        if all([member.signed for member in self.acq_plan_id.com_member_ids]):
            self.acq_plan_id.write({
                'state': 'approve'
            })
            