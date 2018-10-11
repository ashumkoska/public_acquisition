from odoo import api, models, fields, _


class AcquisitionOffer(models.Model):
    
    _name = 'acquisition.offer'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Acquisition Offer'
    
    acq_plan_id = fields.Many2one('acquisition.plan', string='Acquisition Plan', track_visibility='always')
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='on_change')
    submission_date = fields.Date(string='Date of Submission', track_visibility='on_change')
    description = fields.Html(string='Description')
    state = fields.Selection([('new', 'New'), 
                              ('submit', 'Submitted'), 
                              ('approve', 'Approved'), 
                              ('decline', 'Declined')], string='Status', default='new')
    
    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = '%s - %s' % (rec.acq_plan_id.name, rec.partner_id.name)
            res.append((rec.id, name))
        return res
    
    @api.multi
    def submit(self):
        for rec in self:
            rec.write({'state': 'submit'})
            
    @api.multi
    def approve(self):
        for rec in self:
            rec.write({'state': 'approve'})
            
    @api.multi
    def decline(self):
        for rec in self:
            rec.write({'state': 'decline'})
